# Generated by Django 4.1 on 2022-09-01 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avis', '0011_removing_piastrine_from_donazioni'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donazione',
            name='tipo_donazione',
            field=models.IntegerField(
                blank=True,
                choices=[
                    (None, 'Non specificato'),
                    (1, 'Sangue intero'),
                    (2, 'Plasma'),
                ],
                default='Non specificato',
                null=True,
            ),
        ),
    ]