from datetime import timedelta

from django.db.models import OuterRef, Prefetch, Subquery
from django.utils import timezone

from .models import CallLog, Donatore, Donazione

# Eritro types have no dedicated Sesso interval fields; treat them as whole blood.
FOCUS_TYPES = (
    Donazione.TipoDonazione.SANGUE_INTERO,
    Donazione.TipoDonazione.PLASMA,
    Donazione.TipoDonazione.ERITRO_PLASMAFERESI,
    Donazione.TipoDonazione.ERITROCITI,
)

ORDER_PROSSIMA = "prossima"
ORDER_DONATORE = "donatore"
ORDER_ULTIMA = "ultima"
ALLOWED_ORDER_BY = (ORDER_PROSSIMA, ORDER_DONATORE, ORDER_ULTIMA)
ORDER_ASC = ""
ORDER_DESC = "-"
ALLOWED_ORDER_DIRECTIONS = (ORDER_ASC, ORDER_DESC)
ULTIMO_MAI = "mai"
ALLOWED_ULTIMO = ("", ULTIMO_MAI) + tuple(CallLog.Result.values)


def interval_kind(tipo_donazione):
    if tipo_donazione == Donazione.TipoDonazione.PLASMA:
        return "plasma"
    return "sangue"


def next_eligible_date(sesso, last_date, last_type, focus_type, today=None):
    today = today or timezone.localdate()
    if last_date is None:
        return today
    days = getattr(
        sesso,
        f"gg_da_{interval_kind(last_type)}_a_{interval_kind(focus_type)}",
    )
    return last_date + timedelta(days=days)


def parse_focus_type(value):
    try:
        focus_type = int(value)
    except (TypeError, ValueError):
        return Donazione.TipoDonazione.SANGUE_INTERO
    if focus_type in FOCUS_TYPES:
        return focus_type
    return Donazione.TipoDonazione.SANGUE_INTERO


def parse_order_by(value):
    if value in ALLOWED_ORDER_BY:
        return value
    return ORDER_PROSSIMA


def parse_order_direction(value):
    if value in ALLOWED_ORDER_DIRECTIONS:
        return value
    return ORDER_ASC


DEFAULT_HIDE_DAYS = 1
MAX_HIDE_DAYS = 365


def parse_ultimo(value):
    if value in ALLOWED_ULTIMO:
        return value
    return ""


def parse_hide_days(value):
    if value in (None, ""):
        return DEFAULT_HIDE_DAYS
    try:
        days = int(value)
    except (TypeError, ValueError):
        return DEFAULT_HIDE_DAYS
    return max(0, min(days, MAX_HIDE_DAYS))


def called_within_days(last_call, days, today=None):
    if days <= 0 or last_call is None or last_call.result != CallLog.Result.CALLED:
        return False
    today = today or timezone.localdate()
    call_date = timezone.localtime(last_call.created_at).date()
    return (today - call_date).days < days


def exclude_called_recently(rows, days, today=None):
    today = today or timezone.localdate()
    visible = []
    hidden = 0
    for row in rows:
        if called_within_days(row["last_call"], days, today):
            hidden += 1
        else:
            visible.append(row)
    return visible, hidden


def _sort_key(row, order_by):
    donatore = row["donatore"]
    if order_by == ORDER_DONATORE:
        return (donatore.cognome.lower(), donatore.nome.lower())
    if order_by == ORDER_ULTIMA:
        return (
            row["ultima_data"] is None,
            row["ultima_data"] or timezone.localdate(),
            donatore.cognome.lower(),
            donatore.nome.lower(),
        )
    return (
        row["next_date"],
        donatore.cognome.lower(),
        donatore.nome.lower(),
    )


def eligible_today(
    user,
    focus_type,
    *,
    gruppo="",
    rh="",
    ultimo="",
    order_by=ORDER_PROSSIMA,
    order_direction=ORDER_ASC,
    today=None,
):
    today = today or timezone.localdate()
    last = Donazione.objects.filter(donatore_id=OuterRef("pk")).order_by(
        "-data_donazione"
    )
    qs = (
        Donatore.objects.filter(
            sezione__utente=user,
            stato_donatore__is_attivo=True,
            fermo_per_malattia=False,
        )
        .select_related("sesso", "stato_donatore")
        .annotate(
            ultima_data=Subquery(last.values("data_donazione")[:1]),
            ultima_tipo=Subquery(last.values("tipo_donazione")[:1]),
        )
        .prefetch_related(
            Prefetch(
                "call_logs",
                queryset=CallLog.objects.order_by("-created_at"),
                to_attr="recent_calls",
            )
        )
        .order_by("cognome", "nome")
    )
    if gruppo:
        qs = qs.filter(gruppo_sanguigno=gruppo)
    if rh:
        qs = qs.filter(rh=rh)

    rows = []
    for donatore in qs:
        next_date = next_eligible_date(
            donatore.sesso,
            donatore.ultima_data,
            donatore.ultima_tipo,
            focus_type,
            today=today,
        )
        if next_date > today:
            continue
        phone = donatore.cellulare or donatore.telefono
        last_call = donatore.recent_calls[0] if donatore.recent_calls else None
        ultima_tipo_display = ""
        if donatore.ultima_data:
            if donatore.ultima_tipo is None:
                ultima_tipo_display = Donazione.TipoDonazione.__empty__
            else:
                ultima_tipo_display = Donazione.TipoDonazione(
                    donatore.ultima_tipo
                ).label
        rows.append(
            {
                "donatore": donatore,
                "phone": phone,
                "ultima_data": donatore.ultima_data,
                "ultima_tipo_display": ultima_tipo_display,
                "next_date": next_date,
                "last_call": last_call,
            }
        )
    ultimo = parse_ultimo(ultimo)
    if ultimo == ULTIMO_MAI:
        rows = [row for row in rows if row["last_call"] is None]
    elif ultimo:
        rows = [
            row
            for row in rows
            if row["last_call"] is not None and row["last_call"].result == ultimo
        ]
    rows.sort(
        key=lambda row: _sort_key(row, parse_order_by(order_by)),
        reverse=parse_order_direction(order_direction) == ORDER_DESC,
    )
    return rows
