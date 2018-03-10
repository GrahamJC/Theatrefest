from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    'qnap',
    'grahamc.myqnapcloud.com',
    'theatrefest.ukwest.cloudapp.azure.com'
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

