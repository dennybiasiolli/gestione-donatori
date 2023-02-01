# Generated by Django 4.0.5 on 2022-06-11 16:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Sezione",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("descrizione", models.CharField(max_length=100)),
                ("indirizzo", models.CharField(max_length=255)),
                ("cap", models.CharField(max_length=5)),
                ("comune", models.CharField(max_length=100)),
                ("provincia", models.CharField(max_length=2)),
                ("telefono", models.CharField(blank=True, max_length=20)),
                ("fax", models.CharField(blank=True, max_length=20)),
                ("email", models.CharField(max_length=100)),
                ("presidente", models.CharField(max_length=100)),
                ("segretario", models.CharField(max_length=100)),
                (
                    "utente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Sezioni",
            },
        ),
    ]
