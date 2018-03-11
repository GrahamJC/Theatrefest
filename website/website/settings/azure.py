from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'theatrefest.ukwest.cloudapp.azure.com'
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'theatrefest',
        'USER': 'theatrefest',
        'PASSWORD': 'barnum',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(message)s",
        }
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": r"/var/log/theatrefest/theatrefest.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["file"],
            "propogate": False,
        },
        "django.server": {
            "level": "INFO",
            "handlers": ["file"],
            "propogate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file"],
    },
}

