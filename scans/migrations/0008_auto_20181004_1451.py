# Generated by Django 2.0.4 on 2018-10-04 07:51

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0007_auto_20180925_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scantaskmodel',
            name='fileAttachment',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\tuank\\PycharmProjects\\VulnerablititesManagement\\files_data\\scan_attachment'), upload_to='', verbose_name='File attachment'),
        ),
    ]
