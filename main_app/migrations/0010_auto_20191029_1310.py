# Generated by Django 2.1.2 on 2019-10-29 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_auto_20191029_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='constituency',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='constituency',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
