from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class SpashtUser(AbstractUser):
    place = models.CharField(max_length=120, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    PROFESSION_CHOICES = [
        ("student", "Student"), 
        ("law_practitioner", "Law Practitioner"), 
        ("other", "Other")
    ]
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, blank=True, null=True)
    mobile_no = PhoneNumberField(blank=True, null=True, unique=True)
    def __str__(self):
        return self.username