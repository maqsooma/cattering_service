# Generated by Django 4.2.10 on 2024-02-23 09:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_is_staff_customuser_is_superuser_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='email_address',
        ),
    ]
