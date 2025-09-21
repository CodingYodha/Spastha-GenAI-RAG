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
    
class ChatMessage(models.Model):
    user = models.ForeignKey(SpashtUser, on_delete=models.CASCADE, related_name="chat_messages")
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        who = "bot" if self.is_bot is True else "user"
        return f"{who}:{self.message[:30]}..."