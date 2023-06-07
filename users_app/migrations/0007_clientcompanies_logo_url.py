# Generated by Django 2.2.7 on 2022-04-20 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0006_dashboards_related_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientcompanies',
            name='logo_url',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users_app.clientcompanies'),
        ),
        migrations.AddField(
            model_name='candidatepresentation',
            name='extension_value',
            field=models.TextField(default='none'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]