# Generated by Django 5.0.1 on 2024-02-06 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_membersmodel_superusermodel_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='membersmodel',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='membersmodel',
            name='password',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]