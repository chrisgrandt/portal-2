# Generated by Django 2.2.7 on 2020-04-08 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internalportal_app', '0004_auto_20200203_1703'),
    ]

    operations = [
        migrations.CreateModel(
            name='Weblinks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('site_url', models.CharField(max_length=200)),
                ('logo_url', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=30)),
            ],
        ),
    ]