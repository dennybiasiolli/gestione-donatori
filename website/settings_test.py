# DON'T CHANGE THE ORDER OF THESE IMPORTS
import multiprocessing

from dotenv import load_dotenv  # isort:skip

load_dotenv(".env.default")

# DON'T CHANGE THE ORDER OF THESE IMPORTS
from .settings_base import *  # noqa isort:skip


print("Using multiproc for testing.")
multiprocessing.set_start_method("fork")

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa
    }
}
