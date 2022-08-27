# Generated by Django 4.0 on 2022-06-27 10:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('oracle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TriggerParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(max_length=128, unique=True, verbose_name='English Name')),
                ('name_fa', models.CharField(max_length=128, verbose_name='Persian Name')),
                ('description', models.CharField(max_length=1024, verbose_name='Description')),
                ('value', models.CharField(max_length=32, verbose_name='Parameter Value')),
                ('trigger_name', models.CharField(max_length=128, verbose_name='Trigger Name')),
            ],
        ),
        migrations.AlterField(
            model_name='instrument',
            name='market_status',
            field=models.CharField(default='A', max_length=20),
        ),
    ]