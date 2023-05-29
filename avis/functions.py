from django.db.models import Count
from openpyxl import Workbook

from .models import Donatore, Donazione


def get_dati_statistici(user, anno: int) -> dict:
    qs = Donazione.objects.select_related(
        "donatore", "donatore__sesso", "donatore__sezione", "donatore__stato_donatore"
    ).filter(donatore__sezione__utente=user, data_donazione__year=anno)

    stats = {
        "Soci_Donatori": {
            "Maschi": {
                "18_25": 0,
                "26_35": 0,
                "36_45": 0,
                "46_55": 0,
                "56_65": 0,
                "Oltre_65": 0,
                "N_D": 0,
                "Totale": 0,
            },
            "Femmine": {
                "18_25": 0,
                "26_35": 0,
                "36_45": 0,
                "46_55": 0,
                "56_65": 0,
                "Oltre_65": 0,
                "N_D": 0,
                "Totale": 0,
            },
            "Totale": 0,
        },
        "Soci_Non_Donatori": {
            "Maschi": {
                "18_25": 0,
                "26_35": 0,
                "36_45": 0,
                "46_55": 0,
                "56_65": 0,
                "Oltre_65": 0,
                "N_D": 0,
                "Totale": 0,
            },
            "Femmine": {
                "18_25": 0,
                "26_35": 0,
                "36_45": 0,
                "46_55": 0,
                "56_65": 0,
                "Oltre_65": 0,
                "N_D": 0,
                "Totale": 0,
            },
            "Totale": 0,
        },
        "Soci_Nuovi_Iscritti": {
            "Maschi": {
                "18_25": 0,
                "26_35": 0,
                "36_45": 0,
                "46_55": 0,
                "56_65": 0,
                "Oltre_65": 0,
                "N_D": 0,
                "Totale": 0,
            },
            "Femmine": {
                "18_25": 0,
                "26_35": 0,
                "36_45": 0,
                "46_55": 0,
                "56_65": 0,
                "Oltre_65": 0,
                "N_D": 0,
                "Totale": 0,
            },
            "Totale": 0,
        },
    }

    stats_gruppo = {
        "0_RHp": 0,
        "0_RHn": 0,
        "A_RHp": 0,
        "A_RHn": 0,
        "B_RHp": 0,
        "B_RHn": 0,
        "AB_RHp": 0,
        "AB_RHn": 0,
        "N_D": 0,
        "Totale": 0,
    }

    stats_tipo = {
        "Sangue_Intero": {
            "Maschi": 0,
            "Femmine": 0,
            "Totale": 0,
        },
        "Plasmaferesi": {
            "Maschi": 0,
            "Femmine": 0,
            "Totale": 0,
        },
        "Altre_donazioni": {
            "Maschi": 0,
            "Femmine": 0,
            "Totale": 0,
        },
    }

    donazioni_no_data_rilascio_tessera = 0
    donazioni_no_data_nascita = 0
    for donazione in qs:
        donatore = donazione.donatore
        anno_tesseramento = 1900
        if (
            donatore.data_rilascio_tessera
            and donatore.data_rilascio_tessera.year > 1901
        ):
            anno_tesseramento = donatore.data_rilascio_tessera.year
        else:
            donazioni_no_data_rilascio_tessera += 1

        # statistiche per tipo socio, sesso, eta
        soci_key = "Soci_Donatori"
        if anno_tesseramento >= anno:
            soci_key = "Soci_Nuovi_Iscritti"
        elif not donatore.stato_donatore.is_attivo:
            soci_key = "Soci_Non_Donatori"

        sesso_key = "Maschi"
        if donatore.sesso.codice == "F":
            sesso_key = "Femmine"

        eta_key = "N_D"
        if donatore.data_nascita and donatore.data_nascita.year > 1901:
            anno_nascita = donatore.data_nascita.year
            eta = anno - anno_nascita
            if 18 <= eta <= 25:
                eta_key = "18_25"
            elif 26 <= eta <= 35:
                eta_key = "26_35"
            elif 36 <= eta <= 45:
                eta_key = "36_45"
            elif 46 <= eta <= 55:
                eta_key = "46_55"
            elif 56 <= eta <= 65:
                eta_key = "56_65"
            elif eta > 65:
                eta_key = "Oltre_65"
        else:
            donazioni_no_data_nascita += 1

        # incremento il totale per tipo soci, sesso, eta
        stats[soci_key][sesso_key][eta_key] += 1
        # incremento il totale per tipo soci, sesso
        stats[soci_key][sesso_key]["Totale"] += 1
        # incremento il totale per tipo soci
        stats[soci_key]["Totale"] += 1

        # statistiche per gruppo sanguigno
        gruppo_key = "N_D"
        if donatore.gruppo_sanguigno == "0" and donatore.rh == "+":
            gruppo_key = "0_RHp"
        elif donatore.gruppo_sanguigno == "0" and donatore.rh == "-":
            gruppo_key = "0_RHn"
        elif donatore.gruppo_sanguigno == "A" and donatore.rh == "+":
            gruppo_key = "A_RHp"
        elif donatore.gruppo_sanguigno == "A" and donatore.rh == "-":
            gruppo_key = "A_RHn"
        elif donatore.gruppo_sanguigno == "B" and donatore.rh == "+":
            gruppo_key = "B_RHp"
        elif donatore.gruppo_sanguigno == "B" and donatore.rh == "-":
            gruppo_key = "B_RHn"
        elif donatore.gruppo_sanguigno == "AB" and donatore.rh == "+":
            gruppo_key = "AB_RHp"
        elif donatore.gruppo_sanguigno == "AB" and donatore.rh == "-":
            gruppo_key = "AB_RHn"

        stats_gruppo[gruppo_key] += 1
        stats_gruppo["Totale"] += 1

        # statistiche per tipo donazione, sesso
        tipo_key = "Altre_donazioni"
        if donazione.tipo_donazione == Donazione.TipoDonazione.SANGUE_INTERO:
            tipo_key = "Sangue_Intero"
        elif donazione.tipo_donazione == Donazione.TipoDonazione.PLASMA:
            tipo_key = "Plasmaferesi"

        stats_tipo[tipo_key][sesso_key] += 1
        stats_tipo[tipo_key]["Totale"] += 1

    # num. soci_donatori attivi senza donazioni nell'anno
    donatori_attivi_qs = Donatore.objects.select_related("stato_donatore").filter(
        sezione__utente=user,
        stato_donatore__is_attivo=True,
    )
    donatori_attivi = donatori_attivi_qs.count()

    donatori_con_donazioni_qs = (
        donatori_attivi_qs.prefetch_related("donazioni")
        .filter(
            donazioni__data_donazione__year=anno,
        )
        .annotate(num_donazioni=Count("donazioni"))
    )
    donatori_con_donazioni = donatori_con_donazioni_qs.count()

    return {
        "count": qs.count(),
        "stats": stats,
        "stats_gruppo": stats_gruppo,
        "stats_tipo": stats_tipo,
        "donazioni_no_data_rilascio_tessera": donazioni_no_data_rilascio_tessera,
        "donazioni_no_data_nascita": donazioni_no_data_nascita,
        "donatori_attivi_senza_donazioni": donatori_attivi - donatori_con_donazioni,
    }


def get_elenco_soci_xls(user) -> Workbook:
    qs = (
        Donatore.objects.select_related("sezione", "stato_donatore")
        .filter(
            sezione__utente=user,
            stato_donatore__can_export_elenco_soci_xls=True,
        )
        .order_by("stato_donatore__pk", "cognome", "nome")
    )

    wb = Workbook()

    ws = wb.active  # grab the active worksheet
    ws.title = "Elenco soci"
    ws.append(
        [
            "COGNOME",
            "NOME",
            "LUOGO DI NASCITA",
            "DATA DI NASCITA",
            "CODICE FISCALE",
            "INDIRIZZO DI RESIDENZA",
            "COMUNE",
            "CAP",
            "NAZIONALITA'",
            "DATA DI ISCRIZIONE",
            "TIPOLOGIA DI SOCIO",
            "DATA CESSATA ISCRIZIONE",
            "CAUSA CESSATA ISCRIZIONE",
            "TELEFONO",
            "INDIRIZZO MAIL",
            "Provinciale",
            "Comunale",
        ]
    )
    for donatore in qs:
        indirizzo = (
            donatore.indirizzo + f" Fraz. {donatore.frazione}"
            if donatore.frazione
            else donatore.indirizzo
        )
        telefono = donatore.cellulare if donatore.cellulare else donatore.telefono
        tipologia = "DONATORE"
        if not donatore.stato_donatore.is_attivo:
            tipologia = "EX DONATORE"

        ws.append(
            [
                donatore.cognome,
                donatore.nome,
                donatore.luogo_nascita,
                donatore.data_nascita.strftime("%d/%m/%Y")
                if donatore.data_nascita
                else "",
                donatore.codice_fiscale,
                indirizzo,
                donatore.comune,
                donatore.cap,
                "",  # NAZIONALITA'
                donatore.data_iscrizione.strftime("%d/%m/%Y")
                if donatore.data_iscrizione
                else "",
                tipologia,
                donatore.data_cessata_iscrizione.strftime("%d/%m/%Y")
                if donatore.data_cessata_iscrizione
                else "",
                donatore.causa_cessata_iscrizione,
                telefono,
                donatore.email,
                "",  # Provinciale
                "",  # Comunale
            ]
        )
    return wb
