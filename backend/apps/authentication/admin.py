from django.contrib import admin
from .models import CustomUser, OTPVerification

admin.site.register(CustomUser)
admin.site.register(OTPVerification)
