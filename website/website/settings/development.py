from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]

INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'theatrefest',
        'USER': 'theatrefest',
        'PASSWORD': 'barnum',
#        'HOST': 'localhost',
        'HOST': 'theatrefest.ukwest.cloudapp.azure.com',
        'PORT': '5432',
    }
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        'request': {
            '()': 'django_requestlogging.logging_filters.RequestFilter',
        }
    },
    "formatters": {
        "basic": {
            "format": "%(asctime)s %(levelname)-8s %(name)-32s %(message)s",
        },
        "request": {
            "format": "%(asctime)s %(username)-32s %(levelname)-8s %(name)-32s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "basic",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": r"E:\Temp\Theatrefest\theatrefest.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 10,
            "filters": ['request'],
            "formatter": "request",
        },
        "django": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": r"E:\Temp\Theatrefest\django.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 10,
            "formatter": "basic",
        },
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["django"],
            "propagate": False,
        },
        "django.server": {
            "level": "WARNING",
            "handlers": ["django"],
            "propagate": False,
        },
        "tickets": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

# E-mail
EMAIL_HOST = "ssrs.reachmail.net"
EMAIL_PORT = 465
EMAIL_HOST_USER = "GCCONSUL2\graham"
EMAIL_HOST_PASSWORD = get_secret("EASYSMTP_EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = True
