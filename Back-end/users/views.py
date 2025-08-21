from django.shortcuts import render, redirect
import hashlib
from django.db import connections, IntegrityError
import re
from validate_email_address import validate_email
import random
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import json
import string
import os
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.db import transaction


# Define a strong password policy
def is_strong_password(password):
    return all([
        re.search(r"[A-Z]", password),
        re.search(r"[a-z]", password),
        re.search(r"[0-9]", password),
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    ])

# Generate random password
def generate_temp_password(length=8):
    """Tạo mật khẩu tạm thời gồm chữ hoa, chữ thường và số"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Sign up view and password validation
def signup_view(request):
    if 'user' in request.session:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()

        # Password length validation
        if len(password) < 6:  # You can set a minimum length (e.g., 6)
            return render(request, 'signup/index.html', {'error': 'Password must be at least 6 characters.'})
        if len(password) > 20:
            return render(request, 'signup/index.html', {'error': 'Password cannot exceed 20 characters.'})
        if not is_strong_password(password):
            return render(request, 'signup/index.html', {'error': 'Password must contain uppercase, lowercase, number, and special character.'})
        
        # Validate email existence
        if not validate_email(email, verify=True):
            return render(request, 'signup/index.html', {'error': 'This email address does not seem to exist.'})

        # Check duplicate username
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE account = %s", [username])
            if cursor.fetchone()[0] > 0:
                return render(request, 'signup/index.html', {'error': 'Username already exists.'})

        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE email_contact = %s", [email])
            if cursor.fetchone()[0] > 0:
                return render(request, 'signup/index.html', {'error': 'This email is already registered.'})
        
        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        otp_digits = list(otp_code)
        while len(otp_digits) < 6:
            otp_digits.append(' ')  # tránh lỗi nếu OTP ngắn hơn

        year = datetime.now().year

        # Send OTP email with HTML format
        send_mail(
            'Lucenda - Secure OTP for Your Account',
            f'Your OTP code is: {otp_code}. Please note that this code will expire in 5 minutes. For your security, do not share this code with anyone.',
            'Lucenda Support <noreply@yourdomain.com>',  # from email
            [email],
            fail_silently=False,
            html_message=f"""
                <!doctype html>
                <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
                <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <meta http-equiv="x-ua-compatible" content="ie=edge">
                <title>Your OTP Code</title>
                <style>
                    body, table, td, a {{ text-size-adjust: 100%; -ms-text-size-adjust:100%; -webkit-text-size-adjust:100%; }}
                    table, td {{ mso-table-lspace:0pt; mso-table-rspace:0pt; border-collapse: collapse !important; }}
                    img {{ -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }}
                    body {{ margin:0; padding:0; width:100% !important; height:100% !important; }}
                    @media (prefers-color-scheme: dark) {{
                    .card {{ background: #0f172a !important; }}
                    .text-muted {{ color: #94a3b8 !important; }}
                    .title, .text {{ color: #e2e8f0 !important; }}
                    .otp-box {{ background:#0b1220 !important; border-color:#334155 !important; color:#e2e8f0 !important; }}
                    }}
                </style>
                </head>
                <body style="background: #f3faff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial;">

                <div style="display:none; font-size:1px; color:#f3faff; line-height:1; max-height:0; max-width:0; opacity:0; overflow:hidden;">
                    Hi {username}, your OTP code is {otp_code}. This code will expire in 5 minutes.
                </div>

                <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                    <td align="center" style="padding: 32px 16px;">
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width: 560px; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 16px rgba(30, 64, 175, 0.12);" class="card">
                        <tr>
                            <td style="background: linear-gradient(135deg, #e8f4ff 0%, #d6ebff 50%, #c2e2ff 100%); padding: 28px 24px; text-align:center;">
                            <div style="display:inline-block; padding:10px 16px; border-radius:999px; background:rgba(255,255,255,0.9); border:1px solid rgba(59,130,246,0.20); font-weight:600; color:#1e3a8a;">
                                Lucenda Security
                            </div>
                            <h1 style="margin:16px 0 0; font-size:22px; color:#0f172a; font-weight:700;" class="title">
                                Email Verification
                            </h1>
                            <p style="margin:8px 0 0; font-size:14px; color:#334155;" class="text">
                                Please use the OTP code below to verify your account.
                            </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 28px 24px 8px;">
                            <p style="margin:0 0 12px; font-size:15px; color:#0f172a;" class="text">
                                Hi <strong>{username}</strong>,
                            </p>
                            <p style="margin:0 0 20px; font-size:15px; color:#0f172a;" class="text">
                                Your OTP code is:
                            </p>
                            <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin: 0 0 20px;">
                                <tr>
                                <td align="center">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:auto;">
                                    {''.join(f'<td class="otp-box" style="width:48px; height:56px; border:1px solid #bcd9ff; background:#f0f7ff; color:#0f172a; font-weight:700; font-size:22px; text-align:center; border-radius:10px;">{digit}</td><td style="width:8px;"></td>' for digit in otp_digits)[:-25]}
                                    </table>
                                </td>
                                </tr>
                            </table>
                            <p style="margin:0 0 12px; font-size:14px; color:#0f172a;" class="text">
                                This code will <strong>expire in 5 minutes</strong>. Please do not share it with anyone.
                            </p>
                            <p style="margin:12px 0 0; font-size:13px; color:#475569;" class="text-muted">
                                If you didn’t request this, you can safely ignore this email.
                            </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px 24px 28px; text-align:center;">
                            <hr style="border:none; border-top:1px solid #e2e8f0; margin:0 0 16px;">
                            <p style="margin:0; font-size:12px; color:#64748b;" class="text-muted">
                                © {year} Lucenda. All rights reserved.
                            </p>
                            </td>
                        </tr>
                        </table>
                        <div style="max-width:560px; margin:16px auto 0; font-family: monospace; font-size:12px; color:#475569; text-align:center;">
                        Fallback OTP: <strong>{otp_code}</strong>
                        </div>
                    </td>
                    </tr>
                </table>
                </body>
                </html>
            """
        )

        # Store OTP & temp data in session
        request.session['signup_temp'] = {
            'username': username,
            'email': email,
            'password': password,
            'otp': otp_code,
            'otp_expire': (timezone.now() + timedelta(minutes=5)).isoformat()
        }

        return redirect('verify_otp')  # Trang nhập OTP

    return render(request, 'signup/index.html')


def login_view(request):
    if 'user' in request.session:
        return redirect('home')
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

def policy_view(request):
    return render(request, 'signup/Term & policy/index.html')

def forgot_password_view(request):
    if 'user' in request.session:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email').strip()

        # Validate email existence
        if not validate_email(email, verify=True):
            return render(request, 'forgotpassword/index.html', {'error': 'This email address does not seem to exist.'})

        # Check if email exists
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE email_contact = %s", [email])
            if cursor.fetchone()[0] == 0:
                # Email chưa tồn tại, render lỗi
                return render(request, 'forgotpassword/index.html', {'error': 'This email is not registered.'})

        # Generate a temporary password
        temp_password = generate_temp_password()
        year = timezone.now().year

        # Send email with the temporary password
        send_mail(
            'Lucenda - Your New Temporary Password',
            f'Hello {email}. This is your new temporary password: {temp_password}. Don\'t share it with anyone.',
            'Lucenda Support <noreply@yourdomain.com>',  # from email
            [email],
            fail_silently=False,
            html_message = f"""
                <!doctype html>
                <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
                <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <meta http-equiv="x-ua-compatible" content="ie=edge">
                <title>Your New Temporary Password</title>
                <style>
                    body, table, td, a {{ text-size-adjust:100%; -ms-text-size-adjust:100%; -webkit-text-size-adjust:100%; }}
                    table, td {{ mso-table-lspace:0pt; mso-table-rspace:0pt; border-collapse: collapse !important; }}
                    img {{ -ms-interpolation-mode: bicubic; border:0; outline:none; text-decoration:none; }}
                    body {{ margin:0; padding:0; width:100% !important; height:100% !important; background: #e3f2fd; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial; }}
                    @media (prefers-color-scheme: dark) {{
                        .card {{ background: #0f172a !important; }}
                        .text-muted {{ color: #94a3b8 !important; }}
                        .title, .text {{ color: #e2e8f0 !important; }}
                        .password-box {{ background:#0b1220 !important; border-color:#334155 !important; color:#e2e8f0 !important; }}
                    }}
                </style>
                </head>
                <body>
                <div style="display:none; font-size:1px; color:#e3f2fd; line-height:1; max-height:0; max-width:0; opacity:0; overflow:hidden;">
                    Hi {email}, your temporary password is {temp_password}.
                </div>

                <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                <td align="center" style="padding: 32px 16px;">
                    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width: 560px; background:#F0F8FF; border-radius:16px; overflow:hidden; box-shadow:0 4px 16px rgba(30,64,175,0.12);" class="card">
                        <tr>
                            <td style="background: linear-gradient(135deg, #cce4f6 0%, #99d0f0 50%, #66bbe8 100%); padding: 28px 24px; text-align:center;">
                                <div style="display:inline-block; padding:10px 16px; border-radius:999px; background:rgba(255,255,255,0.9); border:1px solid rgba(0,123,255,0.2); font-weight:600; color:#0a3d62;">
                                    Lucenda Security
                                </div>
                                <h1 style="margin:16px 0 0; font-size:22px; color:#0a3d62; font-weight:700;" class="title">
                                    Password Reset
                                </h1>
                                <p style="margin:8px 0 0; font-size:14px; color:#0a3d62;" class="text">
                                    Your new temporary password is shown below.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 28px 24px 8px;">
                                <p style="margin:0 0 12px; font-size:15px; color:#0a3d62;" class="text">
                                    Hi <strong>{email}</strong>,
                                </p>
                                <p style="margin:0 0 20px; font-size:15px; color:#0a3d62;" class="text">
                                    Please use the following temporary password to log in:
                                </p>
                                <div style="display:flex; justify-content:center; margin-bottom:20px;">
                                    <div style="padding:16px 204px; border-radius:10px; background:#e0f2ff; color:#0a3d62; font-weight:700; font-size:20px; letter-spacing:1px;">
                                        {temp_password}
                                    </div>
                                </div>
                                <p style="margin:0 0 12px; font-size:14px; color:#0a3d62;" class="text">
                                    For security, please log in and change this password immediately.
                                </p>
                                <p style="margin:12px 0 0; font-size:13px; color:#475569;" class="text-muted">
                                    If you didn’t request this, please contact our support team.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px 24px 28px; text-align:center;">
                                <hr style="border:none; border-top:1px solid #cce4f6; margin:0 0 16px;">
                                <p style="margin:0; font-size:12px; color:#64748b;" class="text-muted">
                                    © {year} Lucenda. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
                </tr>
                </table>
                </body>
                </html>
                """
        )
        # Update password in DB
        with connections['legacy'].cursor() as cursor:
            cursor.execute("""
                UPDATE Users
                SET password = %s
                WHERE email_contact = %s
            """, [temp_password, email])

        return render(request, 'forgotpassword/index.html', {'error': 'Temporary password sent to your email.'})

    return render(request, 'forgotpassword/index.html')

# Trang Home
def home_view(request):
    if request.user.is_authenticated:
        email = request.user.email
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE email_contact = %s", [email])
            if cursor.fetchone()[0] > 0:
                # Email đã tồn tại và người dùng sẽ đăng nhập
                cursor.execute("SELECT account FROM Users WHERE email_contact = %s", [email])
                request.session['user'] = cursor.fetchone()[0]
            else:
                # Email chưa tồn tại và tạo ra email mới
                base_username = email.split('@')[0]
                username = base_username
                suffix = 1

                # Lấy tất cả account để tránh trùng
                cursor.execute("SELECT account FROM Users")
                existing_usernames = {u[0] for u in cursor.fetchall()}

                while username in existing_usernames:
                    username = f"{base_username}{suffix}"
                    suffix += 1

                # Tạo mật khẩu ngẫu nhiên
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

                # Create new id_user
                with connections['legacy'].cursor() as cursor:
                    cursor.execute("SELECT TOP 1 id_user FROM Users ORDER BY id_user DESC")
                    last_id = cursor.fetchone()
                    new_id = f"U{int(last_id[0][1:]) + 1:03d}" if last_id else "U001"

                # Insert into DB
                with connections['legacy'].cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO Users (id_user, name, email_contact, password, account, gender, language, dob)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [new_id, username, email, password, username, 'Male', 'Vietnamese', '2000-01-01'])

                request.session['user'] = username

                year = timezone.now().year

                # Send email with the generated password for a new Google sign-in account
                send_mail(
                    'Lucenda - Welcome! Your New Account and Password',
                    f"""Hello {email},

                Welcome to Lucenda! Your account was created using Google Sign-In. 
                We have generated a secure password for you: {password}

                Please keep this password safe and do not share it with anyone.
                """,
                    'Lucenda Support <noreply@yourdomain.com>',  # from email
                    [email],
                    fail_silently=False,
                    html_message=f"""
                        <!doctype html>
                        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
                        <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width">
                        <meta http-equiv="x-ua-compatible" content="ie=edge">
                        <title>Welcome to Lucenda</title>
                        <style>
                            body, table, td, a {{ text-size-adjust:100%; -ms-text-size-adjust:100%; -webkit-text-size-adjust:100%; }}
                            table, td {{ mso-table-lspace:0pt; mso-table-rspace:0pt; border-collapse: collapse !important; }}
                            img {{ -ms-interpolation-mode: bicubic; border:0; outline:none; text-decoration:none; }}
                            body {{ margin:0; padding:0; width:100% !important; height:100% !important; background: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial; }}
                            @media (prefers-color-scheme: dark) {{
                                .card {{ background: #0f172a !important; }}
                                .text-muted {{ color: #94a3b8 !important; }}
                                .title, .text {{ color: #e2e8f0 !important; }}
                                .password-box {{ background:#0b1220 !important; border-color:#334155 !important; color:#e2e8f0 !important; }}
                            }}
                        </style>
                        </head>
                        <body>
                        <div style="display:none; font-size:1px; color:#f1f5f9; line-height:1; max-height:0; max-width:0; opacity:0; overflow:hidden;">
                            Hi {email}, welcome to Lucenda! Your generated password is {password}.
                        </div>

                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                        <td align="center" style="padding: 32px 16px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width: 560px; background:#F4FAFF; border-radius:16px; overflow:hidden; box-shadow:0 4px 16px rgba(30,64,175,0.12);" class="card">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 50%, #3b82f6 100%); padding: 28px 24px; text-align:center;">
                                        <div style="display:inline-block; padding:10px 16px; border-radius:999px; background:rgba(255,255,255,0.9); border:1px solid rgba(59,130,246,0.2); font-weight:600; color:#0a3d62;">
                                            Lucenda Security
                                        </div>
                                        <h1 style="margin:16px 0 0; font-size:22px; color:#0a3d62; font-weight:700;" class="title">
                                            Welcome to Lucenda
                                        </h1>
                                        <p style="margin:8px 0 0; font-size:14px; color:#0a3d62;" class="text">
                                            Your account has been successfully created via Google Sign-In.
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 28px 24px 8px;">
                                        <p style="margin:0 0 12px; font-size:15px; color:#0a3d62;" class="text">
                                            Hi <strong>{username}</strong>,
                                        </p>
                                        <p style="margin:0 0 20px; font-size:15px; color:#0a3d62;" class="text">
                                            We’ve generated a secure password for your new account. Please keep it safe and <strong>do not share it with anyone</strong>.
                                        </p>
                                        <div style="display:flex; justify-content:center; margin-bottom:20px;">
                                            <div style="padding:16px 204px; border-radius:10px; background:#d4e6f1; color:#2a5370; font-weight:700; font-size:20px; letter-spacing:1px;" class="password-box">
                                                {password}
                                            </div>
                                        </div>
                                        <p style="margin:0 0 12px; font-size:14px; color:#0a3d62;" class="text">
                                            You can use this password to log in via email as well as Google. We recommend changing it as soon as possible for security.
                                        </p>
                                        <p style="margin:12px 0 0; font-size:13px; color:#475569;" class="text-muted">
                                            If you didn’t create this account, please contact our support team immediately.
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 24px 28px; text-align:center;">
                                        <hr style="border:none; border-top:1px solid #dbeafe; margin:0 0 16px;">
                                        <p style="margin:0; font-size:12px; color:#64748b;" class="text-muted">
                                            © {year} Lucenda. All rights reserved.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                        </tr>
                        </table>
                        </body>
                        </html>
                    """
                )


    if 'user' not in request.session:
        return render(request, 'home/index.html')
    return render(request, 'home/index.html', {'haslogin': request.session['user']})


# Event: Main event
def event_main_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'event/main-event/index.html', {'haslogin': request.session['user']})

# Event: Recycle bin
def event_recycle_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'event/recycle-bin-event/index.html', {'haslogin': request.session['user']})
    

# Calendar
def calendar_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'calendar/day-view/index.html', {'haslogin': request.session['user']})


# Calendar: Recycle Bin
def calendar_recycle_view(request):
    if 'user' not in request.session:
        return redirect('login')
    return render(request, 'calendar/recycle-bin/index.html', {'haslogin': request.session['user']})


# About Us
def about_view(request):
    if 'user' not in request.session:
        return render(request, 'aboutus/index.html')
    return render(request, 'aboutus/index.html', {'haslogin': request.session['user']})


# Profile
def profile_view(request):
    if 'user' not in request.session:
        return redirect('login')

    # Lấy dữ liệu (user) của người dùng ra khỏi database
    username = request.session['user']
    with connections['default'].cursor() as cursor:
        cursor.execute("""
            SELECT email_contact, gender, language, dob, password, id_user
            FROM Users
            WHERE account = %s
        """, [username])
        row = cursor.fetchone()

    if row:
        data = {
            'email': row[0],
            'gender': row[1],
            'language': row[2],
            'dob': row[3],
            'password': row[4],
            'id_user': row[5]
        }
    else:
        data = None

    return render(request, 'profile/index.html', {'haslogin': request.session['user'], 'email': data['email'], 'gender': data['gender'], 'language': data['language'], 'dob': data['dob'], 'password': data['password'], 'id_user': data['id_user']})

# Otp Screen
def otp_view(request):
    signup_temp = request.session.get('signup_temp')
    if not signup_temp:
        return redirect('signup')  # Nếu không có session signup tạm, quay lại đăng ký

    if request.method == 'POST':
        # Nối các ô input OTP thành 1 chuỗi
        otp_entered = ''.join([request.POST.get(f'otp{i}', '') for i in range(1, 7)])

        otp_saved = signup_temp.get('otp')
        otp_expire = signup_temp.get('otp_expire')

        if not otp_saved or not otp_expire:
            return render(request, 'otp_screen/index.html', {'error': 'OTP not found. Please resend.'})

        # Chuyển otp_expire từ string sang datetime
        otp_expire_time = datetime.fromisoformat(otp_expire)
        otp_expire_time = otp_expire_time.replace(tzinfo=timezone.get_current_timezone())

        # Kiểm tra OTP hết hạn
        if timezone.now() > otp_expire_time:
            # Xóa OTP và thời gian hết hạn khỏi session
            signup_temp.pop('otp', None)
            signup_temp.pop('otp_expire', None)
            request.session['signup_temp'] = signup_temp
            return render(request, 'otp_screen/index.html', {'error': 'OTP has expired. Please request a new code.'})

        # Kiểm tra OTP hợp lệ
        if otp_entered != otp_saved:
            return render(request, 'otp_screen/index.html', {'error': 'Invalid OTP'})

        # Lấy ra tài khoản mật khẩu mail hợp lệ
        username = signup_temp['username']
        email = signup_temp['email']
        password = signup_temp['password']

        # Create new id_user
        with connections['legacy'].cursor() as cursor:
            cursor.execute("SELECT TOP 1 id_user FROM Users ORDER BY id_user DESC")
            last_id = cursor.fetchone()
            new_id = f"U{int(last_id[0][1:]) + 1:03d}" if last_id else "U001"

        # Insert into DB
        with connections['legacy'].cursor() as cursor:
            cursor.execute("""
                INSERT INTO Users (id_user, name, email_contact, password, account, gender, language, dob)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [new_id, username, email, password, username, 'Male', 'Vietnamese', '2000-01-01'])

        # Xóa toàn bộ session tạm
        del request.session['signup_temp']

        # Chuyển sang màn hình login
        return redirect('login')

    return render(request, 'otp_screen/index.html')

# Resend OTP
def resend_otp_view(request):
    if 'user' in request.session:
        return redirect('home')
    if request.method == 'POST':
        email = request.session.get('signup_temp', {}).get('email')
        if email:
            otp_code = send_otp_email(email)
            request.session['signup_temp']['otp'] = otp_code
            return render(request, 'otp_screen/index.html', {'message': 'OTP has been resent to your email.'})
    return redirect('login')

# Logout
def logout_view(request):
    request.session.flush()
    return redirect('login')

# Delete Account
def delete_account_view(request):
    username = request.session['user']
    print(username)
    with connections['legacy'].cursor() as cursor:
        # Lấy id_user từ username (cột account)
        cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
        result = cursor.fetchone()

        id_user = result[0]

        # Xóa dữ liệu liên quan trong các bảng quan hệ
        cursor.execute("DELETE FROM Used_Eve WHERE id_user = %s", [id_user])
        cursor.execute("DELETE FROM Creator_Eve WHERE id_user = %s", [id_user])
        cursor.execute("DELETE FROM Used_Calen WHERE id_user = %s", [id_user])
        cursor.execute("DELETE FROM Creator_Calen WHERE id_user = %s", [id_user])

        # Cuối cùng, xóa user
        cursor.execute("DELETE FROM Users WHERE id_user = %s", [id_user])

    request.session.flush()
    return redirect('login')

# Chatbot
from groq import Groq
# Khởi tạo client Groq
client = Groq(api_key="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")  # Đăng ký free ở https://console.groq.com

def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        # Gọi API Groq (giống OpenAI)
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Hoặc llama3-8b-8192 nếu muốn nhẹ hơn
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý AI của trang web Lucenda. Bạn có tên là LucendaBot. Bạn sẽ trợ giúp người dùng với các câu hỏi và vấn đề liên quan đến trong và ngoài trang web."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content
        return JsonResponse({"reply": bot_reply})

# Update Gender
@csrf_exempt
def update_gender_sql(request):
    if request.method == "POST":
        # Lấy username từ session
        username = request.session['user']
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        # Lấy gender mới từ request body
        data = json.loads(request.body)
        new_gender = data.get("gender")
        
        if new_gender not in ["Male", "Fmale", "Other"]:
            return JsonResponse({"status": "error", "message": "Invalid gender"}, status=400)

        try:
            with connections['legacy'].cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE Users
                    SET gender = %s
                    WHERE account = %s
                    """,
                    [new_gender, username]
                )
                
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Update Language
@csrf_exempt
def update_language_sql(request):
    if request.method == "POST":
        username = request.session.get('user')
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        new_language = data.get("language")
        if new_language not in ["English", "Vietnamese"]:
            return JsonResponse({"status": "error", "message": "Invalid language"}, status=400)

        try:
            with connections['legacy'].cursor() as cursor:
                cursor.execute(
                    "UPDATE Users SET language = %s WHERE account = %s",
                    [new_language, username]
                )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Update Dob
@csrf_exempt
def update_dob_sql(request):
    if request.method == "POST":
        username = request.session.get('user')
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        new_dob = data.get("dob")  # định dạng yyyy-mm-dd
        if not new_dob:
            return JsonResponse({"status": "error", "message": "No date provided"}, status=400)

        try:
            with connections['legacy'].cursor() as cursor:
                cursor.execute(
                    "UPDATE Users SET dob = %s WHERE account = %s",
                    [new_dob, username]
                )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Update Password
@csrf_exempt
def update_password_sql(request):
    if request.method == "POST":
        username = request.session.get('user')  # Lấy username từ session
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        new_password = data.get("password")
        if not new_password:
            return JsonResponse({"status": "error", "message": "No password provided"}, status=400)

        try:
            with connections['legacy'].cursor() as cursor:
                cursor.execute(
                    "UPDATE Users SET password = %s WHERE account = %s",
                    [new_password, username]
                )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Create new event
def create_event_sql(request):
    if request.method == "POST":
        username = request.session.get('user')  # Lấy username từ session
        
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        with connections["legacy"].cursor() as cursor:
            cursor.execute(
                "SELECT id_user FROM Users WHERE account = %s",
                [username]
            )
            row = cursor.fetchone()

        if not row:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)

        user_id = row[0]  # mã ID của user

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        event_name = data.get("name", "").strip()
        if not event_name:
            return JsonResponse({"status": "error", "message": "Event name is required"}, status=400)

        try:
            # Create new id_event
            with connections['legacy'].cursor() as cursor:
                cursor.execute("SELECT TOP 1 id_event FROM Events ORDER BY id_event DESC")
                last_id = cursor.fetchone()
                new_id = f"E{int(last_id[0][1:]) + 1:03d}" if last_id else "E001"

            # Cập nhập bảng event
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Events (id_event, name_event, detail, time_event, time_created, loop, in_trash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [new_id, event_name, "", timezone.now() + timedelta(days=10), timezone.now() + timedelta(hours=7), datetime(2000, 1, 1), 0]
                )

            # Cập nhập bảng created event
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Creator_Eve (id_user, id_event)
                    VALUES (%s, %s)
                    """,
                    [user_id, new_id]
                )

            # Cập nhập bảng used event
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Used_Eve (id_user, id_event, notification)
                    VALUES (%s, %s, %s)
                    """,
                    [user_id, new_id, 0]
                )

            return JsonResponse({"status": "success"}, status=201)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Display event
def get_events(request):
    username = request.session.get("user")
    if not username:
        return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

    try:
        with connections["legacy"].cursor() as cursor:
            # Lấy id_user
            cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({"status": "error", "message": "User not found"}, status=404)
            user_id = row[0]

            # Lấy các id_event user có quyền
            cursor.execute("""
                SELECT id_event
                FROM Used_Eve
                WHERE id_user = %s
            """, [user_id])
            id_events = [r[0] for r in cursor.fetchall()]

            if not id_events:
                return JsonResponse([], safe=False, status=200)

            # Lấy id_event + name_event trong Events theo các id trên
            placeholders = ",".join(["%s"] * len(id_events))
            cursor.execute(f"""
                SELECT id_event, name_event
                FROM Events
                WHERE id_event IN ({placeholders})
                  AND in_trash = 0
                ORDER BY time_created DESC
            """, id_events)
            rows = cursor.fetchall()

            # Trả về list chuỗi "id - name"
            events = [f"{row[0]} - {row[1]}" for row in rows]
            data = [{"name_event": f"{row[0]} - {row[1]}"} for row in rows]
            
        return JsonResponse(data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# Display event info
def get_event_data(request):
    username = request.session.get("user")
    if not username:
        return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)
    event_name = request.GET.get("name", "").strip()
    match = re.match(r"^(\S+)", event_name)
    event_id = match.group(1) if match else None

    if not event_id:
        return JsonResponse({"status": "error", "message": "Invalid event name"}, status=400)

    try:
        # Tìm account của người tạo sự kiện này
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                SELECT account
                FROM Users
                WHERE id_user = (
                    SELECT id_user
                    FROM Creator_Eve
                    WHERE id_event = %s
                )
            """, [event_id])

            row_name = cursor.fetchone()
            id_name = row_name[0] if row_name else None

        # Tìm thông tin sự kiện
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                SELECT id_event, name_event, detail, time_event, time_created, loop, in_trash
                FROM Events
                WHERE id_event = %s
            """, [event_id])

            row = cursor.fetchone()

        # Tìm tất cả mọi người được chia sẻ sự kiện này
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                SELECT id_user
                FROM Used_Eve
                WHERE id_event = %s
            """, [event_id])

            shared_id_users = cursor.fetchall()

        # Tìm người hiện dùng sự kiện này
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                SELECT notification
                FROM Used_Eve
                WHERE id_user = (
                    SELECT id_user
                    FROM Users
                    WHERE account = %s
                ) and id_event = %s
            """, [username, event_id])

            row_not = cursor.fetchone()
            notification_row = row_not[0] if row_not else None

        if row:
            data = {
                "id_event": row[0],
                "title": row[1],
                "detail": row[2],
                "time_event": row[3].strftime("%B %d, %Y at %#I:%M %p") if row[3] else None,
                "date_created": row[4].strftime("%b %d, %Y - %H:%M") if row[4] else None,
                "loop": row[5],
                "notification": notification_row,
                "author_id": id_name,
                "shared_ids": [user[0].strip() if isinstance(user[0], str) else user[0] for user in shared_id_users]
            }
        else:
            data = {
                "id_event": "Unknown",
                "title": "Unknown Event",
                "detail": "No details available.",
                "time_event": "Unknown",
                "date_created": "Unknown",
                "loop": "Unknown",
                "notification": 0,
                "author_id": "Unknown",
                "shared_ids": []
            }

        return JsonResponse(data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# Xóa sự kiện
@csrf_exempt  # (nếu bạn test bằng fetch, nên dùng. Khi production thì nên xài CSRF token)
def delete_event(request):
    if request.method == "POST":
        username = request.session.get("user")
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        try:
            with connections["legacy"].cursor() as cursor:
                # Lấy id_user
                cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({"status": "error", "message": "User not found"}, status=404)
                user_id = row[0]

            data = json.loads(request.body)
            event_name = data.get("name")
            match = re.match(r"^(\S+)", event_name)
            event_id = match.group(1) if match else None

            if not event_name:
                return JsonResponse({"error": "Thiếu tên sự kiện"}, status=400)

            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    SELECT id_user
                    FROM Creator_Eve
                    WHERE id_event = %s
                """, [event_id])

                creator_row = cursor.fetchone()
                if not creator_row:
                    return JsonResponse({"error": "Không tìm thấy người tạo sự kiện"}, status=404)
                creator_id = creator_row[0]

                if creator_id != user_id:
                    return JsonResponse({"error": "Bạn không có quyền xoá sự kiện này"}, status=403)

            # --- SQL xoá sự kiện ---
            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Used_Eve
                    WHERE id_event = %s
                """, [event_id])

            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    UPDATE Events
                    SET in_trash = 1
                    WHERE id_event = %s
                """, [event_id])

            return JsonResponse({"message": f"Đã xoá sự kiện {event_name}"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)

# Cập nhập lại sự kiện
@csrf_exempt
def save_event(request):
    username = request.session.get("user")
    if not username:
        return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

    with connections["legacy"].cursor() as cursor:
        # Lấy id_user
        cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)
        user_id = row[0].strip()

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        event_id = data.get("event_id").strip()

        if not event_id:
            return JsonResponse({"status": "error", "message": "No event selected"}, status=400)
        
        title = data.get("title", "")
        author = data.get("author", "")
        notification = data.get("notification", "Disable")  # Enable / Disable
        repeat_type = data.get("repeat_time", "")
        due_date = data.get("due_time", None)
        time_created = data.get("created_time", None)
        shared_with = data.get("shared_list", "")
        detail = data.get("detail", "")

        # Tên của sự kiện sẽ được lưu
        title_to_update = title

        # Tác giả của sự kiện được lưu
        author_to_update = author

        # Thông báo của sự kiện được lưu
        notification_to_update = 1 if notification == "Enable" else 0

        # Loại lặp lại của sự kiện được lưu
        if repeat_type == "Each Week":
            repeat_type_to_update = "2000-01-01"  # Chỉ là một giá trị mặc định, không dùng đến
        elif repeat_type == "Each Month":
            repeat_type_to_update = "2000-01-02"
        elif repeat_type == "Each Year":
            repeat_type_to_update = "2000-01-03"
        elif repeat_type == "Each Day":
            repeat_type_to_update = "2000-01-04"
        else:
            match = re.search(r"\d+", repeat_type)
            if match:
                number = match.group()  # "5"
                year = number.zfill(4)  # luôn có 4 ký tự, thêm 0 ở trước nếu thiếu
                result = f"{year}-01-01"
            repeat_type_to_update = result

        # Thời hạn của sự kiện được lưu
        due_date_to_update = datetime.strptime(due_date, "%B %d, %Y at %I:%M %p")

        # Thời gian tạo của sự kiện được lưu
        time_created_to_update = datetime.strptime(time_created, "%b %d, %Y - %H:%M")

        # Danh sách người dùng được chia sẻ
        shared_with_to_update = shared_with

        # Chi tiết của sự kiện được lưu
        detail_to_update = detail

        # Cập nhật sự kiện trong cơ sở dữ liệu
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                UPDATE Events
                SET name_event = %s, detail = %s, time_event = %s, time_created = %s, loop = %s
                WHERE id_event = %s
            """, (title_to_update, detail_to_update, due_date_to_update, time_created_to_update, repeat_type_to_update, event_id))
        
        # Cập nhập notification
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                UPDATE Used_Eve
                SET notification = %s
                WHERE id_event = %s AND id_user = %s
            """, (int(notification_to_update), event_id, user_id))

        # Cập nhật danh sách người dùng được chia sẻ
        with connections["legacy"].cursor() as cursor:
            # Lấy toàn bộ id_user từ bảng Users
            cursor.execute("SELECT id_user FROM Users")
            all_users = {row[0].strip() for row in cursor.fetchall()}  # set để dễ so sánh

        # Lọc + loại trùng
        valid_shared_with = list({u for u in shared_with_to_update if u in all_users})

        # Xóa hết mọi người dùng đã chia sẻ
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                DELETE FROM Used_Eve
                WHERE id_event = %s
            """, [event_id])

        # Cập nhập lại mọi người dùng đã chia sẻ
        with connections["legacy"].cursor() as cursor:
            for id_of_user in valid_shared_with:
                if id_of_user == user_id:
                    cursor.execute("""
                        INSERT INTO Used_Eve (id_event, id_user, notification)
                        VALUES (%s, %s, %s)
                    """, (event_id, id_of_user, 1))  # notification mặc định là 1
                else:
                    cursor.execute("""
                        INSERT INTO Used_Eve (id_event, id_user, notification)
                        VALUES (%s, %s, %s)
                    """, (event_id, id_of_user, 0))  # notification mặc định là 0

        return JsonResponse({"status": "success", "message": "Event updated successfully"})


    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# Lấy sự kiện bị xóa và trả về cho máy chủ
@csrf_exempt
def get_deleted_events(request):
    username = request.session.get("user")

    with connections["legacy"].cursor() as cursor:
        # Lấy id_user
        cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
        row = cursor.fetchone()
        user_id = row[0]

    with connections["legacy"].cursor() as cursor:
        cursor.execute("""
            SELECT Events.id_event, Events.name_event
            FROM Creator_Eve, Events
            WHERE Creator_Eve.id_event = Events.id_event AND Creator_Eve.id_user = %s AND Events.in_trash = 1
        """, [user_id])
        rows = cursor.fetchall()

    # Ghép id và name thành string
    names = [f"{row[0]} - {row[1]}" for row in rows]

    return JsonResponse(names, safe=False)


# Khôi phục sự kiện
@csrf_exempt  # Nếu bạn chưa cấu hình CSRF token từ client thì cần cái này
def restore_event(request):
    if request.method == "POST":
        username = request.session.get("user")
        with connections["legacy"].cursor() as cursor:
            # Lấy id_user
            cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
            row = cursor.fetchone()
            user_id = row[0].strip() if row else None

        try:
            data = json.loads(request.body)
            event_name = data.get("eventName")
            event_id = event_name.split()[0].strip() if event_name else None

            if not event_name:
                return JsonResponse({"success": False, "error": "No event name provided"}, status=400)

            # Cập nhật database (ở đây giả sử bạn có cột deleted trong bảng events)
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    "UPDATE Events SET in_trash=0 WHERE id_event=%s",
                    [event_id]
                )

            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Used_Eve (id_event, id_user, notification) VALUES (%s, %s, %s)",
                    (event_id, user_id, 0)
                )


            # Kiểm tra xem có hàng nào được update không
            if cursor.rowcount == 0:
                return JsonResponse({"success": False, "error": "Event not found"}, status=404)

            return JsonResponse({"success": True})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

# Delete vĩnh viễn
@csrf_exempt
def delete_event1(request):
    if request.method == "POST":
        username = request.session.get("user")
        # Lấy user_id
        with connections["legacy"].cursor() as cursor:
            cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
            row = cursor.fetchone()
            user_id = row[0].strip() if row else None

        try:
            data = json.loads(request.body)
            event_name = data.get("eventName")
            event_id = event_name.split()[0].strip() if event_name else None

            if not event_id:
                return JsonResponse({"success": False, "error": "No event id provided"}, status=400)

            # Xóa sự kiện khỏi bảng Events
            with connections["legacy"].cursor() as cursor:
                cursor.execute("DELETE FROM Creator_Eve WHERE id_event = %s", [event_id])

            # Xóa sự kiện khỏi bảng Events
            with connections["legacy"].cursor() as cursor:
                cursor.execute("DELETE FROM Events WHERE id_event = %s", [event_id])

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

# Hàm lấy sự kiện trong ngày
def get_today_events():
    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT id_event, name_event, detail, time_event, time_created, loop
            FROM Events
            WHERE in_trash = 0
              AND CAST(time_event AS DATE) = CAST(GETDATE() AS DATE)
        """)
        return cursor.fetchall()

# Hàm cronjob (django-crontab sẽ gọi cái này)
def daily_event_reminder():
    with connections['legacy'].cursor() as cursor:
        events = get_today_events()
        for id_event, name_event, detail, time_event, time_created, loop in events:
            if loop == "2000-01-01":
                loop = "Each Week"
            elif loop == "2000-01-02":
                loop = "Each Month"
            elif loop == "2000-01-03":
                loop = "Each Year"
            elif loop == "2000-01-04":
                loop = "Each Day"
            else:
                loop = loop.year
                loop = f"Each {loop} days"

            # 1. Lấy các id_user và email liên quan đến event này
            cursor.execute("""
                SELECT u.id_user, u.email
                FROM Used_Eve ue
                JOIN Users u ON ue.id_user = u.id_user
                WHERE ue.id_event = %s
            """, [id_event])
            users = cursor.fetchall()

            if not users:
                continue  # Không có user nào thì bỏ qua

            # 2. Gửi mail đến từng user
            for id_user, email in users:
                send_mail(
                    subject=f"Event Reminder: {name_event}",
                    message=(
                        f"Hello,\n\n"
                        f"This is a friendly reminder that the event \"{name_event}\" is scheduled for {time_event}.\n\n"
                        f"Details: {detail}\n\n"
                        f"Please make sure to be prepared.\n\n"
                        f"Best regards,\n"
                        f"The Events Team"
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                    html_message = f"""
                    <!doctype html>
                    <html lang="en">
                    <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width">
                    <title>Event Reminder</title>
                    <style>
                        /* RESET */
                        body, table, td, a {{
                        -webkit-text-size-adjust:100%;
                        -ms-text-size-adjust:100%;
                        text-size-adjust:100%;
                        }}
                        table, td {{ border-collapse:collapse !important; }}
                        img {{ border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }}
                        a {{ text-decoration:none; }}
                        body {{
                        margin:0; padding:0; width:100% !important; height:100% !important;
                        background:#f0f8ff;
                        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                        color:#0f172a;
                        }}
                        /* CARD */
                        .card {{
                        background:#ffffff; 
                        border-radius:20px; 
                        overflow:hidden;
                        box-shadow:0 10px 30px rgba(15,23,42,0.15);
                        width:100%; 
                        max-width:680px;
                        text-align:center;
                        }}
                        /* HEADER */
                        .header {{
                        background: linear-gradient(135deg, #cce4f6 0%, #7db6e8 50%, #418cd6 100%);
                        padding:48px 24px 36px;
                        }}
                        .logo {{
                        width:72px; height:72px;
                        border-radius:50%;
                        background:#ffffff33;
                        display:inline-block;
                        line-height:72px;
                        font-size:36px;
                        margin-bottom:18px;
                        }}
                        .header h1 {{
                        margin:0; font-size:32px; font-weight:700; color:#ffffff;
                        }}
                        .header p {{
                        margin:14px 0 0; font-size:16px; color:#f1f5f9;
                        }}
                        /* SECTION */
                        .section {{
                        padding:36px 28px;
                        background:#f0f8ff;
                        }}
                        .info-block {{
                        margin:0 auto; padding:20px 0;
                        border-bottom:1px solid rgba(71,85,105,0.15);
                        }}
                        .info-block:last-child {{
                        border-bottom:none;
                        }}
                        .label {{
                        font-size:15px; font-weight:600; color:#334155; margin-bottom:6px;
                        }}
                        .value {{
                        font-size:17px; color:#0f172a; font-weight:500;
                        }}
                        /* TIMELINE */
                        .timeline {{
                        margin:32px auto 20px;
                        padding:0;
                        list-style:none;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        gap:60px;
                        position:relative;
                        width:fit-content;
                        }}
                        .timeline::before {{
                        content:"";
                        position:absolute;
                        top:50%;
                        left:0;
                        right:0;
                        height:4px;
                        background:#cbd5e1;
                        z-index:0;
                        }}
                        .timeline li {{
                        position:relative;
                        background:#ffffff;
                        border:3px solid #418cd6;
                        border-radius:50%;
                        width:26px;
                        height:26px;
                        z-index:1;
                        }}
                        /* NOTES */
                        .note {{
                        font-size:14px; color:#475569; margin-top:28px;
                        line-height:1.6;
                        }}
                        /* BUTTONS */
                        .btn {{
                        display:inline-block;
                        background:#418cd6;
                        color:#ffffff !important;
                        font-size:15px;
                        font-weight:600;
                        text-decoration:none;
                        padding:14px 28px;
                        border-radius:10px;
                        margin-top:24px;
                        }}
                        .btn-secondary {{
                        display:inline-block;
                        background:#e2e8f0;
                        color:#0f172a !important;
                        font-size:13px;
                        font-weight:500;
                        text-decoration:none;
                        padding:12px 24px;
                        border-radius:8px;
                        margin-top:14px;
                        }}
                        /* FOOTER */
                        .footer {{
                        padding:24px 24px; text-align:center; background:#f8fafc;
                        }}
                        .footer p {{
                        font-size:12px; color:#64748b; margin:6px 0;
                        }}
                        .footer a {{
                        color:#418cd6;
                        }}
                        /* DARK MODE */
                        @media (prefers-color-scheme: dark) {{
                        body {{ background:#0f172a !important; }}
                        .card {{ background:#1e293b !important; }}
                        .header {{ background: linear-gradient(135deg, #334155 0%, #475569 50%, #1e40af 100%) !important; }}
                        .header h1, .header p, .label, .value, .note, .footer p {{ color:#e2e8f0 !important; }}
                        .section {{ background:#1e293b !important; }}
                        .btn {{ background:#2563eb !important; }}
                        .btn-secondary {{ background:#334155 !important; color:#e2e8f0 !important; }}
                        .timeline::before {{ background:#475569 !important; }}
                        }}
                    </style>
                    </head>
                    <body>
                    <!-- WRAPPER TABLE FOR CENTERING -->
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" height="100%" style="height:100vh; min-height:100%; width:100%;">
                        <tr>
                        <td align="center" valign="middle">
                            <!-- CARD -->
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" class="card">
                            <!-- HEADER -->
                            <tr>
                                <td class="header">
                                <div class="logo">📅</div>
                                <h1>Event Reminder</h1>
                                <p>Your scheduled event is happening soon</p>
                                </td>
                            </tr>
                            <!-- CONTENT -->
                            <tr>
                                <td class="section">
                                <div class="info-block">
                                    <div class="label">Event Title</div>
                                    <div class="value">{name_event}</div>
                                </div>
                                <div class="info-block">
                                    <div class="label">Event Details</div>
                                    <div class="value">{detail}</div>
                                </div>
                                <div class="info-block">
                                    <div class="label">Created At</div>
                                    <div class="value">{time_created}</div>
                                </div>
                                <div class="info-block">
                                    <div class="label">Repeat Time</div>
                                    <div class="value">{loop}</div>
                                </div>
                                <div class="info-block">
                                    <div class="label">Event Due</div>
                                    <div class="value">{time_event}</div>
                                </div>
                                <div class="info-block">
                                    <div class="label">Event ID</div>
                                    <div class="value">{event_id}</div>
                                </div>

                                <!-- Timeline -->
                                <ul class="timeline">
                                    <li></li><li></li><li></li>
                                </ul>

                                <!-- Note -->
                                <p class="note">
                                    Check your Lucenda dashboard for any last-minute updates.
                                </p>

                                <!-- Buttons -->
                                <a href="http://127.0.0.1:8000/calendar/day-view/" class="btn">View in Calendar</a><br>
                                <a href=http://127.0.0.1:8000/event/main-event/" class="btn-secondary">Edit or Cancel Event</a>
                                </td>
                            </tr>
                            <!-- FOOTER -->
                            <tr>
                                <td class="footer">
                                <p>© 2025 Lucenda. All rights reserved.</p>
                                </td>
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                    </body>
                    </html>
                    """

                )

# Cập nhật tên người dùng
@csrf_exempt
def update_username(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            new_username = data.get("username")
            
            if not new_username:
                return JsonResponse({"error": "Username is required"}, status=400)

            with connections['legacy'].cursor() as cursor:
                # 🚧 Kiểm tra username đã tồn tại chưa
                cursor.execute("SELECT COUNT(*) FROM Users WHERE account = %s", [new_username])
                count = cursor.fetchone()[0]

                if count > 0:
                    return JsonResponse({"error": "Username already exists", "username_exists": True}, status=409)

                # 🚧 Cập nhật username
                cursor.execute("UPDATE Users SET account = %s WHERE account = %s", [new_username, request.session.get("user")])
                # 🚧 Cập nhật account
                cursor.execute("UPDATE Users SET name = %s WHERE name = %s", [new_username, request.session.get("user")])

            request.session["user"] = new_username
            return JsonResponse({"message": "Username updated successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)

# Cập nhập lịch về client
@csrf_exempt
def calendar_list(request):
    username = request.session.get("user")
    if not username:
        return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

    try:
        with connections["legacy"].cursor() as cursor:
            # Lấy id_user
            cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({"status": "error", "message": "User not found"}, status=404)
            user_id = row[0]

            # Lấy các id_event user có quyền
            cursor.execute("""
                SELECT id_calendar
                FROM Used_Calen
                WHERE id_user = %s
            """, [user_id])
            id_calendars = [r[0] for r in cursor.fetchall()]

            if not id_calendars:
                return JsonResponse([], safe=False, status=200)

            # Lấy id_event + name_event trong Events theo các id trên
            placeholders = ",".join(["%s"] * len(id_calendars))
            cursor.execute(f"""
                SELECT id_calendar, name_calendar
                FROM Calendars
                WHERE id_calendar IN ({placeholders})
                  AND in_trash = 0
                ORDER BY time_created DESC
            """, id_calendars)
            rows = cursor.fetchall()

            # Trả về list chuỗi "id - name"
            calendars = [f"{row[0]} - {row[1]}" for row in rows]
            data = [{"name_calendar": f"{row[0]} - {row[1]}"} for row in rows]

        return JsonResponse(data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# Tạo lịch mới
@csrf_exempt
def create_calendar(request):
    if request.method == "POST":
        username = request.session.get('user')  # Lấy username từ session
        print(username)
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        with connections["legacy"].cursor() as cursor:
            cursor.execute(
                "SELECT id_user FROM Users WHERE account = %s",
                [username]
            )
            row = cursor.fetchone()

        if not row:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)

        user_id = row[0]  # mã ID của user

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        calendar_name = data.get("name", "").strip()
        if not calendar_name:
            return JsonResponse({"status": "error", "message": "Calendar name is required"}, status=400)

        try:
            # Create new id_calendar
            with connections['legacy'].cursor() as cursor:
                cursor.execute("SELECT TOP 1 id_calendar FROM Calendars ORDER BY id_calendar DESC")
                last_id = cursor.fetchone()
                new_id = f"C{int(last_id[0][1:]) + 1:03d}" if last_id else "C001"

            # Cập nhập bảng calendars
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Calendars (id_calendar, name_calendar, time_created, in_trash)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [new_id, calendar_name, timezone.now() + timedelta(hours=7), 0]
                )

            # Cập nhập bảng created calendars
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Creator_Calen (id_user, id_calendar)
                    VALUES (%s, %s)
                    """,
                    [user_id, new_id]
                )

            # Cập nhập bảng used calendars
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Used_Calen (id_user, id_calendar)
                    VALUES (%s, %s)
                    """,
                    [user_id, new_id]
                )

            return JsonResponse({"status": "success"}, status=201)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Xóa lịch
@csrf_exempt  # (nếu bạn test bằng fetch, nên dùng. Khi production thì nên xài CSRF token)
def delete_calendar(request):
    if request.method == "POST":
        username = request.session.get("user")
        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

        try:
            with connections["legacy"].cursor() as cursor:
                # Lấy id_user
                cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({"status": "error", "message": "User not found"}, status=404)
                user_id = row[0]

            data = json.loads(request.body)
            calendar_name = data.get("name")
            match = re.match(r"^(\S+)", calendar_name)
            calendar_id = match.group(1) if match else None

            if not calendar_name:
                return JsonResponse({"error": "Thiếu tên lịch"}, status=400)

            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    SELECT id_user
                    FROM Creator_Calen
                    WHERE id_calendar = %s
                """, [calendar_id])

                creator_row = cursor.fetchone()
                if not creator_row:
                    return JsonResponse({"error": "Không tìm thấy người tạo lịch"}, status=404)
                creator_id = creator_row[0]

                if creator_id != user_id:
                    return JsonResponse({"error": "Bạn không có quyền xoá lịch này"}, status=403)

            # --- SQL xoá lịch ---
            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Used_Calen
                    WHERE id_calendar = %s
                """, [calendar_id])

            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    UPDATE Calendars
                    SET in_trash = 1
                    WHERE id_calendar = %s
                """, [calendar_id])

            return JsonResponse({"message": f"Đã xoá lịch {calendar_name}"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)

# Đổi tên lịch
@csrf_exempt
def rename_calendar(request):
    print("Renaming calendar...")
    if request.method != "POST":
        return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)

    try:
        username = request.session.get("user")
        if not username:
            return JsonResponse({"error": "Not logged in"}, status=403)

        data = json.loads(request.body)
        old_name = data.get("old_name")
        new_name = data.get("new_name")

        if not old_name or not new_name:
            return JsonResponse({"error": "Thiếu tham số"}, status=400)

        # --- Tách id và tên lịch ---
        try:
            calendar_id, old_title = old_name.split(" - ", 1)
            calendar_id = calendar_id.strip()
            old_title = old_title.strip()
        except ValueError:
            return JsonResponse({"error": "Định dạng old_name không hợp lệ"}, status=400)

        # --- Tự viết SQL ở đây ---
        with connections["legacy"].cursor() as cursor:
            # ví dụ: cập nhật bảng Calendars
            cursor.execute("""
                UPDATE Calendars
                SET name_calendar = %s
                WHERE id_calendar = %s
            """, [new_name, calendar_id])

        return JsonResponse({"message": f"Đã đổi tên từ '{old_name}' thành '{new_name}'"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# Chia sẻ lịch
@csrf_exempt
def share_calendar(request):
    username = request.session.get("user")
    if not username:
        return JsonResponse({"status": "error", "message": "Not logged in"}, status=403)

    with connections["legacy"].cursor() as cursor:
        # Lấy id_user
        cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)
        user_id = row[0].strip()

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        old_name = data.get("calendar_id").strip()

        try:
            calendar_id, old_title = old_name.split(" - ", 1)
            calendar_id = calendar_id.strip()
            old_title = old_title.strip()
        except ValueError:
            return JsonResponse({"error": "Định dạng old_name không hợp lệ"}, status=400)

        if not calendar_id:
            return JsonResponse({"status": "error", "message": "No calendar selected"}, status=400)

        shared_with = data.get("shared_list", "")

        # Cập nhật danh sách người dùng được chia sẻ
        with connections["legacy"].cursor() as cursor:
            # Lấy toàn bộ id_user từ bảng Users
            cursor.execute("SELECT id_user FROM Users")
            all_users = {row[0].strip() for row in cursor.fetchall()}  # set để dễ so sánh

        # Lọc + loại trùng
        valid_shared_with = list({u for u in shared_with if u in all_users})

        # Xóa hết mọi người dùng đã chia sẻ
        with connections["legacy"].cursor() as cursor:
            cursor.execute("""
                DELETE FROM Used_Calen
                WHERE id_calendar = %s
            """, [calendar_id])

        # Cập nhập lại mọi người dùng đã chia sẻ
        with connections["legacy"].cursor() as cursor:
            for id_of_user in valid_shared_with:
                cursor.execute("""
                    INSERT INTO Used_Calen (id_calendar, id_user)
                    VALUES (%s, %s)
                """, (calendar_id, id_of_user))

        return JsonResponse({"status": "success", "message": "Event updated successfully"})


    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# Lấy lịch bị xóa và trả về cho máy khách
# Lấy sự kiện bị xóa và trả về cho máy chủ
@csrf_exempt
def get_deleted_events_1(request):
    username = request.session.get("user")

    with connections["legacy"].cursor() as cursor:
        # Lấy id_user
        cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
        row = cursor.fetchone()
        user_id = row[0]

    with connections["legacy"].cursor() as cursor:
        cursor.execute("""
            SELECT Calendars.id_calendar, Calendars.name_calendar
            FROM Creator_Calen, Calendars
            WHERE Creator_Calen.id_calendar = Calendars.id_calendar AND Creator_Calen.id_user = %s AND Calendars.in_trash = 1
        """, [user_id])
        rows = cursor.fetchall()

    # Ghép id và name thành string
    names = [f"{row[0]} - {row[1]}" for row in rows]

    return JsonResponse(names, safe=False)

# Khôi phục sự kiện
@csrf_exempt  # Nếu bạn chưa cấu hình CSRF token từ client thì cần cái này
def restore_event_1(request):
    if request.method == "POST":
        username = request.session.get("user")
        with connections["legacy"].cursor() as cursor:
            # Lấy id_user
            cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
            row = cursor.fetchone()
            user_id = row[0].strip() if row else None

        try:
            data = json.loads(request.body)
            event_name = data.get("eventName")
            event_id = event_name.split()[0].strip() if event_name else None

            if not event_name:
                return JsonResponse({"success": False, "error": "No event name provided"}, status=400)

            # Cập nhật database (ở đây giả sử bạn có cột deleted trong bảng events)
            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    "UPDATE Calendars SET in_trash=0 WHERE id_calendar=%s",
                    [event_id]
                )

            with connections["legacy"].cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Used_Calen (id_calendar, id_user) VALUES (%s, %s)",
                    (event_id, user_id)
                )


            # Kiểm tra xem có hàng nào được update không
            if cursor.rowcount == 0:
                return JsonResponse({"success": False, "error": "Event not found"}, status=404)

            return JsonResponse({"success": True})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

# Delete vĩnh viễn
@csrf_exempt
def delete_event1_1(request):
    if request.method == "POST":
        username = request.session.get("user")
        # Lấy user_id
        with connections["legacy"].cursor() as cursor:
            cursor.execute("SELECT id_user FROM Users WHERE account = %s", [username])
            row = cursor.fetchone()
            user_id = row[0].strip() if row else None

        try:
            data = json.loads(request.body)
            event_name = data.get("eventName")
            event_id = event_name.split()[0].strip() if event_name else None

            if not event_id:
                return JsonResponse({"success": False, "error": "No event id provided"}, status=400)

            # Xóa sự kiện khỏi bảng Events
            with connections["legacy"].cursor() as cursor:
                cursor.execute("DELETE FROM Creator_Calen WHERE id_calendar = %s", [event_id])

            # Xóa sự kiện khỏi bảng Events
            with connections["legacy"].cursor() as cursor:
                cursor.execute("DELETE FROM Calendars WHERE id_calendar = %s", [event_id])

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

# API cho lịch sự kiện
def event_calendar_api(request):
    calendar_id = request.GET.get("calendar_id")  # <-- đọc từ query string
    if not calendar_id:
        return JsonResponse([], safe=False)

    calendar_id = calendar_id.strip()  # Loại bỏ khoảng trắng
    data = []

    with connections["legacy"].cursor() as cursor:
        # Lấy toàn bộ sự kiện của lịch này và hiển thị chúng
        cursor.execute("""
            SELECT Events.id_event, Events.name_event, Events.time_event, Events.detail
            FROM Include, Events
            WHERE Include.id_event = Events.id_event AND Include.id_calendar = %s
        """, [calendar_id])
        events = cursor.fetchall()

        for row in events:
            event = {
                "id": row[0],
                "title": row[1] + " : " + row[3],
                "start": row[2].isoformat(),
                "end": (row[2] + timedelta(hours=1)).isoformat(),
            }
            data.append(event)

    return JsonResponse(data, safe=False)

# Hiển thị sự kiện ở phần tìm kiếm
def get_events_1(request):
    user_name = request.session.get("user")  # lấy từ session

    with connections["legacy"].cursor() as cursor:
        cursor.execute("SELECT id_user FROM Users WHERE account = %s", [user_name])
        row = cursor.fetchone()
        user_id = row[0].strip() if row else None

    with connections["legacy"].cursor() as cursor:
        cursor.execute("""
            SELECT Events.id_event, Events.name_event
            FROM Used_Eve, Events
            WHERE Used_Eve.id_event = Events.id_event AND Used_Eve.id_user = %s
        """, [user_id])
        
        rows = cursor.fetchall()

    # Chuyển thành list of dict
    data = []
    for row in rows:
        data.append(row[0] + ": " + row[1])

    return JsonResponse(data, safe=False)

# Thêm event vào lịch
@csrf_exempt   # cho phép gọi từ fetch (nếu chưa set CSRF token)
def add_event(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            event_name = data.get("eventName")
            calendar_id = str(data.get("calendarId")).strip() if data.get("calendarId") else None

            if not event_name or not calendar_id:
                return JsonResponse({"success": False, "error": "Missing eventName or calendarId"})


            # Tách event_id và title bằng regex
            match = re.match(r"^(E\d+)\s*:\s*(.+)$", event_name.strip())
            if not match:
                return JsonResponse({"success": False, "error": "Invalid eventName format"})


            event_id, event_title = match.groups()

            print(event_id, calendar_id, event_title)
            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    SELECT CASE WHEN EXISTS (
                        SELECT 1
                        FROM [Include]
                        WHERE UPPER(LTRIM(RTRIM([id_event]))) = %s
                        AND [id_calendar] = %s
                    ) THEN 1 ELSE 0 END AS exists_flag
                """, [event_id, calendar_id])
                exists = cursor.fetchone()[0] == 1

            if exists:
                return JsonResponse({
                    "success": False,
                    "error": f"Event {event_id} already exists in calendar {calendar_id}"
                })

            # Nếu chưa có → thêm mới vào Include
            with connections["legacy"].cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Include (id_event, id_calendar)
                    VALUES (%s, %s)
                """, [event_id, calendar_id])

            return JsonResponse({
                "success": True,
                "message": f'Event "{event_title}" added to calendar {calendar_id}',
                "eventId": event_id,
                "eventTitle": event_title,
                "calendarId": calendar_id
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})