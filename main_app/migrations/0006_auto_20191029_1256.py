# Generated by Django 2.1.2 on 2019-10-29 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_auto_20191029_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='constituency',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='party',
            name='id',
            field=models.AutoField(default=2, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='region',
            name='id',
            field=models.AutoField(default=3, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='constituency',
            name='id_number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='party',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]