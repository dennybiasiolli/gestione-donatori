from datetime import date
from typing import Collection, Optional

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Sezione(models.Model):
    utente = models.ForeignKey(User, on_delete=models.RESTRICT)
    descrizione = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)
    cap = models.CharField(max_length=5)
    comune = models.CharField(max_length=100)
    provincia = models.CharField(max_length=2)
    telefono = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100)
    presidente = models.CharField(max_length=100)
    segretario = models.CharField(max_length=100)
    luogo_stampa_benemerenze = models.CharField(
        max_length=100,
        blank=True,
        help_text="Luogo da usare per la stampa delle benemerenze,"
        " se non specificato, verrà usato il comune della sezione.",
    )
    data_stampa_benemerenze = models.DateField(
        null=True,
        blank=True,
        help_text="Data da usare per la stampa delle benemerenze,"
        " se non specificata, verrà usata la data corrente.",
    )
    configurazione_benemerenze = ArrayField(
        models.SmallIntegerField(),
        blank=True,
        default=list,
        # default=[7, 15, 24, 48, 72, 95, 114],
        help_text=(
            "Configurazione delle benemerenze conseguite "
            "(valori numerici interi, separati da virgola)."
        ),
    )

    class Meta:
        verbose_name_plural = "Sezioni"

    def __str__(self):
        return self.descrizione


class Sesso(models.Model):
    codice = models.CharField(max_length=1, unique=True)
    descrizione = models.CharField(max_length=20)
    gg_da_sangue_a_sangue = models.IntegerField()
    gg_da_sangue_a_plasma = models.IntegerField()
    gg_da_sangue_a_piastrine = models.IntegerField()
    gg_da_plasma_a_sangue = models.IntegerField()
    gg_da_plasma_a_plasma = models.IntegerField()
    gg_da_plasma_a_piastrine = models.IntegerField()
    gg_da_piastrine_a_sangue = models.IntegerField()
    gg_da_piastrine_a_plasma = models.IntegerField()
    gg_da_piastrine_a_piastrine = models.IntegerField()

    class Meta:
        verbose_name_plural = "Sessi"

    def __str__(self):
        return self.descrizione


class StatoDonatore(models.Model):
    sezione = models.ForeignKey(
        Sezione, blank=True, null=True, on_delete=models.CASCADE
    )
    codice = models.CharField(max_length=20)
    descrizione = models.CharField(max_length=100, blank=True)
    is_attivo = models.BooleanField(default=True, verbose_name="Attivo")
    can_export_elenco_soci_xls = models.BooleanField(
        default=True,
        verbose_name="Includi in Elenco Soci Excel",
        help_text="Include i donatori in questo stato nell'export dell'elenco soci",
    )

    class Meta:
        verbose_name = "Stato donatore"
        verbose_name_plural = "Stati donatore"
        unique_together = (
            "sezione",
            "codice",
        )

    def __str__(self):
        return self.descrizione


class Donatore(models.Model):
    sezione = models.ForeignKey(
        Sezione, related_name="donatori", on_delete=models.RESTRICT
    )
    num_tessera_avis = models.CharField(
        max_length=255,
        help_text="Num. Tessera AVIS, inserito nel programma",
        verbose_name="N. Tessera AVIS",
    )
    num_tessera_ct = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Num. Tessera usato per la registrazione"
            " e comunicato al Centro Trasfusionale"
        ),
        verbose_name="N. Tessera C.T.",
    )
    cognome = models.CharField(max_length=255)
    nome = models.CharField(max_length=255)
    sesso = models.ForeignKey(Sesso, on_delete=models.RESTRICT)
    stato_donatore = models.ForeignKey(StatoDonatore, on_delete=models.RESTRICT)
    motivo_inattivita = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Motivo inattività",
        help_text="Inserire eventuale motivo di inattività",
    )
    fermo_per_malattia = models.BooleanField(default=False)
    data_rilascio_tessera = models.DateField(null=True, blank=True)
    codice_fiscale = models.CharField(max_length=255, blank=True)
    data_nascita = models.DateField(null=True, blank=True)
    luogo_nascita = models.CharField(max_length=255, blank=True)
    data_iscrizione = models.DateField(null=True, blank=True)
    data_cessata_iscrizione = models.DateField(null=True, blank=True)
    causa_cessata_iscrizione = models.CharField(max_length=255, blank=True)
    gruppo_sanguigno = models.CharField(max_length=10, blank=True)
    rh = models.CharField(max_length=10, blank=True)
    fenotipo = models.CharField(max_length=10, blank=True)
    kell = models.CharField(max_length=10, blank=True)
    indirizzo = models.CharField(max_length=255, blank=True)
    frazione = models.CharField(max_length=255, blank=True)
    cap = models.CharField(max_length=10, blank=True)
    comune = models.CharField(max_length=255, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=255, blank=True)
    telefono_lavoro = models.CharField(max_length=255, blank=True)
    cellulare = models.CharField(max_length=255, blank=True)
    fax = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    donazioni_pregresse = models.IntegerField(default=0)
    num_benemerenze_consegnate = models.IntegerField(default=0)
    scheda_anamnestica = models.TextField(blank=True)
    stampa_donatore = models.BooleanField(default=False)
    check_privacy = models.BooleanField(
        default=False,
        verbose_name="Modulo privacy compilato e consegnato",
    )
    check_privacy_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data compilazione e consegna modulo privacy",
    )

    class Meta:
        verbose_name_plural = "Donatori"
        unique_together = (
            "sezione",
            "num_tessera_avis",
        )

    def __str__(self):
        return "{} - {} {}".format(self.num_tessera_avis, self.cognome, self.nome)

    def validate_unique(self, exclude: Optional[Collection[str]] = ...) -> None:
        if (
            self.num_tessera_ct
            and Donatore.objects.select_related("stato_donatore")
            .filter(
                num_tessera_ct=self.num_tessera_ct,
                stato_donatore__is_attivo=True,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                {
                    "num_tessera_ct": (
                        "Questo valore è già utilizzato da un altro donatore attivo"
                    )
                }
            )
        return super().validate_unique(exclude)

    @property
    def num_benemerenze_conseguite(self):
        """Restituisce il numero di benemerenze conseguite dal donatore."""
        if not self.sezione.configurazione_benemerenze:
            return 0
        for i, soglia in enumerate(self.sezione.configurazione_benemerenze):
            if self.donazioni.count() < soglia:
                return i
        return len(self.sezione.configurazione_benemerenze)


class Donazione(models.Model):
    class TipoDonazione(models.IntegerChoices):
        SANGUE_INTERO = 1, "Sangue intero"
        PLASMA = 2, "Plasma"
        # PIASTRINE = 3, 'Piastrine'
        ERITRO_PLASMAFERESI = 4, "Eritro-Plasmaferesi"
        ERITROCITI = 5, "Eritrociti"
        __empty__ = "Non specificato"

    donatore = models.ForeignKey(
        Donatore, related_name="donazioni", on_delete=models.CASCADE
    )
    tipo_donazione = models.IntegerField(
        null=True,
        choices=TipoDonazione.choices,
        default=TipoDonazione.__empty__,
        blank=True,
    )
    data_donazione = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "Donazioni"
        unique_together = (
            "donatore",
            "data_donazione",
        )

    def __str__(self):
        return "{} - {} {}".format(
            self.data_donazione, self.donatore.cognome, self.donatore.nome
        )
