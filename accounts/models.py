from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils import timezone
import secrets
import string


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, date_of_birth, role, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.generate_verification_token() 
        user.save(using=self._db)


        return user

    def create_superuser(self, email, first_name, last_name, date_of_birth, role, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, date_of_birth, role, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    USER_ROLES = [
        ('buyer', 'Buyer'),
        ('planner', 'Planner'),
        ('caterers', 'Caterers'),
        ('drivers', 'Drivers'),
        ('manager','Manager')
        # Add other roles as needed
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=50, choices=USER_ROLES, default='buyer')
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    verification_expires_at = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth', 'role']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    def generate_verification_token(self):
        # Generate a random token with 64 characters
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
        # Set verification token
        self.verification_token = token
        # Set verification expiration time to 2 hours from now
        self.verification_expires_at = timezone.now() + timezone.timedelta(minutes=2)
