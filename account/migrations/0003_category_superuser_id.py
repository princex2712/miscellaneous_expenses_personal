# Generated by Django 5.0.1 on 2024-02-22 02:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_category_expenses'),
        ('authentication', '0010_alter_membersmodel_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='superuser_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='authentication.superusermodel'),
            preserve_default=False,
        ),
    ]
