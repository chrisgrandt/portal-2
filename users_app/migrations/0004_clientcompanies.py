# Generated by Django 2.2.7 on 2022-03-29 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0003_customuser_is_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientCompanies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.TextField()),
            ],
        ),
    ]