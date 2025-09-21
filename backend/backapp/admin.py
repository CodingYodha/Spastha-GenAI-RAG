from django.contrib import admin
from .models import SpashtUser, ChatMessage
# Register your models here.
admin.site.register(SpashtUser)
admin.site.register(ChatMessage)