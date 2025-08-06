from django.shortcuts import render, redirect
import hashlib
from django.db import connections, IntegrityError

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()

        

        # Password length validation
        if len(password) < 6:  # You can set a minimum length (e.g., 6)
            return render(request, 'signup/index.html', {'error': 'Password must be at least 6 characters.'})
        if len(password) > 20:
            return render(request, 'signup/index.html', {'error': 'Password cannot exceed 20 characters.'})

        # Check duplicate username
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE account = %s", [username])
            if cursor.fetchone()[0] > 0:
                return render(request, 'signup/index.html', {'error': 'Username already exists.'})

        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE email_contact = %s", [email])
            if cursor.fetchone()[0] > 0:
                return render(request, 'signup/index.html', {'error': 'This email is already registered.'})

        # Create new id_user
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT TOP 1 id_user FROM Users ORDER BY id_user DESC")
            last_id = cursor.fetchone()
            new_id = f"U{int(last_id[0][1:]) + 1:03d}" if last_id else "U001"

        # Insert into DB
        with connections['legacy'].cursor() as cursor:
            cursor.execute("""
                INSERT INTO Users (id_user, name, email_contact, password, account, gender, language)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [new_id, username, email, password, username, 'Nam', 'Vietnamese'])

        return redirect('login')

    return render(request, 'signup/index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remember_me = request.POST.get('remember-me') == 'on'

        with connections['legacy'].cursor() as cursor:
            cursor.execute("""
                SELECT id_user, name FROM Users 
                WHERE account = %s AND password = %s
            """, [username, password])
            user_data = cursor.fetchone()

            if not user_data:
                return render(request, 'login/index.html', {'error': 'Invalid username or password'})

        # Đăng nhập thành công
        request.session['user'] = username

        # Remember me
        if remember_me:
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30 ngày
        else:
            request.session.set_expiry(0)  # Hết khi đóng trình duyệt

        return redirect('home')

    return render(request, 'login/index.html')

def home_view(request):
    return render(request, 'home/index.html')

def policy_view(request):
    return render(request, 'signup/Terms_policy/index.html')

# Trang Home
def home_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'home/index.html', {'user': request.session['user']})

# Event: Main event
def event_main_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'event/main-event/index.html', {'user': request.session['user']})

# Event: Recycle bin
def event_recycle_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'event/recycle-bin/index.html', {'user': request.session['user']})


# Calendar
def calendar_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'calendar/index.html')

# About Us
def about_view(request):
    return render(request, 'about/index.html')

# Profile
def profile_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'profile/index.html', {'user': request.session['user']})

# Logout
def logout_view(request):
    request.session.flush()
    return redirect('login')