# core/views.py
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from .forms import QuoteForm
from .models import QuoteRequest, ClickEvent, CallDetail

def home(request):
    # Render landing page; JS will post JSON to /api/quote and /api/click
    return render(request, 'home.html', {
        'phone': '+15551234567',
        'sticky_label': '24/7 Emergency • Call Now'
    })

def _traffic_from_session(request):
    s = request.session
    return {
        'source': s.get('utm_source', ''),
        'medium': s.get('utm_medium', ''),
        'campaign': s.get('utm_campaign', ''),
        'referrer': s.get('referrer', ''),
    }

@require_POST
def api_quote(request):
    # Expect JSON; inline validation + honeypot
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    form = QuoteForm(data)
    # honeypot: if company is filled, drop request
    if data.get('company'):
        return JsonResponse({'status': 'ignored', 'message': 'ok'}, status=200)

    if not form.is_valid():
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    t = _traffic_from_session(request)
    qr = QuoteRequest.objects.create(
        name=form.cleaned_data['name'],
        phone=form.cleaned_data['phone'],
        email=form.cleaned_data.get('email', ''),
        service=form.cleaned_data['service'],
        message=form.cleaned_data.get('message', ''),
        **t
    )

    # Optionally: forward to dashboard API or CRM here with requests.post(...)
    # requests.post(DASHBOARD_URL, json={...}, timeout=5)

    return JsonResponse({'status': 'ok', 'message': 'Thanks! We’ll reach out shortly.'})

@require_POST
def api_click(request):
    # track website or call clicks
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    event_type = data.get('event_type')
    if event_type not in ('website', 'call'):
        return HttpResponseBadRequest('Invalid event type')

    t = _traffic_from_session(request)
    ClickEvent.objects.create(
        event_type=event_type,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        ip=request.META.get('REMOTE_ADDR'),
        **t
    )
    return JsonResponse({'status': 'ok'})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','')
        user = authenticate(request, username=username, password=password)
        if user and user.is_active and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def staff_required(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(staff_required)
def dashboard(request):
    # KPIs
    website_clicks = ClickEvent.objects.filter(event_type='website').count()
    call_clicks = ClickEvent.objects.filter(event_type='call').count()

    # Recent calls list and small aggregates
    recent_calls = CallDetail.objects.order_by('-started_at')[:50]

    # Traffic origins
    def aggregate_sources(qs):
        out = {}
        for row in qs.values_list('source', flat=True):
            key = row or 'unknown'
            out[key] = out.get(key, 0) + 1
        return out

    click_sources = aggregate_sources(ClickEvent.objects.all())
    quote_sources = aggregate_sources(QuoteRequest.objects.all())
    call_sources = aggregate_sources(CallDetail.objects.all())

    return render(request, 'dashboard.html', {
        'website_clicks': website_clicks,
        'call_clicks': call_clicks,
        'recent_calls': recent_calls,
        'click_sources': click_sources,
        'quote_sources': quote_sources,
        'call_sources': call_sources,
    })