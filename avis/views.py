import datetime
import http
from typing import Any, Dict

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, F, Max, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from avis.forms import DonazioneForm

from .models import Donatore, Donazione, Sesso, Sezione, StatoDonatore


def avis_user_check(user):
    return user.is_staff


@require_GET
@user_passes_test(avis_user_check)
def index(request):
    return redirect("donatori")


@method_decorator(user_passes_test(avis_user_check), name="dispatch")
class DonatoreListView(ListView):
    paginate_by = 10
    model = Donatore

    extra_context = {}

    def get_template_names(self):
        stampa = self.request.GET.get("stampa")
        if stampa in ("elenco", "benemerenze", "emails", "etichette"):
            return [f"avis/donatore_list_{stampa}.html"]
        else:
            return super().get_template_names()

    def get_paginate_by(self, queryset):
        stampa = self.request.GET.get("stampa")
        if stampa:
            return 0
        default_paginate_by = super().get_paginate_by(queryset)
        paginate_by = self.request.GET.get("paginate_by", "")
        return paginate_by if paginate_by.isdigit() else default_paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sessi = Sesso.objects.all()
        sezioni = Sezione.objects.filter(utente=self.request.user)
        stati_donatore = StatoDonatore.objects.filter(
            Q(sezione__utente__isnull=True) | Q(sezione__utente=self.request.user)
        )

        get_copy = self.request.GET.copy()
        querystring = get_copy.pop("page", True) and get_copy.urlencode()
        skip_etichette = self.request.GET.get("skip_etichette", "0")
        if skip_etichette:
            skip_etichette = int(skip_etichette)

        context.update(
            {
                **self.extra_context,
                "sessi": sessi,
                "sezioni": sezioni,
                "stati_donatore": stati_donatore,
                "querystring": querystring,
                "skip_etichette_list": range(skip_etichette),
            }
        )

        return context

    def get_queryset(self):
        qs = super().get_queryset()

        donatore_id = self.request.GET.get("donatore_id", None)
        ricerca = self.request.GET.get("ricerca", None)
        sezione_id = self.request.GET.get("sezione_id", None)
        if sezione_id:
            sezione_id = int(sezione_id)
        stato_donatore_ids = self.request.GET.getlist("stato_donatore_ids", None)
        if stato_donatore_ids:
            stato_donatore_ids = [
                int(stato_donatore_id) for stato_donatore_id in stato_donatore_ids
            ]
        if "stato_donatore_ids" not in self.request.GET:
            stato_donatore_ids = [
                StatoDonatore.objects.filter(codice="Attivo").first().pk
            ]
        sesso_id = self.request.GET.get("sesso_id", None)
        if sesso_id:
            sesso_id = int(sesso_id)
        data_nascita_dal = self.request.GET.get("data_nascita_dal", "")
        if data_nascita_dal:
            data_nascita_dal = datetime.date.fromisoformat(data_nascita_dal)
        data_nascita_al = self.request.GET.get("data_nascita_al", "")
        if data_nascita_al:
            data_nascita_al = datetime.date.fromisoformat(data_nascita_al)
        data_iscrizione_dal = self.request.GET.get("data_iscrizione_dal", "")
        if data_iscrizione_dal:
            data_iscrizione_dal = datetime.date.fromisoformat(data_iscrizione_dal)
        data_iscrizione_al = self.request.GET.get("data_iscrizione_al", "")
        if data_iscrizione_al:
            data_iscrizione_al = datetime.date.fromisoformat(data_iscrizione_al)
        gruppo_sanguigno = self.request.GET.get("gruppo_sanguigno", None)
        rh = self.request.GET.get("rh", None)
        fenotipo = self.request.GET.get("fenotipo", None)
        kell = self.request.GET.get("kell", None)
        data_donazione_dal = self.request.GET.get("data_donazione_dal", None)
        if data_donazione_dal:
            data_donazione_dal = datetime.date.fromisoformat(data_donazione_dal)
        data_donazione_al = self.request.GET.get("data_donazione_al", None)
        if data_donazione_al:
            data_donazione_al = datetime.date.fromisoformat(data_donazione_al)
        benemerenze_da = self.request.GET.get("benemerenze_da", None)
        if benemerenze_da:
            benemerenze_da = int(benemerenze_da)
        benemerenze_a = self.request.GET.get("benemerenze_a", None)
        if benemerenze_a:
            benemerenze_a = int(benemerenze_a)
        cap = self.request.GET.get("cap", None)
        cap_diverso = self.request.GET.get("cap_diverso", None)
        filter_donatori = self.request.GET.get("filter_donatori", "")
        comune = self.request.GET.get("comune", None)
        provincia = self.request.GET.get("provincia", None)
        show_n_donazioni = self.request.GET.get("show_n_donazioni", None)
        if show_n_donazioni:
            show_n_donazioni = int(show_n_donazioni)
        order_by_str = self.request.GET.get("order_by", "cognome,nome")
        order_by_direction = self.request.GET.get("order_by_direction", "")
        only_stampa = self.request.GET.get("only_stampa", "0") == "1"
        order_by = list(map(lambda o: order_by_direction + o, order_by_str.split(",")))
        if "cognome" not in order_by:
            order_by.append("cognome")
            order_by.append("nome")

        qs = (
            qs.select_related("sesso", "sezione", "stato_donatore")
            .prefetch_related(
                Prefetch(
                    "donazioni",
                    queryset=Donazione.objects.order_by("-data_donazione"),
                ),
            )
            .filter(sezione__utente=self.request.user)
        )

        if donatore_id:
            qs = qs.filter(id=donatore_id)
        if ricerca:
            qs = qs.filter(
                # pylint: disable=unsupported-binary-operation
                Q(num_tessera_avis__icontains=ricerca)
                | Q(num_tessera_ct__icontains=ricerca)
                | Q(cognome__icontains=ricerca)
                | Q(nome__icontains=ricerca)
                # pylint: enable=unsupported-binary-operation
            )
        if sezione_id:
            qs = qs.filter(sezione_id=sezione_id)
        if stato_donatore_ids:
            qs = qs.filter(stato_donatore_id__in=stato_donatore_ids)
        if sesso_id:
            qs = qs.filter(sesso_id=sesso_id)
        if data_nascita_dal:
            qs = qs.filter(data_nascita__gte=data_nascita_dal)
        if data_nascita_al:
            qs = qs.filter(data_nascita__lte=data_nascita_al)
        if data_iscrizione_dal:
            qs = qs.filter(data_iscrizione__gte=data_iscrizione_dal)
        if data_iscrizione_al:
            qs = qs.filter(data_iscrizione__lte=data_iscrizione_al)
        if gruppo_sanguigno:
            qs = qs.filter(gruppo_sanguigno=gruppo_sanguigno)
        if rh:
            qs = qs.filter(rh=rh)
        if fenotipo:
            qs = qs.filter(fenotipo=fenotipo)
        if kell:
            qs = qs.filter(kell=kell)
        if data_donazione_dal:
            qs = qs.filter(donazioni__data_donazione__gte=data_donazione_dal)
        if data_donazione_al:
            qs = qs.filter(donazioni__data_donazione__lte=data_donazione_al)
        if benemerenze_da:
            qs = qs.filter(num_benemerenze__gte=benemerenze_da)
        if benemerenze_a:
            qs = qs.filter(num_benemerenze__lte=benemerenze_a)
        if cap:
            qs = qs.filter(cap__icontains=cap)
        if cap_diverso:
            qs = qs.exclude(cap__icontains=cap_diverso)
        if filter_donatori == "email":
            qs = qs.exclude(email="")
        elif filter_donatori == "no_email":
            qs = qs.filter(email="")
        elif filter_donatori == "cell":
            qs = qs.exclude(cellulare="")
        elif filter_donatori == "no_cell":
            qs = qs.filter(cellulare="")
        if comune:
            qs = qs.filter(comune__iexact=comune)
        if provincia:
            qs = qs.filter(provincia__iexact=provincia)
        if only_stampa:
            qs = qs.filter(stampa_donatore=True)

        qs = qs.annotate(
            num_donazioni=Count("donazioni"),
            tot_donazioni=Count("donazioni") + F("donazioni_pregresse"),
            ultima_donazione=Max("donazioni__data_donazione"),
        )
        qs = qs.order_by(*order_by)

        page = self.request.GET.get("page", 1)
        paginate_by = self.get_paginate_by(qs)
        page_range = None
        if paginate_by:
            page_range = self.get_paginator(qs, paginate_by).get_elided_page_range(
                number=page
            )

        self.extra_context = {
            "ricerca": ricerca or "",
            "sezione_id": sezione_id or "",
            "stato_donatore_ids": stato_donatore_ids or [],
            "sesso_id": sesso_id or "",
            "data_nascita_dal": data_nascita_dal.isoformat()
            if data_nascita_dal
            else "",
            "data_nascita_al": data_nascita_al.isoformat() if data_nascita_al else "",
            "data_iscrizione_dal": data_iscrizione_dal.isoformat()
            if data_iscrizione_dal
            else "",
            "data_iscrizione_al": data_iscrizione_al.isoformat()
            if data_iscrizione_al
            else "",
            "gruppo_sanguigno": gruppo_sanguigno or "",
            "rh": rh or "",
            "fenotipo": fenotipo or "",
            "kell": kell or "",
            "data_donazione_dal": data_donazione_dal.isoformat()
            if data_donazione_dal
            else "",
            "data_donazione_al": data_donazione_al.isoformat()
            if data_donazione_al
            else "",
            "benemerenze_da": benemerenze_da if benemerenze_da else "",
            "benemerenze_a": benemerenze_a if benemerenze_a else "",
            "cap": cap or "",
            "cap_diverso": cap_diverso or "",
            "filter_donatori": filter_donatori or "",
            "comune": comune or "",
            "provincia": provincia or "",
            "show_n_donazioni": show_n_donazioni or 0,
            "show_advanced": bool(
                data_iscrizione_dal
                or data_iscrizione_al
                or data_nascita_dal
                or data_nascita_al
                or gruppo_sanguigno
                or rh
                or fenotipo
                or kell
                or data_donazione_dal
                or data_donazione_al
                or benemerenze_da
                or benemerenze_a
                or comune
                or provincia
                or cap
                or cap_diverso
                or filter_donatori
            ),
            "paginate_by": paginate_by,
            "page_range": page_range,
            "order_by": order_by_str,
            "order_by_direction": order_by_direction,
            "only_stampa": "1" if only_stampa else "",
        }

        return qs


@method_decorator(user_passes_test(avis_user_check), name="dispatch")
class DonatoreDetailView(DetailView):
    model = Donatore

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related("sesso", "sezione", "stato_donatore").prefetch_related(
            Prefetch(
                "donazioni",
                queryset=Donazione.objects.order_by("-data_donazione"),
            ),
        )
        return qs


@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(avis_user_check)
def donatore_add_stampa(request, pk):
    donatore = get_object_or_404(Donatore, pk=pk)
    donatore.stampa_donatore = True
    donatore.save()
    return HttpResponse(status=http.HTTPStatus.NO_CONTENT)


@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(avis_user_check)
def donatore_remove_stampa(request, pk=None):
    if pk:
        donatore = get_object_or_404(Donatore, pk=pk)
        donatore.stampa_donatore = False
        donatore.save()
        return HttpResponse(status=http.HTTPStatus.NO_CONTENT)
    else:
        Donatore.objects.filter(stampa_donatore=True).update(stampa_donatore=False)
        return redirect("donatori")


@method_decorator(user_passes_test(avis_user_check), name="dispatch")
class DonazioneCreateView(CreateView):
    model = Donazione
    form_class = DonazioneForm

    def get_success_url(self) -> str:
        return reverse_lazy("donatore", kwargs={"pk": self.object.donatore.pk})

    def get_initial(self) -> Dict[str, Any]:
        return {
            "donatore": self.kwargs["pk"],
            "tipo_donazione": Donazione.TipoDonazione.SANGUE_INTERO,
            "data_donazione": datetime.date.today(),
        }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        donatore = get_object_or_404(Donatore, pk=self.kwargs["pk"])
        context_data.update(
            {
                "donatore": donatore,
            }
        )
        return context_data


@csrf_exempt
@require_http_methods(["GET"])
@user_passes_test(avis_user_check)
def dati_statistici(request):
    anno = int(request.GET.get("anno", datetime.date.today().year - 1))
    qs = Donazione.objects.select_related(
        "donatore", "donatore__sesso", "donatore__sezione", "donatore__stato_donatore"
    ).filter(donatore__sezione__utente=request.user, data_donazione__year=anno)

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
        if donatore.data_rilascio_tessera:
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
        if donazione.donatore.data_nascita:
            anno_nascita = donazione.donatore.data_nascita.year
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

    # num. soci_donatori senza donazioni nell'anno

    context = {
        "anno": anno,
        "count": qs.count(),
        "stats": stats,
        "stats_gruppo": stats_gruppo,
        "stats_tipo": stats_tipo,
        "donazioni_no_data_rilascio_tessera": donazioni_no_data_rilascio_tessera,
        "donazioni_no_data_nascita": donazioni_no_data_nascita,
    }

    return render(request, "avis/dati_statistici.html", context)
