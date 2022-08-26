import datetime

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView

from .models import Donatore, Donazione, Sesso, Sezione, StatoDonatore


def avis_user_check(user):
    return user.is_staff


@require_GET
@user_passes_test(avis_user_check)
def index(request):
    return render(request, 'avis/index.html')


@method_decorator(user_passes_test(avis_user_check), name='dispatch')
class DonatoreListView(ListView):
    paginate_by = 10
    model = Donatore

    extra_context = {}

    def get_template_names(self):
        stampa = self.request.GET.get('stampa')
        if stampa in ('benemerenze', 'etichette'):
            return [f'avis/donatore_list_{stampa}.html']
        else:
            return super().get_template_names()

    def get_paginate_by(self, queryset):
        stampa = self.request.GET.get('stampa')
        if stampa:
            return 0
        default_paginate_by = super().get_paginate_by(queryset)
        paginate_by = self.request.GET.get('paginate_by', '')
        return paginate_by if paginate_by.isdigit() else default_paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sessi = Sesso.objects.all()
        sezioni = Sezione.objects.filter(utente=self.request.user)
        stati_donatore = StatoDonatore.objects.filter(
            Q(sezione__utente__isnull=True) | Q(sezione__utente=self.request.user)
        )

        get_copy = self.request.GET.copy()
        querystring = get_copy.pop('page', True) and get_copy.urlencode()
        skip_etichette = self.request.GET.get('skip_etichette', '0')
        if skip_etichette:
            skip_etichette = int(skip_etichette)

        context.update(
            {
                **self.extra_context,
                'sessi': sessi,
                'sezioni': sezioni,
                'stati_donatore': stati_donatore,
                'querystring': querystring,
                'skip_etichette_list': range(skip_etichette),
            }
        )

        return context

    def get_queryset(self):
        qs = super().get_queryset()

        donatore_id = self.request.GET.get('donatore_id', None)
        ricerca = self.request.GET.get('ricerca', None)
        sezione_id = self.request.GET.get('sezione_id', None)
        if sezione_id:
            sezione_id = int(sezione_id)
        stato_donatore_id = self.request.GET.get('stato_donatore_id', None)
        if stato_donatore_id:
            stato_donatore_id = int(stato_donatore_id)
        if 'stato_donatore_id' not in self.request.GET:
            stato_donatore_id = StatoDonatore.objects.filter(codice='Attivo').first().pk
        sesso_id = self.request.GET.get('sesso_id', None)
        if sesso_id:
            sesso_id = int(sesso_id)
        data_nascita_dal = self.request.GET.get('data_nascita_dal', '')
        if data_nascita_dal:
            data_nascita_dal = datetime.date.fromisoformat(data_nascita_dal)
        data_nascita_al = self.request.GET.get('data_nascita_al', '')
        if data_nascita_al:
            data_nascita_al = datetime.date.fromisoformat(data_nascita_al)
        data_iscrizione_dal = self.request.GET.get('data_iscrizione_dal', '')
        if data_iscrizione_dal:
            data_iscrizione_dal = datetime.date.fromisoformat(data_iscrizione_dal)
        data_iscrizione_al = self.request.GET.get('data_iscrizione_al', '')
        if data_iscrizione_al:
            data_iscrizione_al = datetime.date.fromisoformat(data_iscrizione_al)
        gruppo_sanguigno = self.request.GET.get('gruppo_sanguigno', None)
        rh = self.request.GET.get('rh', None)
        fenotipo = self.request.GET.get('fenotipo', None)
        kell = self.request.GET.get('kell', None)
        data_donazione_dal = self.request.GET.get('data_donazione_dal', None)
        if data_donazione_dal:
            data_donazione_dal = datetime.date.fromisoformat(data_donazione_dal)
        data_donazione_al = self.request.GET.get('data_donazione_al', None)
        if data_donazione_al:
            data_donazione_al = datetime.date.fromisoformat(data_donazione_al)
        cap = self.request.GET.get('cap', None)
        cap_diverso = self.request.GET.get('cap_diverso', None)
        comune = self.request.GET.get('comune', None)
        provincia = self.request.GET.get('provincia', None)
        show_n_donazioni = self.request.GET.get('show_n_donazioni', None)
        if show_n_donazioni:
            show_n_donazioni = int(show_n_donazioni)

        qs = (
            qs.select_related('sesso', 'sezione', 'stato_donatore')
            .prefetch_related(
                Prefetch(
                    'donazioni',
                    queryset=Donazione.objects.order_by('-data_donazione'),
                ),
            )
            .filter(sezione__utente=self.request.user)
            .order_by('cognome', 'nome')
        )

        if donatore_id:
            qs = qs.filter(id=donatore_id)
        if ricerca:
            qs = qs.filter(
                Q(num_tessera__icontains=ricerca)
                | Q(cognome__icontains=ricerca)
                | Q(nome__icontains=ricerca)
            )
        if sezione_id:
            qs = qs.filter(sezione_id=sezione_id)
        if stato_donatore_id:
            qs = qs.filter(stato_donatore_id=stato_donatore_id)
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
        if cap:
            qs = qs.filter(cap__icontains=cap)
        if cap_diverso:
            qs = qs.exclude(cap__icontains=cap_diverso)
        if comune:
            qs = qs.filter(comune__iexact=comune)
        if provincia:
            qs = qs.filter(provincia__iexact=provincia)

        qs = qs.annotate(
            num_donazioni=Count('donazioni'),
            tot_donazioni=Count('donazioni') + F('donazioni_pregresse'),
        )

        page = self.request.GET.get('page', 1)
        paginate_by = self.get_paginate_by(qs)
        page_range = None
        if paginate_by:
            page_range = self.get_paginator(qs, paginate_by).get_elided_page_range(
                number=page
            )

        self.extra_context = {
            'ricerca': ricerca or '',
            'sezione_id': sezione_id or '',
            'stato_donatore_id': stato_donatore_id or '',
            'sesso_id': sesso_id or '',
            'data_nascita_dal': data_nascita_dal.isoformat()
            if data_nascita_dal
            else '',
            'data_nascita_al': data_nascita_al.isoformat() if data_nascita_al else '',
            'data_iscrizione_dal': data_iscrizione_dal.isoformat()
            if data_iscrizione_dal
            else '',
            'data_iscrizione_al': data_iscrizione_al.isoformat()
            if data_iscrizione_al
            else '',
            'gruppo_sanguigno': gruppo_sanguigno or '',
            'rh': rh or '',
            'fenotipo': fenotipo or '',
            'kell': kell or '',
            'data_donazione_dal': data_donazione_dal.isoformat()
            if data_donazione_dal
            else '',
            'data_donazione_al': data_donazione_al.isoformat()
            if data_donazione_al
            else '',
            'cap': cap or '',
            'cap_diverso': cap_diverso or '',
            'comune': comune or '',
            'provincia': provincia or '',
            'show_n_donazioni': show_n_donazioni or 0,
            'show_advanced': bool(
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
                or comune
                or provincia
                or cap
                or cap_diverso
            ),
            'paginate_by': paginate_by,
            'page_range': page_range,
        }

        return qs


@method_decorator(user_passes_test(avis_user_check), name='dispatch')
class DonatoreDetailView(DetailView):
    model = Donatore

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('sesso', 'sezione', 'stato_donatore').prefetch_related(
            Prefetch(
                'donazioni',
                queryset=Donazione.objects.order_by('-data_donazione'),
            ),
        )
        return qs
