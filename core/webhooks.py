# core/webhooks.py
import json
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .models import CallDetail

@csrf_exempt
def callrail_handler(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST only')
    # Validate shared secret header
    secret = request.headers.get('X-Webhook-Secret')
    if secret != 'YOUR_SHARED_SECRET':
        return HttpResponseForbidden('Forbidden')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    # Map from CallRail (adjust keys to your payload)
    CallDetail.objects.create(
        caller_number=payload.get('caller_number',''),
        duration_seconds=int(payload.get('duration', 0)),
        started_at=parse_datetime(payload.get('start_time')) or None,
        recording_url=payload.get('recording',''),
        source=payload.get('source',''),
        medium=payload.get('medium',''),
        campaign=payload.get('campaign',''),
        referrer=payload.get('referrer',''),
        metadata=payload
    )
    return JsonResponse({'status': 'ok'})