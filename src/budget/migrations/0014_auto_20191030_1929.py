# Generated by Django 2.2.6 on 2019-10-30 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0013_application_awaiting'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ('-submitted', 'date'), 'permissions': (('change_application_status', 'Can change the application status'),), 'verbose_name': 'application', 'verbose_name_plural': 'applications'},
        ),
    ]
