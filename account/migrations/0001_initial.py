# Generated by Django 5.0.1 on 2024-02-16 13:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0006_membersmodel_is_superuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.membersmodel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
