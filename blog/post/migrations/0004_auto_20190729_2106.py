# Generated by Django 2.2.3 on 2019-07-29 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0003_auto_20190729_2059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='craeted',
            new_name='created',
        ),
    ]
