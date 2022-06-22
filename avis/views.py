import datetime

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404, render

from .models import Donatore, Donazione, Sesso, Sezione, StatoDonatore


def avis_user_check(user):
    return user.is_staff


@user_passes_test(avis_user_check)
def index(request):
    return render(request, 'avis/index.html')


@user_passes_test(avis_user_check)
def donatori(request):
    ricerca = request.GET.get('ricerca', None)
    sezione_id = request.GET.get('sezione_id', None)
    if sezione_id:
        sezione_id = int(sezione_id)
    stato_donatore_id = request.GET.get('stato_donatore_id', None)
    if stato_donatore_id:
        stato_donatore_id = int(stato_donatore_id)
    if 'stato_donatore_id' not in request.GET:
        stato_donatore_id = (
            StatoDonatore.objects.filter(codice='Attivo').first().pk
        )
    sesso_id = request.GET.get('sesso_id', None)
    if sesso_id:
        sesso_id = int(sesso_id)
    data_nascita_dal = request.GET.get('data_nascita_dal', None)
    if data_nascita_dal:
        data_nascita_dal = datetime.date.fromisoformat(data_nascita_dal)
    data_nascita_al = request.GET.get('data_nascita_al', None)
    if data_nascita_al:
        data_nascita_al = datetime.date.fromisoformat(data_nascita_al)
    data_iscrizione_dal = request.GET.get('data_iscrizione_dal', None)
    if data_iscrizione_dal:
        data_iscrizione_dal = datetime.date.fromisoformat(data_iscrizione_dal)
    data_iscrizione_al = request.GET.get('data_iscrizione_al', None)
    if data_iscrizione_al:
        data_iscrizione_al = datetime.date.fromisoformat(data_iscrizione_al)
    gruppo_sanguigno = request.GET.get('gruppo_sanguigno', None)
    rh = request.GET.get('rh', None)
    fenotipo = request.GET.get('fenotipo', None)
    kell = request.GET.get('kell', None)
    data_donazione_dal = request.GET.get('data_donazione_dal', None)
    if data_donazione_dal:
        data_donazione_dal = datetime.date.fromisoformat(data_donazione_dal)
    data_donazione_al = request.GET.get('data_donazione_al', None)
    if data_donazione_al:
        data_donazione_al = datetime.date.fromisoformat(data_donazione_al)
    cap = request.GET.get('cap', None)
    cap_diverso = request.GET.get('cap_diverso', None)
    comune = request.GET.get('comune', None)
    provincia = request.GET.get('provincia', None)
    show_n_donazioni = request.GET.get('show_n_donazioni', None)
    if show_n_donazioni:
        show_n_donazioni = int(show_n_donazioni)

    donatori = (
        Donatore.objects.all()
        .select_related('sesso', 'sezione', 'stato_donatore')
        .prefetch_related(
            Prefetch(
                'donazioni',
                queryset=Donazione.objects.order_by('-data_donazione'),
            ),
        )
        .filter(sezione__utente=request.user)
        .order_by('cognome', 'nome')
    )

    if ricerca:
        donatori = donatori.filter(
            Q(num_tessera__icontains=ricerca)
            | Q(cognome__icontains=ricerca)
            | Q(nome__icontains=ricerca)
        )
    if sezione_id:
        donatori = donatori.filter(sezione_id=sezione_id)
    if stato_donatore_id:
        donatori = donatori.filter(stato_donatore_id=stato_donatore_id)
    if sesso_id:
        donatori = donatori.filter(sesso_id=sesso_id)
    if data_nascita_dal:
        donatori = donatori.filter(data_nascita__gte=data_nascita_dal)
    if data_nascita_al:
        donatori = donatori.filter(data_nascita__lte=data_nascita_al)
    if data_iscrizione_dal:
        donatori = donatori.filter(data_iscrizione__gte=data_iscrizione_dal)
    if data_iscrizione_al:
        donatori = donatori.filter(data_iscrizione__lte=data_iscrizione_al)
    if gruppo_sanguigno:
        donatori = donatori.filter(gruppo_sanguigno=gruppo_sanguigno)
    if rh:
        donatori = donatori.filter(rh=rh)
    if fenotipo:
        donatori = donatori.filter(fenotipo=fenotipo)
    if kell:
        donatori = donatori.filter(kell=kell)
    if data_donazione_dal:
        donatori = donatori.filter(
            donazioni__data_donazione__gte=data_donazione_dal
        )
    if data_donazione_al:
        donatori = donatori.filter(
            donazioni__data_donazione__lte=data_donazione_al
        )
    if cap:
        donatori = donatori.filter(cap__icontains=cap)
    if cap_diverso:
        donatori = donatori.exclude(cap__icontains=cap_diverso)
    if comune:
        donatori = donatori.filter(comune__iexact=comune)
    if provincia:
        donatori = donatori.filter(provincia__iexact=provincia)

    donatori = donatori.annotate(
        num_donazioni=Count('donazioni'),
        tot_donazioni=Count('donazioni') + F('donazioni_pregresse'),
    )

    stati_donatore = StatoDonatore.objects.filter(
        Q(sezione__utente__isnull=True) | Q(sezione__utente=request.user)
    )

    return render(
        request,
        'avis/donatori.html',
        {
            'donatori': donatori,
            'sessi': Sesso.objects.all(),
            'sezioni': Sezione.objects.filter(utente=request.user),
            'stati_donatore': stati_donatore,
            'ricerca': ricerca or '',
            'sezione_id': sezione_id or '',
            'stato_donatore_id': stato_donatore_id or '',
            'sesso_id': sesso_id or '',
            'data_nascita_dal': data_nascita_dal.isoformat()
            if data_nascita_dal
            else '',
            'data_nascita_al': data_nascita_al.isoformat()
            if data_nascita_al
            else '',
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
        },
    )


@user_passes_test(avis_user_check)
def donatore(request, pk):
    donatore = get_object_or_404(Donatore, pk=pk)
    num_donazioni = donatore.donazioni.count()
    tot_donazioni = num_donazioni + donatore.donazioni_pregresse
    donazioni = donatore.donazioni.all().order_by('-data_donazione')
    return render(
        request,
        'avis/donatore.html',
        {
            'donatore': donatore,
            'num_donazioni': num_donazioni,
            'tot_donazioni': tot_donazioni,
            'donazioni': donazioni,
        },
    )
