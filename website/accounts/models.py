from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    uuid = models.UUIDField(unique=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(blank=True, default = '', max_length=30, verbose_name='first name')
    last_name = models.CharField(blank=True, default = '', max_length=30, verbose_name='last name')
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Unselect this instead of deleting accounts.'),
    )
    is_staff = models.BooleanField(
        _('site admin'),
        default=False,
        help_text=_('User can administer this site.'),
    )
    is_admin = models.BooleanField(
        _('system admin'),
        default=False,
        help_text=_('User can access system administration functions.'),
    )
    is_volunteer = models.BooleanField(
        _('volunteer'),
        default=False,
        help_text=_('User can access volunteer functions.'),
    )
    date_joined  = models.DateTimeField(_("date joined"), default = timezone.now)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    objects = UserManager()

    @property
    def username(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
