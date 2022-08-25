# Generated by Django 4.0.5 on 2022-06-11 20:30

from django.db import migrations

# Intervalli minimi previsti dalla legislazione italiana:
# da donazione di sangue intero a donazione di sangue intero:
#   90 giorni tra una donazione e l'altra; max. 4 l'anno per l'uomo,
#   2 volte l'anno in età fertile per la donna
# da donazione di sangue intero a donazione di plasma:
#   1 mese
# da donazione di plasma a donazione di sangue intero:
#   14 giorni
# da donazione di plasma a donazione di plasma:
#   14 giorni
# da donazione di sangue intero a donazione di piastrine:
#   1 mese
# da donazione di piastrine a donazione di sangue intero:
#   14 giorni
# da donazione di piastrine a donazione di piastrine:
#   15 giorni (massimo 6 donazioni all'anno)
# da donazione di multicomponenti a donazione di multicomponenti:
#   3 mesi


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Sesso = apps.get_model('avis', 'Sesso')
    StatoDonatore = apps.get_model('avis', 'StatoDonatore')
    db_alias = schema_editor.connection.alias

    Sesso.objects.using(db_alias).bulk_create(
        [
            Sesso(
                codice='M',
                descrizione='Maschio',
                gg_da_sangue_a_sangue=90,
                gg_da_sangue_a_plasma=30,
                gg_da_sangue_a_piastrine=30,
                gg_da_plasma_a_sangue=14,
                gg_da_plasma_a_plasma=14,
                gg_da_plasma_a_piastrine=14,
                gg_da_piastrine_a_sangue=14,
                gg_da_piastrine_a_plasma=30,
                gg_da_piastrine_a_piastrine=30,
            ),
            Sesso(
                codice='F',
                descrizione='Femmina',
                gg_da_sangue_a_sangue=180,
                gg_da_sangue_a_plasma=30,
                gg_da_sangue_a_piastrine=30,
                gg_da_plasma_a_sangue=14,
                gg_da_plasma_a_plasma=14,
                gg_da_plasma_a_piastrine=14,
                gg_da_piastrine_a_sangue=14,
                gg_da_piastrine_a_plasma=30,
                gg_da_piastrine_a_piastrine=30,
            ),
        ]
    )
    StatoDonatore.objects.using(db_alias).bulk_create(
        [
            StatoDonatore(
                sezione=None,
                codice='Attivo',
                descrizione='Attivo',
                is_attivo=True,
            ),
            StatoDonatore(
                sezione=None,
                codice='Inattivo',
                descrizione='Inattivo',
                is_attivo=False,
            ),
        ]
    )


def reverse_func(apps, schema_editor):
    # forwards_func() creates instances,
    # so reverse_func() should delete them.
    Sesso = apps.get_model('avis', 'Sesso')
    StatoDonatore = apps.get_model('avis', 'StatoDonatore')
    db_alias = schema_editor.connection.alias

    Sesso.objects.using(db_alias).filter(codice='M').delete()
    Sesso.objects.using(db_alias).filter(codice='F').delete()
    StatoDonatore.objects.using(db_alias).filter(sezione=None, codice='Attivo').delete()
    StatoDonatore.objects.using(db_alias).filter(
        sezione=None, codice='Inattivo'
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('avis', '0002_sesso_statodonatore'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
