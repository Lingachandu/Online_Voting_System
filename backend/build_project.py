import os

# Define the complete file contents to match the architecture exactly
FILES_DATA = {
    # Main project settings
    "backend/myproject/__init__.py": "",
    "backend/myproject/wsgi.py": "# WSGI Configuration",
    "backend/myproject/urls.py": """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('backend.apps.authentication.urls')),
    path('', include('backend.apps.elections.urls')),
    path('', include('backend.apps.voting.urls')),
]""",
    "backend/myproject/settings.py": """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'django-insecure-voting-key'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend.apps.authentication',
    'backend.apps.elections',
    'backend.apps.voting',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.myproject.urls'
AUTH_USER_MODEL = 'authentication.CustomUser'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'frontend', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'frontend', 'static')]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""",

    # Apps core modules
    "backend/apps/__init__.py": "",
    "backend/apps/authentication/__init__.py": "",
    "backend/apps/authentication/urls.py": """from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
]""",
    "backend/apps/authentication/models.py": """from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (('admin', 'Admin'), ('voter', 'Voter'))
    username = None
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='voter')
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['role']

class OTPVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_expired = models.BooleanField(default=False)
""",
    "backend/apps/authentication/views.py": """from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .models import CustomUser, OTPVerification
import random

def login_view(request):
    if request.method == "POST":
        phone = request.POST.get('phone_number')
        role = request.POST.get('role')
        user, _ = CustomUser.objects.get_or_create(phone_number=phone, defaults={'role': role})
        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(user=user, otp_code=otp)
        request.session['pre_auth_phone'] = phone
        print(f"\\n--- MOCK SMS OUTBOX: OTP FOR {phone} IS {otp} ---\\n")
        return redirect('verify_otp')
    return render(request, 'authentication/login.html')

def verify_otp_view(request):
    phone = request.session.get('pre_auth_phone')
    if not phone: return redirect('login')
    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(phone_number=phone)
            OTPVerification.objects.filter(user=user, otp_code=otp_entered, is_expired=False).latest('created_at')
            user.is_verified = True; user.save()
            login(request, user)
            del request.session['pre_auth_phone']
            return redirect('admin_dashboard' if user.role == 'admin' else 'voter_dashboard')
        except:
            return render(request, 'authentication/verify_otp.html', {'error': 'Invalid OTP'})
    return render(request, 'authentication/verify_otp.html')

def logout_view(request):
    logout(request); return redirect('login')
""",

    "backend/apps/elections/__init__.py": "",
    "backend/apps/elections/urls.py": """from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/voter/', views.voter_dashboard, name='voter_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
]""",
    "backend/apps/elections/models.py": """from django.db import models

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=100)
    party_affinity = models.CharField(max_length=100, blank=True)
    votes_count = models.IntegerField(default=0)
""",
    "backend/apps/elections/views.py": """from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Election
from backend.apps.voting.models import Vote

@login_required
def voter_dashboard(request):
    elections = Election.objects.filter(is_active=True)
    voted = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)
    return render(request, 'elections/voter_dashboard.html', {'elections': elections, 'voted_elections': voted})

@login_required
def admin_dashboard(request):
    return render(request, 'elections/admin_dashboard.html', {'elections': Election.objects.all()})
""",

    "backend/apps/voting/__init__.py": "",
    "backend/apps/voting/urls.py": """from django.urls import path
from . import views
urlpatterns = [path('cast-vote/<int:election_id>/', views.cast_vote, name='cast_vote')]""",
    "backend/apps/voting/models.py": """from django.db import models
from backend.apps.authentication.models import CustomUser
from backend.apps.elections.models import Election, Candidate

class Vote(models.Model):
    voter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('voter', 'election')
""",
    "backend/apps/voting/views.py": """from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from backend.apps.elections.models import Election, Candidate
from .models import Vote

@login_required
def cast_vote(request, election_id):
    if request.method == "POST" and request.user.role == 'voter':
        candidate_id = request.POST.get('candidate')
        election = get_object_or_404(Election, id=election_id, is_active=True)
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)
        if not Vote.objects.filter(voter=request.user, election=election).exists():
            Vote.objects.create(voter=request.user, election=election, candidate=candidate)
            candidate.votes_count += 1; candidate.save()
    return redirect('voter_dashboard')
""",

    # Frontend Assets
    "frontend/static/css/style.css": """body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
header { background: #1e3a8a; color: white; padding: 15px 30px; display: flex; justify-content: space-between; }
.container { max-width: 600px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.btn { background: #2563eb; color: white; border: none; padding: 10px; width: 100%; font-weight: bold; cursor: pointer; border-radius: 4px; }
.card { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 4px; }""",
    
    "frontend/static/js/main.js": "console.log('Voting System Initialized');",
    
    # HTML Layout Templates
    "frontend/templates/base.html": """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>Voting System</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header>
        <h2>🗳️ Online Voting System</h2>
        {% if user.is_authenticated %}<a href="{% url 'logout' %}" style="color:white;">Logout</a>{% endif %}
    </header>
    {% block content %}{% endblock %}
</body>
</html>""",

    "frontend/templates/authentication/login.html": """{% extends 'base.html' %}
{% block content %}
<div class="container">
    <h2>Login Portal</h2>
    <form method="POST">
        {% csrf_token %}
        <div class="form-group">
            <label>Select Role</label>
            <select name="role"><option value="voter">Voter</option><option value="admin">Admin</option></select>
        </div>
        <div class="form-group">
            <label>Mobile Number</label>
            <input type="tel" name="phone_number" required placeholder="+123456789">
        </div>
        <button type="submit" class="btn">Generate OTP</button>
    </form>
</div>
{% endblock %}""",

    "frontend/templates/authentication/verify_otp.html": """{% extends 'base.html' %}
{% block content %}
<div class="container">
    <h2>Verify OTP</h2>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
    <form method="POST">
        {% csrf_token %}
        <div class="form-group">
            <label>Enter Code (Check your server command terminal output)</label>
            <input type="text" name="otp" required>
        </div>
        <button type="submit" class="btn">Verify</button>
    </form>
</div>
{% endblock %}""",

    "frontend/templates/elections/voter_dashboard.html": """{% extends 'base.html' %}
{% block content %}
<div class="container">
    <h2>Voter Dashboard</h2>
    {% for election in elections %}
    <div class="card">
        <h3>{{ election.title }}</h3>
        {% if election.id in voted_elections %}
            <p style="color:green; font-weight:bold;">✓ Vote Casted Successfully</p>
        {% else %}
            <form method="POST" action="{% url 'cast_vote' election.id %}">
                {% csrf_token %}
                {% for cand in election.candidates.all %}
                    <p><input type="radio" name="candidate" value="{{ cand.id }}"> {{ cand.name }} ({{ cand.party_affinity }})</p>
                {% endfor %}
                <button type="submit" class="btn" style="background:green;">Submit Vote</button>
            </form>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}""",

    "frontend/templates/elections/admin_dashboard.html": """{% extends 'base.html' %}
{% block content %}
<div class="container">
    <h2>Admin Audit Dashboard</h2>
    {% for election in elections %}
    <div class="card">
        <h3>{{ election.title }}</h3>
        <ul>
            {% for cand in election.candidates.all %}
                <li><strong>{{ cand.name }}</strong>: {{ cand.votes_count }} votes</li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}
</div>
{% endblock %}""",

    "backend/manage.py": """#!/usr/bin/env python
import os, sys
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.myproject.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)"""
}

def build():
    for path, content in FILES_DATA.items():
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
    print("🚀 Project folder architecture generated completely with zero missing files!")

if __name__ == '__main__':
    build()