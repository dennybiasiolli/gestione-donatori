import pytest
from django.urls import reverse

from avis.models import Donatore

pytestmark = pytest.mark.django_db


def test_unauthenticated_redirects_to_login(client):
    response = client.get(reverse("donatori"))
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_index_redirects_to_donatori(client, staff_user, stato_attivo):
    client.force_login(staff_user)
    response = client.get(reverse("index"))
    assert response.status_code == 302
    assert response["Location"] == reverse("donatori")


def test_donatori_list_empty(client, staff_user, stato_attivo):
    client.force_login(staff_user)
    response = client.get(reverse("donatori"))
    assert response.status_code == 200
    assert list(response.context["object_list"]) == []


def test_donatori_list_shows_donor(client, staff_user, donatore):
    client.force_login(staff_user)
    response = client.get(reverse("donatori"))
    assert response.status_code == 200
    assert donatore in response.context["object_list"]


def test_donatore_detail(client, staff_user, donatore):
    client.force_login(staff_user)
    response = client.get(reverse("donatore", kwargs={"pk": donatore.pk}))
    assert response.status_code == 200
    assert response.context["object"] == donatore


def test_dati_statistici(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("dati-statistici"))
    assert response.status_code == 200


def test_donatori_list_defaults_to_attivo(
    client, staff_user, donatore, sezione, sesso_m, stato_inattivo
):
    inattivo = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="002",
        cognome="Bianchi",
        nome="Luigi",
        sesso=sesso_m,
        stato_donatore=stato_inattivo,
    )
    client.force_login(staff_user)
    response = client.get(reverse("donatori"))
    object_list = list(response.context["object_list"])
    assert donatore in object_list
    assert inattivo not in object_list


def test_donatori_list_stato_filter_empty_means_all_statuses(
    client, staff_user, donatore, sezione, sesso_m, stato_inattivo
):
    inattivo = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="002",
        cognome="Bianchi",
        nome="Luigi",
        sesso=sesso_m,
        stato_donatore=stato_inattivo,
    )
    client.force_login(staff_user)
    response = client.get(reverse("donatori"), {"stato_filter": "1"})
    object_list = list(response.context["object_list"])
    assert donatore in object_list
    assert inattivo in object_list


def test_elenco_stampa_includes_inactive_donors(
    client, staff_user, donatore, sezione, sesso_m, stato_inattivo
):
    inattivo = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="002",
        cognome="Bianchi",
        nome="Luigi",
        sesso=sesso_m,
        stato_donatore=stato_inattivo,
        stampa_donatore=True,
    )
    client.force_login(staff_user)
    response = client.get(reverse("donatori"), {"only_stampa": "1"})
    object_list = list(response.context["object_list"])
    assert inattivo in object_list
    assert donatore not in object_list
