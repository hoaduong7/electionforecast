# Generated by Django 2.1.2 on 2019-10-31 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0027_auto_20191031_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constituency',
            name='id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='constituency',
            name='raw_name',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]