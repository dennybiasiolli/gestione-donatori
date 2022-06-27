from .settings import *  # noqa
from .settings import MIDDLEWARE

MIDDLEWARE = MIDDLEWARE + [
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
