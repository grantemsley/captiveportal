# Generated by Django 3.2.4 on 2021-06-10 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0009_alter_portal_allow_printing'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='voucher',
            options={'permissions': [('view_reports', 'Can view voucher reports')]},
        ),
    ]