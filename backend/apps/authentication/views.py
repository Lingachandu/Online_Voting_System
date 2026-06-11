from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .models import CustomUser, OTPVerification
from apps.elections.views import seed_default_data
import random


def login_view(request):
    seed_default_data()
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('voter_dashboard')

    if request.method == "POST":
        phone = request.POST.get('phone_number')
        role = request.POST.get('role')
        agree_terms = request.POST.get('agree_terms')
        state = request.POST.get('state')
        aadhaar_number = request.POST.get('aadhaar_number')
        face_image = request.POST.get('face_image')
        
        if not agree_terms:
            return render(request, 'authentication/login.html', {
                'error': 'You must agree to the Terms & Conditions and Privacy Policy.'
            })
        
        # Enforce that admins can only login with phone number 9876543210
        if role == 'admin' and phone != '9876543210':
            return render(request, 'authentication/login.html', {
                'error': 'You are not admin'
            })
            
        # Validate Aadhaar based on selected state
        if role == 'voter':
            if state == 'ap':
                if not aadhaar_number or len(aadhaar_number) != 12 or not aadhaar_number.isdigit() or not aadhaar_number.startswith('123'):
                    return render(request, 'authentication/login.html', {
                        'error': 'Aadhaar number must be exactly 12 numeric digits and start with "123" for Andhra Pradesh.'
                    })
            elif state == 'tg':
                if not aadhaar_number or len(aadhaar_number) != 12 or not aadhaar_number.isdigit() or not aadhaar_number.startswith('456'):
                    return render(request, 'authentication/login.html', {
                        'error': 'Aadhaar number must be exactly 12 numeric digits and start with "456" for Telangana.'
                    })
            elif state == 'chennai':
                if not aadhaar_number or len(aadhaar_number) != 12 or not aadhaar_number.isdigit() or not aadhaar_number.startswith('789'):
                    return render(request, 'authentication/login.html', {
                        'error': 'Aadhaar number must be exactly 12 numeric digits and start with "789" for Chennai.'
                    })
        
        user, _ = CustomUser.objects.get_or_create(phone_number=phone, defaults={'role': role})
        
        # Ensure the role selected matches the database role for existing users
        if user.role != role:
            return render(request, 'authentication/login.html', {
                'error': f'This number is registered as {user.role.upper()}. Please select the correct role.'
            })
            
        # Update user's state, Aadhaar number, and face image in the database profile
        if role == 'voter':
            if face_image:
                if not user.face_image:
                    # First login: store the captured face image
                    user.face_image = face_image
                else:
                    # SECOND LOGIN ATTEMPT DETECTED — face already registered
                    # Block immediately regardless of whether they've voted
                    return render(request, 'authentication/login.html', {
                        'error': '🚫 Duplicate Login Detected: Your face biometric is already registered in our system. You are attempting to access the portal a second time. This session has been blocked to prevent fraudulent access. If this is an error, contact the Election Commission.'
                    })
            user.state = state
            user.aadhaar_number = aadhaar_number
            user.save()

            
        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(user=user, otp_code=otp)
        request.session['pre_auth_phone'] = phone
        print(f"\n--- MOCK SMS OUTBOX: OTP FOR {phone} IS {otp} ---\n", flush=True)
        return redirect('verify_otp')
    return render(request, 'authentication/login.html')

def verify_otp_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('voter_dashboard')

    phone = request.session.get('pre_auth_phone')
    if not phone: return redirect('login')
    
    latest_verification = None
    try:
        user = CustomUser.objects.get(phone_number=phone)
        latest_verification = OTPVerification.objects.filter(user=user, is_expired=False).latest('created_at')
    except (CustomUser.DoesNotExist, OTPVerification.DoesNotExist):
        pass

    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(phone_number=phone)
            verification = OTPVerification.objects.filter(user=user, otp_code=otp_entered, is_expired=False).latest('created_at')
            verification.is_expired = True
            verification.save()
            
            user.is_verified = True; user.save()
            login(request, user)
            del request.session['pre_auth_phone']
            if user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('voter_dashboard')
        except:
            return render(request, 'authentication/verify_otp.html', {
                'error': 'Invalid OTP',
                'demo_otp': latest_verification.otp_code if latest_verification else None
            })
            
    return render(request, 'authentication/verify_otp.html', {
        'demo_otp': latest_verification.otp_code if latest_verification else None
    })

def logout_view(request):
    logout(request); return redirect('login')

def terms_view(request):
    return render(request, 'authentication/terms.html')

def privacy_view(request):
    return render(request, 'authentication/privacy.html')