# Generated by Django 2.2.6 on 2019-10-11 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0006_auto_20191006_0842'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ('-date', 'amount'), 'verbose_name': 'application', 'verbose_name_plural': 'applications'},
        ),
    ]
