import pytest
from django.contrib.auth import get_user_model

from avis.models import Donatore, Sesso, Sezione, StatoDonatore

User = get_user_model()


@pytest.fixture
def sesso_m(db):
    return Sesso.objects.create(
        codice="M",
        descrizione="Maschio",
        gg_da_sangue_a_sangue=90,
        gg_da_sangue_a_plasma=30,
        gg_da_sangue_a_piastrine=30,
        gg_da_plasma_a_sangue=14,
        gg_da_plasma_a_plasma=14,
        gg_da_plasma_a_piastrine=14,
        gg_da_piastrine_a_sangue=14,
        gg_da_piastrine_a_plasma=30,
        gg_da_piastrine_a_piastrine=30,
    )


@pytest.fixture
def stato_attivo(db):
    return StatoDonatore.objects.create(
        codice="Attivo", descrizione="Attivo", is_attivo=True
    )


@pytest.fixture
def stato_inattivo(db):
    return StatoDonatore.objects.create(
        codice="Inattivo", descrizione="Inattivo", is_attivo=False
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="teststaff", password="testpass", is_staff=True
    )


@pytest.fixture
def sezione(staff_user):
    return Sezione.objects.create(
        utente=staff_user,
        descrizione="Sezione Test",
        indirizzo="Via Test 1",
        cap="12345",
        comune="TestCity",
        provincia="TC",
        email="test@test.com",
        presidente="Test Presidente",
        segretario="Test Segretario",
    )


@pytest.fixture
def donatore(sezione, sesso_m, stato_attivo):
    return Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="001",
        cognome="Rossi",
        nome="Mario",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
