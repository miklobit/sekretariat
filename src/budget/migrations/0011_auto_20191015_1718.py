# Generated by Django 2.2.6 on 2019-10-15 15:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0010_auto_20191014_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='submitted',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2019, 10, 15, 15, 18, 11, 250058, tzinfo=utc), verbose_name='submission date'),
            preserve_default=False,
        ),
    ]
