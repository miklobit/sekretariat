# -*- coding: utf-8 -*-
import logging

import dateparser
from django.conf import settings
from django.db import models
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.timezone import get_current_timezone_name
from django.utils.translation import ugettext_lazy as _
from django_powerbank.db.models.base import BaseModel
from django_powerbank.db.models.fields import SecretField

from website.misc.mail import send_mail_template

log = logging.getLogger(__name__)


def text_to_time(text):
    assert text
    assert text.strip()
    tz = get_current_timezone_name()
    try:
        # return maya.when(text, timezone=tz).datetime(tz)
        settings = {
            'TIMEZONE': tz,
            'RETURN_AS_TIMEZONE_AWARE': True,
            'TO_TIMEZONE': tz,
            'PREFER_DATES_FROM': 'current_period',
        }
        log.debug("text: %s", text)
        return dateparser.parse(
            text,
            settings=settings,
            languages=['pl'],
            locales=['pl'],
            date_formats=[
                '%Y-%m-%d\t%H:%M',
                '%Y-%m-%d\t%H:%M:%S',
                '%d.%m.%Y\t%H:%M',
                '%-d.%m.%Y\t%H:%M',
            ],
        )
    except ValueError as ex:
        raise ValueError(text) from ex


def text_to_times(text):
    def parser(lines):
        last_item = None
        for line in lines.splitlines():
            log.debug("line: %s", line)
            if not line or not line.strip():
                continue
            line = line.replace(",", ":")
            if line.startswith("\t"):
                line = last_item.strftime("%Y-%m-%d") + line
            last_item = text_to_time(line)
            log.debug("last_item: %s", last_item)
            yield last_item

    return sorted(set(parser(text)))


class OpenOfficeGroup(BaseModel):
    name = models.CharField(max_length=250, verbose_name=_('title'))

    class Meta:
        verbose_name = _('open office group')
        verbose_name_plural = _('open office groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return resolve_url("sekretariat:OpenOfficeGroupDetail", self.pk)

    def update_slots(self, text):
        existing = OpenOfficeSlot.objects.filter(group=self).values_list('start', flat=True)
        items = [OpenOfficeSlot(start=start, group=self) for start in text_to_times(text) if start not in existing]
        OpenOfficeSlot.objects.bulk_create(items)


class OpenOfficeSlot(BaseModel):
    group = models.ForeignKey(OpenOfficeGroup, on_delete=models.CASCADE)
    start = models.DateTimeField(verbose_name=_('event start'))
    student = models.CharField(max_length=250, verbose_name=_('student name'), null=True, blank=True)
    email = models.EmailField(max_length=250, verbose_name=_('email'), null=True, blank=True, unique=True)
    confirmation_secret = SecretField(max_length=200, source_field='email', null=True, blank=True)
    confirmed = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('open office slot')
        verbose_name_plural = _('open office slot')
        ordering = 'start', 'group',
        unique_together = 'group', 'start'
        default_related_name = 'slots'

    def __str__(self):
        return "{:%Y-%m-%d %H:%M} {}".format(self.start, self.group)

    def get_absolute_url(self):
        return resolve_url("sekretariat:OpenOfficeGroupDetail", self.group_id)

    def confirm(self):
        self.confirmed = timezone.now()
        self.save()
        self.send_confirmed()

    def cancel(self):
        self.send_cancelled()
        self.confirmed = None
        self.student = None
        self.email = None
        self.save()

    def send_confirmation_prompt(self):
        subject = _("{start:%Y-%m-%d %H:%M} Prośba o potwierdzenie terminu")
        template = "OpenOfficeSlot/email/prompt.html"
        self._send_message(subject, template)

    def send_confirmed(self):
        subject = _("{start:%Y-%m-%d %H:%M} Prośba o potwierdzenie terminu")
        template = "OpenOfficeSlot/email/confirmed.html"
        self._send_message(subject, template)

    def send_cancelled(self):
        subject = _("{start:%Y-%m-%d %H:%M} Termin anulowany")
        template = "OpenOfficeSlot/email/cancelled.html"
        self._send_message(subject, template)

    def _send_message(self, subject=None, template=None):
        assert self.confirmation_secret, "Secret is missing for email '{}'".format(self.confirmation_email)
        self.save()
        confirm_url = resolve_url("sekretariat:OpenOfficeSlotBookConfirm", pk=self.pk, secret=self.confirmation_secret)
        confirm_url = '{base_url}{url}'.format(base_url=settings.BASE_URL, url=confirm_url)
        cancel_url = resolve_url("sekretariat:OpenOfficeSlotBookCancel", pk=self.pk, secret=self.confirmation_secret)
        cancel_url = '{base_url}{url}'.format(base_url=settings.BASE_URL, url=cancel_url)
        ctx = {
            'person': self.student,
            'start': self.start,
            'email': self.email,
            'confirm_url': confirm_url,
            'cancel_url': cancel_url,
            'count': OpenOfficeSlot.objects.filter(email=self.email).count() - 1,
        }
        subject = subject.format(**ctx)
        send_mail_template(template, ctx, subject, to=self.email)
