# Generated by Django 2.1.2 on 2019-10-29 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0012_auto_20191029_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='shortname',
            field=models.CharField(max_length=6),
        ),
    ]
