# Generated by Django 4.0.5 on 2022-06-11 20:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("avis", "0001_sezione"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sesso",
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
                ("codice", models.CharField(max_length=1, unique=True)),
                ("descrizione", models.CharField(max_length=20)),
                ("gg_da_sangue_a_sangue", models.IntegerField()),
                ("gg_da_sangue_a_plasma", models.IntegerField()),
                ("gg_da_sangue_a_piastrine", models.IntegerField()),
                ("gg_da_plasma_a_sangue", models.IntegerField()),
                ("gg_da_plasma_a_plasma", models.IntegerField()),
                ("gg_da_plasma_a_piastrine", models.IntegerField()),
                ("gg_da_piastrine_a_sangue", models.IntegerField()),
                ("gg_da_piastrine_a_plasma", models.IntegerField()),
                ("gg_da_piastrine_a_piastrine", models.IntegerField()),
            ],
            options={
                "verbose_name_plural": "Sessi",
            },
        ),
        migrations.CreateModel(
            name="StatoDonatore",
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
                ("codice", models.CharField(max_length=20)),
                ("descrizione", models.CharField(blank=True, max_length=100)),
                (
                    "is_attivo",
                    models.BooleanField(default=True, verbose_name="Attivo"),
                ),
                (
                    "sezione",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="avis.sezione",
                    ),
                ),
            ],
            options={
                "verbose_name": "Stato donatore",
                "verbose_name_plural": "Stati donatore",
                "unique_together": {("sezione", "codice")},
            },
        ),
    ]
