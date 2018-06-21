from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TRAINING = True

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
#        'NAME': 'training',
        'USER': 'theatrefest',
        'PASSWORD': 'barnum',
        'HOST': 'localhost',
#        'HOST': 'theatrefest.ukwest.cloudapp.azure.com',
        'PORT': '5432',
    },
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
EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 587
EMAIL_HOST_USER = "postmaster@mg.theatrefest.co.uk"
EMAIL_HOST_PASSWORD = get_secret("MAILGUN_EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

# Stripe
STRIPE_PUBLIC_KEY = get_secret("STRIPE_TEST_PUBLIC_KEY")
STRIPE_PRIVATE_KEY = get_secret("STRIPE_TEST_PRIVATE_KEY")
STRIPE_FEE_FIXED = Decimal(0.2)
STRIPE_FEE_PERCENT = Decimal(0.014)
