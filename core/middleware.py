# core/middleware.py
from urllib.parse import urlparse
from django.utils.deprecation import MiddlewareMixin

class UTMReferrerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        s = request.session
        if s.get('tracked'):  # set once per session
            return
        params = request.GET
        s['utm_source'] = params.get('utm_source') or ''
        s['utm_medium'] = params.get('utm_medium') or ''
        s['utm_campaign'] = params.get('utm_campaign') or ''
        ref = request.META.get('HTTP_REFERER', '')
        s['referrer'] = ref
        # Quick source inference if no utm_source
        if not s['utm_source']:
            if 'google.' in ref:
                s['utm_source'] = 'google'
                s['utm_medium'] = s['utm_medium'] or 'organic'
            elif 'bing.' in ref:
                s['utm_source'] = 'bing'
                s['utm_medium'] = s['utm_medium'] or 'organic'
            elif ref:
                host = urlparse(ref).hostname or ''
                s['utm_source'] = host
        s['tracked'] = True