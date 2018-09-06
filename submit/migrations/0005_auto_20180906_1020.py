# Generated by Django 2.0.4 on 2018-09-06 03:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0004_submitmodel_scantask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submitmodel',
            name='scanTask',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scans.ScanTaskModel'),
        ),
        migrations.AlterField(
            model_name='submitmodel',
            name='submitter',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
