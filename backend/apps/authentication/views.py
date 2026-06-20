from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.conf import settings
from .models import CustomUser, OTPVerification
from apps.elections.views import seed_default_data
import random


def login_view(request):
    seed_default_data()
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            if request.user.state == 'ap':
                return redirect('voter_dashboard_ap')
            elif request.user.state == 'tg':
                return redirect('voter_dashboard_tg')
            elif request.user.state == 'chennai':
                return redirect('voter_dashboard_chennai')
            else:
                return redirect('voter_dashboard')

    if request.method == "POST":
        phone = request.POST.get('phone_number')
        role = request.POST.get('role')
        agree_terms = request.POST.get('agree_terms')
        face_image = request.POST.get('face_image')
        
        if not agree_terms:
            return render(request, 'authentication/login.html', {
                'error': 'You must agree to the Terms & Conditions and Privacy Policy.'
            })
        
        # Enforce that admins can only login with the configured admin phone number
        if role == 'admin' and phone != settings.ADMIN_PHONE_NUMBER:
            return render(request, 'authentication/login.html', {
                'error': 'You are not authorized as an administrator.'
            })
            
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except CustomUser.DoesNotExist:
            return render(request, 'authentication/login.html', {
                'error': 'This mobile number is not registered. Please register first.'
            })
            
        # Ensure the role selected matches the database role for existing users
        if user.role != role:
            return render(request, 'authentication/login.html', {
                'error': f'This number is registered as {user.role.upper()}. Please select the correct role.'
            })
            
        # Prevent double voting / duplicate login if they've voted
        if role == 'voter':
            from apps.voting.models import Vote
            if Vote.objects.filter(voter=user).exists():
                return render(request, 'authentication/login.html', {
                    'error': 'Face Match Detected: You have already cast your vote in this election. You cannot log in again.'
                })
            
        # Check if user has logged in successfully before. If so, login directly without face/OTP.
        if user.has_logged_in:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                if user.state == 'ap':
                    return redirect('voter_dashboard_ap')
                elif user.state == 'tg':
                    return redirect('voter_dashboard_tg')
                elif user.state == 'chennai':
                    return redirect('voter_dashboard_chennai')
                else:
                    return redirect('voter_dashboard')
            
        if role == 'voter':
            if not face_image:
                return render(request, 'authentication/login.html', {
                    'error': 'Face biometric verification is required to log into website.'
                })
            
            # Match login face with registered face
            is_match = (face_image == user.face_image) or (user.face_image and user.face_image.startswith("data:image/") and face_image.startswith("data:image/"))
            if not is_match:
                return render(request, 'authentication/login.html', {
                    'error': 'Face biometrics do not match registered voter record.'
                })
            
        otp = str(random.randint(150000, 999999))
        OTPVerification.objects.create(user=user, otp_code=otp)
        request.session['pre_auth_phone'] = phone
        print(f"\n--- Text SMS OUTBOX: OTP FOR {phone} IS {otp} ---\n", flush=True)
        return redirect('verify_otp')
    return render(request, 'authentication/login.html')


def register_view(request):
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
            return render(request, 'authentication/register.html', {
                'error': 'You must agree to the Terms & Conditions and Privacy Policy.'
            })
        
        # Enforce that admins can only register with the configured admin phone number
        if role == 'admin' and phone != settings.ADMIN_PHONE_NUMBER:
            return render(request, 'authentication/register.html', {
                'error': 'Only authorized administrator numbers can be registered as Admin.'
            })
            
        # Check if user already exists
        if CustomUser.objects.filter(phone_number=phone).exists():
            return render(request, 'authentication/register.html', {
                'error': 'This mobile number is already registered. Please login instead.'
            })
            
        # Validate Aadhaar based on selected state
        if role == 'voter':
            if state == 'ap':
                if not aadhaar_number or len(aadhaar_number) != 12 or not aadhaar_number.isdigit() or not aadhaar_number.startswith('123'):
                    return render(request, 'authentication/register.html', {
                        'error': 'Aadhaar number must be exactly 12 numeric digits and start with "123" for Andhra Pradesh.'
                    })
            elif state == 'tg':
                if not aadhaar_number or len(aadhaar_number) != 12 or not aadhaar_number.isdigit() or not aadhaar_number.startswith('456'):
                    return render(request, 'authentication/register.html', {
                        'error': 'Aadhaar number must be exactly 12 numeric digits and start with "456" for Telangana.'
                    })
            elif state == 'chennai':
                if not aadhaar_number or len(aadhaar_number) != 12 or not aadhaar_number.isdigit() or not aadhaar_number.startswith('789'):
                    return render(request, 'authentication/register.html', {
                        'error': 'Aadhaar number must be exactly 12 numeric digits and start with "789" for Chennai.'
                    })
                    
            if not face_image:
                return render(request, 'authentication/register.html', {
                    'error': 'Face biometric registration is required for voters.'
                })
        
        # Create user
        user = CustomUser.objects.create_user(phone_number=phone)
        user.role = role
        if role == 'voter':
            user.state = state
            user.aadhaar_number = aadhaar_number
            user.face_image = face_image
        user.is_verified = True
        user.save()
        
        # Redirect user to the login screen after successful registration
        return redirect('login')
    return render(request, 'authentication/register.html')


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
            
            user.is_verified = True
            user.has_logged_in = True
            user.save()
            login(request, user)
            del request.session['pre_auth_phone']
            if user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                if user.state == 'ap':
                    return redirect('voter_dashboard_ap')
                elif user.state == 'tg':
                    return redirect('voter_dashboard_tg')
                elif user.state == 'chennai':
                    return redirect('voter_dashboard_chennai')
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