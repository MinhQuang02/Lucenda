from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, re_path, include
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse
from users import views
import os

def serve_ui(path):
    file_path = os.path.join(settings.BASE_DIR.parent, 'Back-end', 'templates', path, 'index.html')
    with open(file_path, encoding="utf-8") as f:
        return HttpResponse(f.read())

urlpatterns = [
    path('', lambda request: redirect('home')),
    path('login/', views.login_view, name='login'),           # Login
    path('signup/', views.signup_view, name='signup'),  # Signup
    path('forgotpassword/', views.forgot_password_view, name='forgot_password'),  # Forgot Password 
    path('signup/Term & policy/', views.policy_view, name='policy'),  # Terms & Policy
    path('home/', views.home_view, name='home'),        # Home
    path('event/main-event/', views.event_main_view, name='event_main'),
    path('event/recycle-bin-event/', views.event_recycle_view, name='event_recycle'),  # Recycle Bin
    path('calendar/day-view/', views.calendar_view, name='calendar'),  # Calendar
    path('calendar/recycle-bin/', views.calendar_recycle_view, name='calendar_recycle'),  # Calendar Recycle Bin
    path('aboutus/', views.about_view, name='about'),     # About Us
    path('profile/', views.profile_view, name='profile'),  # Profile
    path('otp_screen/', views.otp_view, name='verify_otp'),  # OTP Verification
    path('resend_otp/', views.resend_otp_view, name='resend_otp'),   # Resend OTP
    path('logout/', views.logout_view, name='logout'),  # Logout
    path("chat-api/", views.chat_api, name="chat_api"),  # Chat API
    path("delete-account/", views.delete_account_view, name="delacc"),  # Delete Account
    path('auth/', include('social_django.urls', namespace='social')),  # Google OAuth
    path('update-gender-sql/', views.update_gender_sql, name='update_gender_sql'), # Update Gender
    path('update-language-sql/', views.update_language_sql, name='update_language_sql'),  # Update Language
    path('update-dob-sql/', views.update_dob_sql, name='update_dob_sql'),  # Update Date of Birth
    path("update-password/", views.update_password_sql, name="update_password"),   # Update Password
    path("api/events/", views.create_event_sql, name="create_event_sql"), # Create Event
    path("api_display/events/", views.get_events, name="get_events"),  # Display Events
    path("get-event-data/", views.get_event_data, name="get_event_data"),  # Display Events Info
    path("delete-event/", views.delete_event, name="delete_event"),  # Delete Event
    path("api/save_event/", views.save_event, name="save_event"),  # Save Event
    path("api/deleted-events/", views.get_deleted_events, name="get_deleted_events"),  # Get Deleted Events
    path("restore-event/", views.restore_event, name="restore_event"), # Restore Event
    path("delete-event1/", views.delete_event1, name="delete_event1"),  # Delete Event
    path("update-username/", views.update_username, name="update_username"),  # Update Username
    path("api/calendars/", views.calendar_list, name="calendar_list"),  # Get Calendar List
    path("api/create-calendar/", views.create_calendar, name="create_calendar"),  # Create Calendar
    path("api/delete-calendar/", views.delete_calendar, name="delete_calendar"),  # Delete Calendar
    path("api/rename-calendar/", views.rename_calendar, name="rename_calendar"),  # Rename Calendar
    path("api/share-calendar/", views.share_calendar, name="share_calendar"),  # Share Calendar
    path("api/deleted-events-1/", views.get_deleted_events_1, name="get_deleted_events_1"), # Get Deleted Calendar
    path("restore-event-1/", views.restore_event_1, name="restore_event_1"), # Restore Calendar
    path("delete-event1-1/", views.delete_event1_1, name="delete_event1_1"),  # Delete Calendar
    path("api/event-calendar/", views.event_calendar_api, name="event_calendar_api"),  # Event Calendar
    path("api/events-1/", views.get_events_1, name="get_events_1"), # Get Events
    path("add-event", views.add_event, name="add_event"),  # Add Event
]