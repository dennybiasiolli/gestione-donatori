import json
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q

from avis.models import Donatore, Donazione, Sesso, Sezione, StatoDonatore

User = get_user_model()


class Command(BaseCommand):
    help = 'Importa i vecchi dati dotnet nel gestionale'

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--dir',
            type=str,
            required=True,
            help='path containing files to import',
        )

    def _read_json(self, path):
        with open(path) as f:
            return json.load(f)

    def _date_from_string_or_none(self, str_datetime):
        return str_datetime[:10] if str_datetime else None

    def handle(self, *args, **options):
        user = User.objects.filter(is_superuser=True).first()

        # import sezioni
        sezioni = self._read_json(os.path.join(options['dir'], 'sezioni.json'))

        sezione = Sezione.objects.filter(
            descrizione=sezioni[0]['Descrizione']
        ).first()
        if sezione is None:
            sezione = Sezione.objects.create(
                utente=user,
                descrizione=sezioni[0]['Descrizione'],
                indirizzo=sezioni[0]['Indirizzo'],
                cap=sezioni[0]['Cap'],
                comune=sezioni[0]['Comune'],
                provincia=sezioni[0]['Provincia'],
                telefono=sezioni[0]['Tel'],
                fax=sezioni[0]['Fax'],
                email=sezioni[0]['Email'],
                presidente=sezioni[0]['Presidente'],
                segretario=sezioni[0]['Segretario'],
            )

        # import stati donatori
        stati = self._read_json(
            os.path.join(options['dir'], 'statiDonatori.json')
        )
        for stato in stati:
            stato_donatore = StatoDonatore.objects.filter(
                # utente=user,
                codice=stato['Descrizione'],
            ).first()
            if stato_donatore is None:
                stato_donatore = StatoDonatore.objects.create(
                    sezione=sezione,
                    codice=stato['Descrizione'],
                    descrizione=stato['DescrizioneEstesa'],
                    is_attivo=stato['Attivo'],
                )

        stati_donatore = StatoDonatore.objects.filter(
            Q(sezione__isnull=True) | Q(sezione=sezione)
        ).values('id', 'codice')

        # import donatori
        donatori = self._read_json(
            os.path.join(options['dir'], 'donatori.json')
        )
        sesso_m = Sesso.objects.filter(codice='M').first()
        sesso_f = Sesso.objects.filter(codice='F').first()
        for d in donatori:
            donatore = Donatore.objects.filter(
                sezione=sezione,
                num_tessera=d['NumTessera'],
            ).first()
            if donatore is None:
                sesso = d.get('Sesso', {}) or {}
                sesso = sesso.get('Descrizione', 'F')
                sesso = sesso_f if sesso == 'F' else sesso_m
                donatore = Donatore.objects.create(
                    sezione=sezione,
                    num_tessera=d['NumTessera'],
                    cognome=d['Cognome'],
                    nome=d['Nome'],
                    sesso=sesso,
                    stato_donatore_id=stati_donatore.filter(
                        codice=d['StatoDonatore']['Descrizione']
                    ).first()['id'],
                    num_tessera_cartacea=d['NumTesseraCartacea'] or '',
                    data_rilascio_tessera=self._date_from_string_or_none(
                        d['DataRilascioTessera']
                    ),
                    codice_fiscale='',
                    data_nascita=self._date_from_string_or_none(
                        d['DataNascita']
                    ),
                    data_iscrizione=self._date_from_string_or_none(
                        d['DataIscrizione']
                    ),
                    gruppo_sanguigno=d['GruppoSanguigno'],
                    rh=d['Rh'],
                    fenotipo=d['Fenotipo'],
                    kell=d['Kell'],
                    indirizzo=d['Indirizzo'],
                    frazione=d['Frazione'],
                    cap=d['Cap'],
                    comune=d['Comune'],
                    provincia=d['Provincia'],
                    telefono=d['Telefono'],
                    telefono_lavoro=d['TelefonoLavoro'],
                    cellulare=d['Cellulare'],
                    fax='',
                    email=d['Email'],
                    fermo_per_malattia=d['FermoPerMalattia'],
                    donazioni_pregresse=d['DonazioniPregresse'],
                    num_benemerenze=d['NumBenemerenze'],
                )

            # import donazioni
            donazioni = sorted(
                d['donazioni'], key=lambda k: k['DataDonazione']
            )
            for donazione in donazioni:
                tipo_donazione = donazione.get('TipoDonazione', {}) or {}
                tipo_donazione = tipo_donazione.get('Descrizione', None)
                if tipo_donazione == 'Sangue intero':
                    tipo_donazione = Donazione.TipoDonazione.SANGUE_INTERO
                elif tipo_donazione == 'Plasma':
                    tipo_donazione = Donazione.TipoDonazione.PLASMA
                elif tipo_donazione == 'Piastrine':
                    tipo_donazione = Donazione.TipoDonazione.PIASTRINE
                elif tipo_donazione is None:
                    tipo_donazione = None
                else:
                    print(tipo_donazione)
                    raise tipo_donazione
                try:
                    Donazione.objects.create(
                        donatore=donatore,
                        tipo_donazione=tipo_donazione,
                        data_donazione=self._date_from_string_or_none(
                            donazione['DataDonazione']
                        ),
                    )
                except Exception:
                    print(
                        donatore,
                        '\n',
                        '\t',
                        self._date_from_string_or_none(
                            donazione['DataDonazione']
                        ),
                        # err,
                    )
                    raise

        self.stdout.write('Importazione donatori completata con successo')
