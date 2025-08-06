from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse
from users import views
import os

def serve_ui(path):
    file_path = os.path.join(settings.BASE_DIR.parent, 'UI', 'Source Code', path, 'index.html')
    with open(file_path, encoding="utf-8") as f:
        return HttpResponse(f.read())

urlpatterns = [
    path('', views.login_view, name='login'),           # Login
    path('signup/', views.signup_view, name='signup'),  # Signup
    path('policy/', views.policy_view, name='policy'),  # Terms & Policy
    path('home/', views.home_view, name='home'),        # Home
    path('event/', views.event_main_view, name='event_main'),
    path('event/recycle-bin/', views.event_recycle_view, name='event_recycle'),  # Recycle Bin
    path('calendar/', views.calendar_view, name='calendar'),  # Calendar
    path('about/', views.about_view, name='about'),     # About Us
    path('profile/', views.profile_view, name='profile'),  # Profile
    path('logout/', views.logout_view, name='logout'),  # Logout
]

