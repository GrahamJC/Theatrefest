import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from registration.signals import user_registered, user_activated

log = logging.getLogger(__name__)

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    log.info("Login succeeded for: %s", user.email);

@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    if user:
        log.info("Log out for: %s", user.email);

@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    log.warning("Login failed for: %s", credentials["username"])

@receiver(user_registered)
def user_registered_callback(sender, request, user, **kwargs):
    log.info("New user registered: %s", user.email)

@receiver(user_activated)
def user_activated_callback(sender, request, user, **kwargs):
    log.info("New user activated: %s", user.email)
