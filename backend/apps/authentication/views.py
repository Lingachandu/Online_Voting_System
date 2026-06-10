from django.shortcuts import render, redirect
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
        print(f"\n--- MOCK SMS OUTBOX: OTP FOR {phone} IS {otp} ---\n")
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