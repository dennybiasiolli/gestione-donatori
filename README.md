# Gestione Donatori

![Django CI](https://github.com/dennybiasiolli/api-dennybiasiolli-com/actions/workflows/django.yml/badge.svg)


## Project setup

- Clone the repository and enter in its directory

    ```
    git clone git@github.com:dennybiasiolli/gestione-donatori.git
    cd gestione-donatori
    ```

- Get static libs (bootstrap, etc...)

    Note: ensure `unzip` is installed

    ```
    make get-static-libs:
    ```

- Create and enable a virtual environment for this project (Python 3.11)

- Install required packages

    `make requirements`

- Create/update database with migrations

    A SQLite database for debugging is created if not existent,
    PostgreSQL databases must be created before launching this command

    `python manage.py migrate`

- Loading default data

    `python manage.py loaddata avis`

- Create an admin

    `python manage.py createsuperuser`

    and follow instructions on the command line

- (optional) Import old data

    `python manage.py avis_import_dotnet_data -d $DATA_DIRECTORY`

    `$DATA_DIRECTORY` is the folder containing all JSON files from the old software

- Start a local instance of django

    `python manage.py runserver`

- Open admin page

    Open `http://localhost:8000/admin/` from a browser and login with admin credentials


## Local settings

Create a `website/settings_local.py` file with a content like this:

```py
import os

os.environ['DB_ENGINE'] = 'django.db.backends.postgresql'
os.environ['DB_NAME'] = 'database_name'
os.environ['DB_USER'] = 'youruser'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'

from .settings import *  # noqa
```

And launch `manage.py` commands with

`DJANGO_SETTINGS_MODULE=website.settings_local python manage.py ...`


## Sync project

- Update `main` branch (check for unstaged changes)

    ```
    git checkout main
    git pull
    ```

- Update static libs (bootstrap, etc...)

    Note: ensure `unzip` is installed

    ```
    make get-static-libs:
    ```

- Enable the virtual environment

- Update packages

    `make requirements`

## Enabling Git Hooks (optional)

You can create your own git hooks in the `.git/hooks/` directory, or you can use pre-defined hooks with

```sh
# use hooks from `.githooks` directory
git config --local core.hooksPath .githooks/

# use a single hook
ln -sf ../../.githooks/pre-commit .git/hooks/pre-commit
ln -sf ../../.githooks/pre-push .git/hooks/pre-push
```

This will add a pre-commit hook checking for `make style` before each commit,
and a pre-push hook checking for `make test` before each push.

You can skip hooks when committing/pushing with `--no-verify`
according to [git commit man page)](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt--n).


## Test / style with makefile

- `make test` for testing the whole codebase

- `make test-coverage` for testing the whole codebase and providing a coverage report

- `make style-check` check the code style for the entire codebase

- `make style-fix` tries to fix common errors in the codebase


## Environment variables

- `SECRET_KEY`
- `DEBUG`: set to `True`, `true` or `1` to enable debug
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `ADMIN_BASE_URL`: base url for admin mode, defaults to `admin`
