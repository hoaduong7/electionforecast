# Generated by Django 2.1.2 on 2019-10-29 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_auto_20191029_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constituency',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]