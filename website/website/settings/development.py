from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'theatrefest',
        'USER': 'theatrefest',
        'PASSWORD': 'barnum',
        'HOST': 'theatrefest.ukwest.cloudapp.azure.com',
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
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": r"E:\Temp\theatrefest.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 10,
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
        "handlers": ["console", "file"],
    },
}
