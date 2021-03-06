# Generated by Django 3.1.1 on 2020-10-10 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('donatori', '0005_donazione'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donatore',
            name='sezione',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donatori', to='donatori.sezione'),
        ),
        migrations.AlterField(
            model_name='donazione',
            name='donatore',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donazioni', to='donatori.donatore'),
        ),
    ]
