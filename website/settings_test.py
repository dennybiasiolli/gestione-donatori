import multiprocessing

from .settings import *  # noqa

print("Using multiproc for testing.")
multiprocessing.set_start_method("fork")

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dbtest.sqlite3",  # noqa
    }
}
