# Generated by Django 4.1 on 2022-09-01 09:38

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    DonazioneModel = apps.get_model("avis", "Donazione")
    db_alias = schema_editor.connection.alias
    DonazioneModel.objects.using(db_alias).filter(
        tipo_donazione=3  # Donazione.TipoDonazione.PIASTRINE
    ).update(tipo_donazione=None)


class Migration(migrations.Migration):
    dependencies = [
        ("avis", "0010_donatore_luogo_nascita"),
    ]

    operations = [
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
