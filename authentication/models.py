# authentication/models.py
from django.db import models

class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    validated = models.BooleanField(default=False)  # Ensure this field is here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number


