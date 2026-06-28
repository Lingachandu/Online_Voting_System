from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Mobile Phone Number field must be set')
        extra_fields.setdefault('role', 'voter')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'), 
        ('voter', 'Voter')
    )
    STATE_CHOICES = (
        ('ap', 'Andhra Pradesh'),
        ('tg', 'Telangana'),
        ('chennai', 'Chennai')
    )
    
    username = None
    phone_number = models.CharField(max_length=10, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='voter')
    state = models.CharField(max_length=10, choices=STATE_CHOICES, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    face_image = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    has_logged_in = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.phone_number} ({self.role})"


class OTPVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_expired = models.BooleanField(default=False)