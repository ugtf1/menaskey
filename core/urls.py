# core/urls.py
from django.urls import path
from . import views, webhooks

urlpatterns = [
    path('', views.home, name='home'),
    path('api/quote', views.api_quote, name='api_quote'),
    path('api/click', views.api_click, name='api_click'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # CallRail/webhook endpoint (secure with a secret/token or IP allowlist)
    path('webhooks/callrail', webhooks.callrail_handler, name='callrail_handler'),
]