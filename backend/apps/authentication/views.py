from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.conf import settings
from .models import CustomUser
from apps.elections.views import seed_default_data

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
        full_name = request.POST.get('full_name', '').strip()
        
        if not agree_terms:
            return render(request, 'authentication/login.html', {
                'error': 'You must agree to the Terms & Conditions and Privacy Policy.'
            })
        
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
            
        if user.role != role:
            return render(request, 'authentication/login.html', {
                'error': f'This number is registered as {user.role.upper()}. Please select the correct role.'
            })

        if user.role == 'admin':
            user.has_logged_in = True
            user.save()
            login(request, user)
            return redirect('admin_dashboard')

        if not full_name:
            return render(request, 'authentication/login.html', {
                'error': 'Full name is required for Voter login.'
            })

        user.first_name = full_name
        user.save()

        request.session['pre_auth_phone'] = phone
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
        
        if not agree_terms:
            return render(request, 'authentication/register.html', {
                'error': 'You must agree to the Terms & Conditions and Privacy Policy.'
            })
        
        if role == 'admin' and phone != settings.ADMIN_PHONE_NUMBER:
            return render(request, 'authentication/register.html', {
                'error': 'Only authorized administrator numbers can be registered as Admin.'
            })
            
        if CustomUser.objects.filter(phone_number=phone).exists():
            existing_user = CustomUser.objects.get(phone_number=phone)
            if not existing_user.is_verified:
                if not existing_user.totp_secret:
                    from .otp import generate_totp_secret
                    existing_user.totp_secret = generate_totp_secret()
                    existing_user.save()
                request.session['pre_auth_phone'] = phone
                return redirect('verify_otp')
                
            return render(request, 'authentication/register.html', {
                'error': 'This mobile number is already registered. Please login instead.'
            })
            
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
        
        user = CustomUser.objects.create_user(phone_number=phone)
        user.role = role
        user.is_verified = False
        if role == 'voter':
            user.state = state
            user.aadhaar_number = aadhaar_number
            
        from .otp import generate_totp_secret
        user.totp_secret = generate_totp_secret()
        user.save()
        
        request.session['pre_auth_phone'] = phone
        return redirect('verify_otp')
    return render(request, 'authentication/register.html')


def verify_otp_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('voter_dashboard')

    phone = request.session.get('pre_auth_phone')
    if not phone: return redirect('login')

    try:
        user = CustomUser.objects.get(phone_number=phone)
    except CustomUser.DoesNotExist:
        return redirect('login')

    from .otp import get_totp_uri, verify_totp_code
    totp_uri = get_totp_uri(user)

    masked_phone = ""
    if phone:
        phone_str = str(phone).strip()
        if len(phone_str) >= 4:
            masked_phone = f"{phone_str[:2]}{'*' * (len(phone_str) - 4)}{phone_str[-2:]}"
        else:
            masked_phone = phone_str

    setup_required = not user.is_verified

    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        if verify_totp_code(user, otp_entered):
            user.is_verified = True
            user.has_logged_in = True
            user.save()
            login(request, user)
            if 'pre_auth_phone' in request.session:
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
        else:
            return render(request, 'authentication/verify_otp.html', {
                'error': 'Invalid Authenticator code. Please try again.',
                'masked_phone': masked_phone,
                'totp_uri': totp_uri,
                'setup_required': setup_required,
            })
            
    return render(request, 'authentication/verify_otp.html', {
        'masked_phone': masked_phone,
        'totp_uri': totp_uri,
        'setup_required': setup_required,
    })

def logout_view(request):
    logout(request); return redirect('login')

def terms_view(request):
    return render(request, 'authentication/terms.html')

def privacy_view(request):
    return render(request, 'authentication/privacy.html')

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def send_otp_direct_view(request):
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    return JsonResponse({'success': False, 'error': 'SMS OTP is disabled. Users must authenticate using their Google Authenticator App.'}, status=400)