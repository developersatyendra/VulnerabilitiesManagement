# Generated by Django 2.0.4 on 2018-10-01 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_auto_20181001_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportmodel',
            name='status',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Requested'), (1, 'Processing'), (2, 'Processed'), (3, 'Error')], default=0, null=True, verbose_name='Description of Vulnerability'),
        ),
    ]
