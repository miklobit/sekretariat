# Generated by Django 2.2.6 on 2019-10-06 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_auto_20190602_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decision',
            name='notes',
            field=models.TextField(blank=True, help_text='Notatka nie jest wymagana do podjęcia decyzji.', null=True, verbose_name='notes'),
        ),
    ]
