import os
import posixpath
import json
from django.core.exceptions import ImproperlyConfigured

from decimal import Decimal

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Read JSON secrets file
with open(os.path.join(BASE_DIR, "secrets.json")) as f:
    secrets = json.loads(f.read())

def get_secret(setting):
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured("Secret {)} not found".format(setting))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("SECRET_KEY")

# Application definition
INSTALLED_APPS = [
    'django.contrib.sites',
    'registration',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'debug_toolbar',
    'crispy_forms',

    'accounts.apps.AccountsConfig',
    'content.apps.ContentConfig',
    'program.apps.ProgramConfig',
    'tickets.apps.TicketsConfig',
    'boxoffice.apps.BoxOfficeConfig',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django_requestlogging.middleware.LogSetupMiddleware',
]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'tf_filters': 'website.tf_filters'
            },
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# User model
AUTH_USER_MODEL = "accounts.User"

# Internationalization
LANGUAGE_CODE = 'en-uk'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
	os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['django_static']))
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Registration
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
REGISTRATION_DEFAULT_FROM_EMAIL = "noreply@theatrefest.co.uk"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Stripe
STRIPE_PUBLIC_KEY = get_secret("STRIPE_PUBLIC_KEY")
STRIPE_PRIVATE_KEY = get_secret("STRIPE_PRIVATE_KEY")
STRIPE_FEE_FIXED = Decimal(0.2)
STRIPE_FEE_PERCENT = Decimal(0.014)

# Debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
}
