# Generated by Django 4.1 on 2022-09-01 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("avis", "0009_rename_num_tessera_cartacea_donatore_num_tessera_ct"),
    ]

    operations = [
        migrations.AddField(
            model_name="donatore",
            name="luogo_nascita",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
