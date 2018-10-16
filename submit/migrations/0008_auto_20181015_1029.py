# Generated by Django 2.0.4 on 2018-10-15 03:29

import django.core.files.storage
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0007_auto_20181004_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submitmodel',
            name='fileSubmitted',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage('C:\\Users\\tuank\\PycharmProjects\\VulnerablititesManagement\\files_data\\imported_file'), upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['zip'])], verbose_name='File attachment'),
        ),
    ]