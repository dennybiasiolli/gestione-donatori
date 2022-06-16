# Gestione Donatori


## Setup progetto

- Clona il progetto in locale

    `git clone git@github.com:dennybiasiolli/gestione-donatori.git`

- Entra nella directory del progetto

    `cd gestione-donatori`

- Crea un ambiente virtuale per questa installazione (Python 3.10.x consigliato)

    `python -m venv venv`

- Attiva l'ambiente virtuale (da ripetere ogni volta che si lavora sul repository)

    `source venv/bin/activate`

- Installa le dipendenze richieste per il progetto

    ```
    pip install --upgrade pip
    pip install -r requirements_dev.txt
    ```

- Crea/aggiorna il database applicando le migrazioni necessarie

    Nota: in sviluppo viene utilizzato un DB SQLite e creato se non esiste,
    per PostgreSQL il database deve già essere presente, anche se vuoto.

    `python manage.py migrate`

- Creazione utente amministratore

    `python manage.py createsuperuser`

    e seguire le indicazioni

- (opzionale) Importazione dati da vecchia istanza gestionale

    `python manage.py avis_import_dotnet_data -d $DIRECTORY_DATI`

    `$DIRECTORY_DATI` deve essere la cartella in cui sono presenti i file JSON
    esportati dal vecchio gestionale

- Avviare localmente il server di sviluppo

    `python manage.py runserver`

- Accedere all'interfaccia di amministrazione

    Aprire da browser `http://localhost:8000/admin/` e accedere con le credenziali
    di amministratore create all'inizio


## Allineamento progetto alle ultime modifiche

- Aggiornare il branch `main` (assicurandosi di non avere modifiche in corso)

    ```
    git checkout main
    git pull
    ```

- Aggiornare il database locale all'ultima versione

    `python manage.py migrate`
