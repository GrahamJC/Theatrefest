from django.conf import settings

def training(request):
    return { 'TRAINING': settings.TRAINING }
