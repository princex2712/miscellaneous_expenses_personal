# Generated by Django 5.0.1 on 2024-02-09 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_membersmodel_superuser_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='superusermodel',
            name='otp',
            field=models.CharField(default=100000, max_length=50),
        ),
    ]
