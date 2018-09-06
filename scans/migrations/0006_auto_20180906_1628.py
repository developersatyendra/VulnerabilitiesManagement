# Generated by Django 2.0.4 on 2018-09-06 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0005_auto_20180903_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scantaskmodel',
            name='scanInfo',
        ),
        migrations.AddField(
            model_name='scaninfomodel',
            name='scanTask',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ScanInfoScanTask', to='scans.ScanTaskModel'),
            preserve_default=False,
        ),
    ]
