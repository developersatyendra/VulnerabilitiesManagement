# Generated by Django 2.0.4 on 2018-09-25 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0006_auto_20180906_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scantaskmodel',
            name='scanProject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ScanProjectScanTask', to='projects.ScanProjectModel'),
        ),
    ]
