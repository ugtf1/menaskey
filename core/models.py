
from django.db import models

class QuoteRequest(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    service = models.CharField(max_length=120)
    message = models.TextField(blank=True)
    # session-captured traffic data (best-effort)
    source = models.CharField(max_length=120, blank=True)   # e.g., google, bing, direct
    medium = models.CharField(max_length=120, blank=True)   # e.g., organic, cpc
    campaign = models.CharField(max_length=120, blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ClickEvent(models.Model):
    EVENT_TYPES = (('website', 'Website Click'), ('call', 'Call Click'))
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    user_agent = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    source = models.CharField(max_length=120, blank=True)
    medium = models.CharField(max_length=120, blank=True)
    campaign = models.CharField(max_length=120, blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CallDetail(models.Model):
    # from CallRail or webhook
    caller_number = models.CharField(max_length=40, blank=True)
    duration_seconds = models.IntegerField(default=0)
    started_at = models.DateTimeField()
    recording_url = models.URLField(blank=True)
    source = models.CharField(max_length=120, blank=True)     # google, bing, direct, etc.
    medium = models.CharField(max_length=120, blank=True)     # organic, ppc, etc.
    campaign = models.CharField(max_length=120, blank=True)
    referrer = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)