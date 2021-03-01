# builtin
import uuid

# django
from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.utils import timezone

# third party
from phonenumber_field.modelfields import PhoneNumberField

# local
from .managers import UserManager


class AbstractFirebaseUser(AbstractBaseUser, PermissionsMixin):
    uid = models.CharField(unique=True, default=uuid.uuid1, max_length=50)
    display_name = models.CharField(
        'full name',
        max_length=100,
        null=True,
        blank=True,
    )

    phone_number = PhoneNumberField(
        'phone number',
        unique=True,
        null=True,
        blank=True,
        error_messages={
            'unique': "A user with this phone number already exists.",
        },
    )

    email = models.EmailField(
        'email address',
        unique=True,
        null=True,
        blank=True,
        default=None,
        error_messages={
            'unique': "A user with this email address already exists.",
        },
    )

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.',
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        abstract = True

    def get_username(self):
        return f'{self.identifer}'

    def clean(self):
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def identifer(self):
        return self.display_name or self.phone_number or self.email or self.uid


class FirebaseUser(AbstractFirebaseUser):
    """ Firebase User for Direct use  """

    class Meta(AbstractFirebaseUser.Meta):
        swappable = 'AUTH_USER_MODEL'
