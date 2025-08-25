# Lucenda's Website Source code and Documentation

## Requirements

Các thư viện cần thiết được định nghĩa trong `requirements.txt`:

```
Django>=4.2
python-dotenv
djangorestframework
django-crontab
social-auth-app-django
validate-email-address
mssql-django
pyodbc
groq
openai
```

## Hướng dẫn cài đặt và chạy dự án

### 1. Tạo môi trường ảo
```bash
python -m venv venv
```

### 2. Kích hoạt môi trường ảo
- **Windows (CMD):**
```bash
venv\Scripts\activate
```
- **Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```
- **Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 4. Chạy migrate
```bash
python manage.py migrate
```

### 5. Khởi chạy server
```bash
python manage.py runserver
```

Mặc định server sẽ chạy tại [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
