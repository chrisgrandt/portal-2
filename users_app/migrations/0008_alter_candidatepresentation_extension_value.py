# Generated by Django 3.2.13 on 2023-01-25 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0007_clientcompanies_logo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidatepresentation',
            name='extension_value',
            field=models.TextField(null=True),
        ),
    ]
