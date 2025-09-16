from django.contrib import admin
from .models import QuoteRequest, ClickEvent, CallDetail

# Register your models here.
admin.site.register([QuoteRequest, ClickEvent, CallDetail])
