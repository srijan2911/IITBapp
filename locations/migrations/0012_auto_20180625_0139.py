# Generated by Django 2.0.5 on 2018-06-24 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0011_auto_20180625_0104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='parent_relation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='short_name',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]
