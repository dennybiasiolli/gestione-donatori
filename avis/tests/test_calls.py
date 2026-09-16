from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from avis.calls import (
    ORDER_DESC,
    ORDER_DONATORE,
    ORDER_PROSSIMA,
    ORDER_ULTIMA,
    ULTIMO_MAI,
    called_within_days,
    eligible_today,
    next_eligible_date,
    parse_focus_type,
    parse_hide_days,
    parse_order_by,
    parse_order_direction,
    parse_ultimo,
)
from avis.models import CallLog, Donatore, Donazione, Sezione

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_parse_focus_type_defaults_to_whole_blood():
    assert parse_focus_type(None) == Donazione.TipoDonazione.SANGUE_INTERO
    assert parse_focus_type("nope") == Donazione.TipoDonazione.SANGUE_INTERO
    assert parse_focus_type("2") == Donazione.TipoDonazione.PLASMA


def test_parse_order_by_defaults_to_prossima():
    assert parse_order_by(None) == ORDER_PROSSIMA
    assert parse_order_by("nope") == ORDER_PROSSIMA
    assert parse_order_by(ORDER_DONATORE) == ORDER_DONATORE
    assert parse_order_direction("-") == ORDER_DESC
    assert parse_order_direction("up") == ""
    assert parse_ultimo("chiamato") == CallLog.Result.CALLED
    assert parse_ultimo("nope") == ""
    assert parse_hide_days(None) == 1
    assert parse_hide_days("0") == 0
    assert parse_hide_days("7") == 7
    assert parse_hide_days("-3") == 0


def test_next_eligible_date_without_donations_is_today(sesso_m):
    today = date(2026, 9, 16)
    assert (
        next_eligible_date(
            sesso_m, None, None, Donazione.TipoDonazione.SANGUE_INTERO, today
        )
        == today
    )


def test_next_eligible_date_uses_sesso_interval(sesso_m):
    last = date(2026, 6, 18)
    next_date = next_eligible_date(
        sesso_m,
        last,
        Donazione.TipoDonazione.SANGUE_INTERO,
        Donazione.TipoDonazione.SANGUE_INTERO,
        date(2026, 9, 16),
    )
    assert next_date == last + timedelta(days=90)


def test_unauthenticated_chiama_oggi_redirects(client):
    response = client.get(reverse("chiama-oggi"))
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_never_donated_active_donor_is_callable(client, staff_user, donatore):
    donatore.cellulare = "3331112222"
    donatore.save()
    client.force_login(staff_user)
    response = client.get(reverse("chiama-oggi"))
    assert response.status_code == 200
    pks = [row["donatore"].pk for row in response.context["rows"]]
    assert donatore.pk in pks
    assert "Chiama oggi" in response.content.decode()


def test_inactive_and_ill_donors_are_excluded(
    client, staff_user, donatore, sezione, sesso_m, stato_inattivo, stato_attivo
):
    donatore.fermo_per_malattia = True
    donatore.save()
    inattivo = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="003",
        cognome="Neri",
        nome="Paolo",
        sesso=sesso_m,
        stato_donatore=stato_inattivo,
    )
    client.force_login(staff_user)
    response = client.get(reverse("chiama-oggi"))
    pks = [row["donatore"].pk for row in response.context["rows"]]
    assert donatore.pk not in pks
    assert inattivo.pk not in pks


def test_recent_donation_excluded_until_interval_elapses(client, staff_user, donatore):
    today = timezone.localdate()
    Donazione.objects.create(
        donatore=donatore,
        tipo_donazione=Donazione.TipoDonazione.SANGUE_INTERO,
        data_donazione=today - timedelta(days=10),
    )
    client.force_login(staff_user)
    response = client.get(reverse("chiama-oggi"))
    pks = [row["donatore"].pk for row in response.context["rows"]]
    assert donatore.pk not in pks

    Donazione.objects.filter(donatore=donatore).update(
        data_donazione=today - timedelta(days=90)
    )
    response = client.get(reverse("chiama-oggi"))
    pks = [row["donatore"].pk for row in response.context["rows"]]
    assert donatore.pk in pks


def test_other_section_donor_not_listed(
    client, staff_user, donatore, sesso_m, stato_attivo
):
    other = User.objects.create_user(username="otherstaff", password="x", is_staff=True)
    other_sezione = Sezione.objects.create(
        utente=other,
        descrizione="Altra",
        indirizzo="Via 2",
        cap="00000",
        comune="Altro",
        provincia="AA",
        email="a@b.c",
        presidente="P",
        segretario="S",
    )
    other_donor = Donatore.objects.create(
        sezione=other_sezione,
        num_tessera_avis="099",
        cognome="Altro",
        nome="Utente",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    client.force_login(staff_user)
    rows = eligible_today(staff_user, Donazione.TipoDonazione.SANGUE_INTERO)
    pks = [row["donatore"].pk for row in rows]
    assert donatore.pk in pks
    assert other_donor.pk not in pks


def test_chiama_oggi_default_sort_is_next_date(
    client, staff_user, donatore, sezione, sesso_m, stato_attivo
):
    today = timezone.localdate()
    earlier = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="010",
        cognome="Verdi",
        nome="Anna",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    Donazione.objects.create(
        donatore=earlier,
        tipo_donazione=Donazione.TipoDonazione.SANGUE_INTERO,
        data_donazione=today - timedelta(days=120),
    )
    client.force_login(staff_user)
    response = client.get(reverse("chiama-oggi"))
    names = [row["donatore"].cognome for row in response.context["rows"]]
    assert names == ["Verdi", "Rossi"]
    assert response.context["order_by"] == ORDER_PROSSIMA
    assert 'name="comune"' not in response.content.decode()
    assert "Ultimo chiamato" in response.content.decode()
    html = response.content.decode()
    assert "bi-caret-up-fill" in html
    assert "ordinato crescente" in html
    assert response.context["paginate_by"] == 10
    assert 'target="_blank"' in html
    assert "Stampa lista" in html


def test_chiama_oggi_sort_by_donor_and_last_donation(
    client, staff_user, donatore, sezione, sesso_m, stato_attivo
):
    today = timezone.localdate()
    earlier = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="010",
        cognome="Verdi",
        nome="Anna",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    Donazione.objects.create(
        donatore=earlier,
        tipo_donazione=Donazione.TipoDonazione.SANGUE_INTERO,
        data_donazione=today - timedelta(days=120),
    )
    client.force_login(staff_user)

    by_name = client.get(reverse("chiama-oggi"), {"order_by": ORDER_DONATORE})
    assert [row["donatore"].cognome for row in by_name.context["rows"]] == [
        "Rossi",
        "Verdi",
    ]

    by_last = client.get(reverse("chiama-oggi"), {"order_by": ORDER_ULTIMA})
    assert [row["donatore"].cognome for row in by_last.context["rows"]] == [
        "Verdi",
        "Rossi",
    ]

    descending = client.get(
        reverse("chiama-oggi"),
        {"order_by": ORDER_DONATORE, "order_by_direction": ORDER_DESC},
    )
    assert [row["donatore"].cognome for row in descending.context["rows"]] == [
        "Verdi",
        "Rossi",
    ]
    assert "bi-caret-down-fill" in descending.content.decode()
    assert "ordinato decrescente" in descending.content.decode()


def test_chiama_oggi_filters_by_last_call(
    client, staff_user, donatore, sezione, sesso_m, stato_attivo
):
    chiamato = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="011",
        cognome="Verdi",
        nome="Anna",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    CallLog.objects.create(
        donatore=chiamato,
        result=CallLog.Result.CALLED,
        created_by=staff_user,
    )
    client.force_login(staff_user)

    never = client.get(reverse("chiama-oggi"), {"ultimo": ULTIMO_MAI})
    assert [row["donatore"].pk for row in never.context["rows"]] == [donatore.pk]

    called = client.get(reverse("chiama-oggi"), {"ultimo": "chiamato"})
    assert [row["donatore"].pk for row in called.context["rows"]] == [chiamato.pk]

    recall = client.get(reverse("chiama-oggi"), {"ultimo": "richiamare"})
    assert [row["donatore"].pk for row in recall.context["rows"]] == []


def test_chiama_oggi_hides_people_called_today(
    client, staff_user, donatore, sezione, sesso_m, stato_attivo
):
    chiamato = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="013",
        cognome="Verdi",
        nome="Anna",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    no_answer = Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="014",
        cognome="Neri",
        nome="Luca",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    CallLog.objects.create(
        donatore=chiamato,
        result=CallLog.Result.CALLED,
        created_by=staff_user,
    )
    CallLog.objects.create(
        donatore=no_answer,
        result=CallLog.Result.NO_ANSWER,
        created_by=staff_user,
    )
    client.force_login(staff_user)

    hidden = client.get(reverse("chiama-oggi"))
    pks = [row["donatore"].pk for row in hidden.context["rows"]]
    assert chiamato.pk not in pks
    assert donatore.pk in pks
    assert no_answer.pk in pks
    assert hidden.context["hidden_chiamati_count"] == 1
    assert hidden.context["nascondi_giorni"] == 1
    assert "nascosti (chiamati da 1 gg)" in hidden.content.decode()

    shown = client.get(reverse("chiama-oggi"), {"nascondi_giorni": "0"})
    shown_pks = [row["donatore"].pk for row in shown.context["rows"]]
    assert chiamato.pk in shown_pks
    assert shown.context["hidden_chiamati_count"] == 0


def test_called_yesterday_stays_on_todays_list(client, staff_user, donatore):
    log = CallLog.objects.create(
        donatore=donatore,
        result=CallLog.Result.CALLED,
        created_by=staff_user,
    )
    CallLog.objects.filter(pk=log.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )
    client.force_login(staff_user)
    response = client.get(reverse("chiama-oggi"))
    pks = [row["donatore"].pk for row in response.context["rows"]]
    assert donatore.pk in pks

    hidden = client.get(reverse("chiama-oggi"), {"nascondi_giorni": "2"})
    hidden_pks = [row["donatore"].pk for row in hidden.context["rows"]]
    assert donatore.pk not in hidden_pks
    assert hidden.context["hidden_chiamati_count"] == 1


def test_called_within_days_helper(staff_user, donatore):
    log = CallLog.objects.create(
        donatore=donatore,
        result=CallLog.Result.CALLED,
        created_by=staff_user,
    )
    assert called_within_days(log, 1) is True
    assert called_within_days(log, 0) is False
    CallLog.objects.filter(pk=log.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )
    log.refresh_from_db()
    assert called_within_days(log, 1) is False
    assert called_within_days(log, 2) is True


def test_chiama_oggi_paginates(
    client, staff_user, donatore, sezione, sesso_m, stato_attivo
):
    Donatore.objects.create(
        sezione=sezione,
        num_tessera_avis="012",
        cognome="Verdi",
        nome="Anna",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    client.force_login(staff_user)
    page1 = client.get(reverse("chiama-oggi"), {"paginate_by": "1", "page": "1"})
    page2 = client.get(reverse("chiama-oggi"), {"paginate_by": "1", "page": "2"})
    assert page1.context["row_count"] == 2
    assert page1.context["page_obj"].paginator.num_pages == 2
    assert len(page1.context["rows"]) == 1
    assert len(page2.context["rows"]) == 1
    assert (
        page1.context["rows"][0]["donatore"].pk
        != page2.context["rows"][0]["donatore"].pk
    )


def test_call_log_create_records_outcome(client, staff_user, donatore):
    client.force_login(staff_user)
    response = client.post(
        reverse("call-log-create", kwargs={"pk": donatore.pk}),
        {"result": "chiamato", "note": "Richiamare lunedì", "tipo": "1"},
        follow=True,
    )
    assert response.status_code == 200
    log = CallLog.objects.get()
    assert log.donatore == donatore
    assert log.result == CallLog.Result.CALLED
    assert log.note == "Richiamare lunedì"
    assert log.created_by == staff_user
    assert "Chiamata annotata" in response.content.decode()
    pks = [row["donatore"].pk for row in response.context["rows"]]
    assert donatore.pk not in pks


def test_call_log_invalid_result_is_rejected(client, staff_user, donatore):
    client.force_login(staff_user)
    response = client.post(
        reverse("call-log-create", kwargs={"pk": donatore.pk}),
        {"result": "appuntamento"},
        follow=True,
    )
    assert response.status_code == 200
    assert CallLog.objects.count() == 0
    messages = [str(message) for message in response.context["messages"]]
    assert "Esito chiamata non valido." in messages


def test_call_log_other_section_is_404(client, staff_user, sesso_m, stato_attivo):
    other = User.objects.create_user(
        username="otherstaff2", password="x", is_staff=True
    )
    other_sezione = Sezione.objects.create(
        utente=other,
        descrizione="Altra2",
        indirizzo="Via 3",
        cap="00000",
        comune="Altro",
        provincia="AA",
        email="c@d.e",
        presidente="P",
        segretario="S",
    )
    other_donor = Donatore.objects.create(
        sezione=other_sezione,
        num_tessera_avis="100",
        cognome="Fuori",
        nome="Sezione",
        sesso=sesso_m,
        stato_donatore=stato_attivo,
    )
    client.force_login(staff_user)
    response = client.post(
        reverse("call-log-create", kwargs={"pk": other_donor.pk}),
        {"result": "chiamato"},
    )
    assert response.status_code == 404
    assert CallLog.objects.count() == 0
