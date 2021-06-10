# Generated by Django 3.2.4 on 2021-06-08 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('voucher', '0006_portal_allow_printing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roll',
            name='minutes',
        ),
        migrations.AddField(
            model_name='roll',
            name='time_limit',
            field=models.CharField(default='15 minutes', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='portal',
            name='allow_printing',
            field=models.ManyToManyField(blank=True, null=True, to='auth.Group'),
        ),
    ]