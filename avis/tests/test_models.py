from datetime import date

import pytest
from django.core.exceptions import ValidationError

from avis.models import Donatore, Donazione

pytestmark = pytest.mark.django_db


def test_donatore_str(donatore):
    assert str(donatore) == "001 - Rossi Mario"


def test_num_benemerenze_conseguite_no_config(donatore):
    donatore.sezione.configurazione_benemerenze = []
    donatore.sezione.save()
    assert donatore.num_benemerenze_conseguite == 0


def test_num_benemerenze_conseguite_below_first_threshold(donatore):
    donatore.sezione.configurazione_benemerenze = [5, 10, 20]
    donatore.sezione.save()
    assert donatore.num_benemerenze_conseguite == 0


def test_num_benemerenze_conseguite_between_thresholds(donatore):
    donatore.sezione.configurazione_benemerenze = [1, 5]
    donatore.sezione.save()
    Donazione.objects.create(
        donatore=donatore, tipo_donazione=None, data_donazione=date(2024, 1, 1)
    )
    Donazione.objects.create(
        donatore=donatore, tipo_donazione=None, data_donazione=date(2024, 2, 1)
    )
    # 2 donations: >= threshold[0]=1 but < threshold[1]=5 → index 1
    assert donatore.num_benemerenze_conseguite == 1


def test_num_benemerenze_conseguite_above_all_thresholds(donatore):
    donatore.sezione.configurazione_benemerenze = [1, 2]
    donatore.sezione.save()
    Donazione.objects.create(
        donatore=donatore, tipo_donazione=None, data_donazione=date(2024, 1, 1)
    )
    Donazione.objects.create(
        donatore=donatore, tipo_donazione=None, data_donazione=date(2024, 2, 1)
    )
    Donazione.objects.create(
        donatore=donatore, tipo_donazione=None, data_donazione=date(2024, 3, 1)
    )
    # 3 donations: above all thresholds → returns len of config
    assert donatore.num_benemerenze_conseguite == 2


def test_validate_unique_raises_for_duplicate_active_ct(sezione, sesso_m, stato_attivo):
    Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="001",
        num_tessera_ct="CT001",
        cognome="Rossi",
        nome="Mario",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    duplicate = Donatore(
        sezione=sezione,
        num_tessera_avis="002",
        num_tessera_ct="CT001",
        cognome="Bianchi",
        nome="Luigi",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    with pytest.raises(ValidationError, match="num_tessera_ct"):
        duplicate.validate_unique()


def test_validate_unique_allows_same_ct_if_existing_is_inactive(
    sezione, sesso_m, stato_attivo, stato_inattivo
):
    Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="001",
        num_tessera_ct="CT001",
        cognome="Rossi",
        nome="Mario",
        sesso=sesso_m,
        stato_donatore=stato_inattivo,
    )
    active_donor = Donatore(
        sezione=sezione,
        num_tessera_avis="002",
        num_tessera_ct="CT001",
        cognome="Bianchi",
        nome="Luigi",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    # Should not raise — existing donor with same CT is inactive
    active_donor.validate_unique(exclude=None)
