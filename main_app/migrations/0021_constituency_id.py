# Generated by Django 2.1.2 on 2019-10-30 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0020_auto_20191030_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='constituency',
            name='id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
