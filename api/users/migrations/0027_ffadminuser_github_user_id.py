# Generated by Django 2.2.13 on 2020-06-20 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_ffadminuser_google_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='ffadminuser',
            name='github_user_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]