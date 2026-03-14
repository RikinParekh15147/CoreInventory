"""
Django development settings for CoreInventory.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend is inherited from base.py (which uses .env)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Simpler static file storage for dev
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Skip email verification in dev
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Celery: use in-memory broker for dev if Redis not available
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
