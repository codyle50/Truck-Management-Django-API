# Generated by Django 3.2 on 2021-09-27 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account_app', '0004_user_paid_untill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='paid_untill',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
