# Generated by Django 4.0 on 2022-07-04 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oracle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='market_status',
            field=models.CharField(default='A', max_length=20),
        ),
    ]