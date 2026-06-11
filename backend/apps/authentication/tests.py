from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import OTPVerification

User = get_user_model()

class AuthenticationModelTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(phone_number="1234567890", password="testpassword123")
        self.assertEqual(user.phone_number, "1234567890")
        self.assertEqual(user.role, "voter")
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_user_no_phone_raises_value_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(phone_number="", password="testpassword123")

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(phone_number="9876543210", password="adminpassword")
        self.assertEqual(admin.phone_number, "9876543210")
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_create_superuser_invalid_staff_or_superuser_raises_value_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(phone_number="9876543210", password="adminpassword", is_staff=False)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(phone_number="9876543210", password="adminpassword", is_superuser=False)


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.verify_otp_url = reverse('verify_otp')
        self.terms_url = reverse('terms')
        self.privacy_url = reverse('privacy')
        
    def test_login_page_renders_successfully(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_login_redirects_authenticated_users(self):
        # Authenticate a voter user
        user = User.objects.create_user(phone_number="8888888888", role="voter", state="tg")
        self.client.force_login(user)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('voter_dashboard_tg'))

    def test_login_post_missing_terms_returns_error(self):
        response = self.client.post(self.login_url, {
            'phone_number': '8888888888',
            'role': 'voter'
            # 'agree_terms' missing
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You must agree to the Terms')

    def test_login_admin_wrong_number_returns_error(self):
        response = self.client.post(self.login_url, {
            'phone_number': '1111111111',
            'role': 'admin',
            'agree_terms': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not admin')

    def test_login_role_mismatch_returns_error(self):
        # Create user as voter first, but using the admin-allowed number 9876543210
        # to bypass the admin number check and reach the database role check.
        User.objects.create_user(phone_number="9876543210", role="voter")
        # Attempt login as admin
        response = self.client.post(self.login_url, {
            'phone_number': '9876543210',
            'role': 'admin',
            'agree_terms': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'registered as VOTER. Please select the correct role.')

    def test_login_ap_voter_invalid_aadhaar_returns_error(self):
        response = self.client.post(self.login_url, {
            'phone_number': '8888888888',
            'role': 'voter',
            'state': 'ap',
            'aadhaar_number': '12345', # too short
            'agree_terms': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aadhaar number must be exactly 12 numeric digits')

    def test_login_ap_voter_valid_aadhaar_success(self):
        response = self.client.post(self.login_url, {
            'phone_number': '8888888888',
            'role': 'voter',
            'state': 'ap',
            'aadhaar_number': '123456789012',
            'agree_terms': 'on'
        })
        self.assertRedirects(response, self.verify_otp_url)

    def test_login_generates_otp_and_redirects(self):
        response = self.client.post(self.login_url, {
            'phone_number': '8888888888',
            'role': 'voter',
            'state': 'tg',
            'agree_terms': 'on'
        })
        self.assertRedirects(response, self.verify_otp_url)
        self.assertEqual(self.client.session['pre_auth_phone'], '8888888888')
        
        user = User.objects.get(phone_number='8888888888')
        otp_exists = OTPVerification.objects.filter(user=user, is_expired=False).exists()
        self.assertTrue(otp_exists)

    def test_verify_otp_page_requires_pre_auth_phone(self):
        response = self.client.get(self.verify_otp_url)
        self.assertRedirects(response, self.login_url)

    def test_verify_otp_success_invalidates_otp_and_logs_in(self):
        user = User.objects.create_user(phone_number="8888888888", role="voter", state="tg")
        otp_record = OTPVerification.objects.create(user=user, otp_code="123456")
        
        # Simulate session state
        session = self.client.session
        session['pre_auth_phone'] = "8888888888"
        session.save()
        
        response = self.client.post(self.verify_otp_url, {
            'otp': '123456'
        })
        
        # Should redirect to Telangana voter dashboard since state is tg
        self.assertRedirects(response, reverse('voter_dashboard_tg'))
        
        # Check that OTP is now expired
        otp_record.refresh_from_db()
        self.assertTrue(otp_record.is_expired)
        
        # Check user is logged in
        self.assertNotIn('pre_auth_phone', self.client.session)

    def test_verify_otp_failure_keeps_otp_active_and_shows_error(self):
        user = User.objects.create_user(phone_number="8888888888")
        otp_record = OTPVerification.objects.create(user=user, otp_code="123456")
        
        session = self.client.session
        session['pre_auth_phone'] = "8888888888"
        session.save()
        
        response = self.client.post(self.verify_otp_url, {
            'otp': '999999' # wrong OTP
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid OTP')
        
        otp_record.refresh_from_db()
        self.assertFalse(otp_record.is_expired)

    def test_legal_pages_render_successfully(self):
        response_terms = self.client.get(self.terms_url)
        self.assertEqual(response_terms.status_code, 200)
        self.assertTemplateUsed(response_terms, 'authentication/terms.html')

        response_privacy = self.client.get(self.privacy_url)
        self.assertEqual(response_privacy.status_code, 200)
        self.assertTemplateUsed(response_privacy, 'authentication/privacy.html')

    def test_login_first_time_stores_face_image(self):
        dummy_face = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        response = self.client.post(self.login_url, {
            'phone_number': '8888888888',
            'role': 'voter',
            'state': 'ap',
            'aadhaar_number': '123456789012',
            'agree_terms': 'on',
            'face_image': dummy_face
        })
        self.assertRedirects(response, self.verify_otp_url)
        
        user = User.objects.get(phone_number='8888888888')
        self.assertEqual(user.face_image, dummy_face)

    def test_login_second_time_with_vote_blocks_access(self):
        from apps.elections.models import Election, Candidate
        from apps.voting.models import Vote
        
        dummy_face = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Create voter who already has a face image
        user = User.objects.create_user(phone_number="8888888888", role="voter", state="ap", aadhaar_number="123456789012", face_image=dummy_face)
        
        # Create election and candidate, and cast a vote for this user
        election = Election.objects.create(title="Active Election", description="Active", is_active=True)
        candidate = Candidate.objects.create(election=election, name="Candidate A", party_affinity="Party A")
        Vote.objects.create(voter=user, election=election, candidate=candidate)
        
        # Now try to log in again with the same credentials and face image
        response = self.client.post(self.login_url, {
            'phone_number': '8888888888',
            'role': 'voter',
            'state': 'ap',
            'aadhaar_number': '123456789012',
            'agree_terms': 'on',
            'face_image': dummy_face
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')
        self.assertContains(response, 'Face Match Detected: You have already cast your vote')

    def test_login_second_time_without_vote_passes(self):
        dummy_face = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Create voter who has a face image but has not voted yet
        user = User.objects.create_user(phone_number="8888888888", role="voter", state="ap", aadhaar_number="123456789012", face_image=dummy_face)
        
        response = self.client.post(self.login_url, {
            'phone_number': '8888888888',
            'role': 'voter',
            'state': 'ap',
            'aadhaar_number': '123456789012',
            'agree_terms': 'on',
            'face_image': dummy_face
        })
        self.assertRedirects(response, self.verify_otp_url)

