# Generated by Django 4.1 on 2022-09-01 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avis', '0008_rename_num_tessera_donatore_num_tessera_avis'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donatore',
            old_name='num_tessera_cartacea',
            new_name='num_tessera_ct',
        ),
        migrations.AlterField(
            model_name='donatore',
            name='num_tessera_ct',
            field=models.CharField(
                blank=True,
                help_text=(
                    'Num. Tessera usato per la registrazione'
                    ' e comunicato al Centro Trasfusionale'
                ),
                max_length=255,
                verbose_name='N. Tessera C.T.',
            ),
        ),
    ]