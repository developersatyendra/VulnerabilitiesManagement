# Generated by Django 2.0.4 on 2018-09-27 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_auto_20180927_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportmodel',
            name='format',
            field=models.SmallIntegerField(choices=[(0, 'PDF'), (1, 'XML'), (2, 'XLS'), (3, 'HTML')], default=0, verbose_name='File format of report'),
        ),
    ]