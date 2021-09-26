from django.db import models
from django.contrib.auth.models import User,AbstractUser,AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import auth

# Create your models here.




#===========================================================================
#   ACCOUNT CATEGORY MODEL
#===========================================================================

class AccountCategory(models.Model):
    title = models.CharField(max_length=256)
    max_amount_of_drivers = models.IntegerField(default=1)
    max_amount_of_trucks = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural='account categories'

    def __str__(self):
        return self.title

















# ==============================================================================
#   USER and USER MANAGER: CUSTOM USER MODEL
# ==============================================================================

class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):

    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    company_name = models.CharField(max_length=256, blank=True)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    phone = models.CharField(
        verbose_name='phone',
        max_length=20,
        unique=True,
    )

    last_uid = models.CharField(max_length=256,default='-1')
    last_token = models.CharField(max_length=256,default='-1')
    last_uid_password = models.CharField(max_length=256,default='-1')
    last_token_password = models.CharField(max_length=256,default='-1')

    account_category = models.ForeignKey(AccountCategory, null=True, default=None, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] #email and password are required by default

    def __str__(self):
        if self.email != None:
            return self.email
        else:
            return 'Anonymous'

    objects = UserManager()





#===========================================================================
#   DRIVER PROFILE MODEL
#===========================================================================
class DriverProfile(models.Model):

    user = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL)

    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    phone = models.CharField(
        verbose_name='phone',
        max_length=20,
        unique=True,
    )

    last_uid = models.CharField(max_length=256,default='-1')
    last_token = models.CharField(max_length=256,default='-1')
    last_uid_password = models.CharField(max_length=256,default='-1')
    last_token_password = models.CharField(max_length=256,default='-1')

    def __str__(self):
        if self.email != None:
            return self.email
        else:
            return 'Anonymous'
