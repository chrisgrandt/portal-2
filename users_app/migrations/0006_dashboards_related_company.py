# Generated by Django 2.2.7 on 2022-04-05 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0005_candidatepresentation_presentationaccess'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboards',
            name='related_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users_app.ClientCompanies'),
        ),
    ]
