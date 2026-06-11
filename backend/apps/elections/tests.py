from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Election, Candidate
from apps.voting.models import Vote

User = get_user_model()

class ElectionDashboardTests(TestCase):
    def setUp(self):
        self.voter_user = User.objects.create_user(phone_number="8888888888", role="voter", state="ap")
        self.voter_user_tg = User.objects.create_user(phone_number="5555555555", role="voter", state="tg")
        self.admin_user = User.objects.create_superuser(phone_number="9876543210")
        
        self.active_election = Election.objects.create(title="Active Election AP", description="Active AP", state="ap", is_active=True)
        self.active_election_tg = Election.objects.create(title="Active Election TG", description="Active TG", state="tg", is_active=True)
        self.inactive_election = Election.objects.create(title="Inactive Election", description="Inactive", state="ap", is_active=False)
        
        self.candidate_active = Candidate.objects.create(election=self.active_election, name="Active Candidate", party_affinity="Active Party", party_symbol="🦁")
        self.candidate_inactive = Candidate.objects.create(election=self.inactive_election, name="Inactive Candidate", party_affinity="Inactive Party")
        
        self.voter_dashboard_url = reverse('voter_dashboard')
        self.voter_dashboard_ap_url = reverse('voter_dashboard_ap')
        self.voter_dashboard_tg_url = reverse('voter_dashboard_tg')
        self.admin_dashboard_url = reverse('admin_dashboard')
        self.toggle_election_url = reverse('toggle_election', args=[self.active_election.id])
        self.add_candidate_url = reverse('add_candidate')

    def test_dashboards_redirect_unauthenticated_users(self):
        # Without logging in, dashboard access should redirect to login
        response = self.client.get(self.voter_dashboard_ap_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.voter_dashboard_ap_url}")
        
        response = self.client.get(self.voter_dashboard_tg_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.voter_dashboard_tg_url}")

        response = self.client.get(self.admin_dashboard_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.admin_dashboard_url}")

    def test_voter_dashboard_routing_and_filtering(self):
        # AP Voter
        self.client.force_login(self.voter_user)
        response = self.client.get(self.voter_dashboard_url)
        self.assertRedirects(response, self.voter_dashboard_ap_url)

        response = self.client.get(self.voter_dashboard_ap_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/voter_dashboard_ap.html')
        self.assertContains(response, "Active Election AP")
        self.assertNotContains(response, "Active Election TG") # TG election hidden
        
        # TG Voter
        self.client.force_login(self.voter_user_tg)
        response = self.client.get(self.voter_dashboard_url)
        self.assertRedirects(response, self.voter_dashboard_tg_url)

        response = self.client.get(self.voter_dashboard_tg_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/voter_dashboard_tg.html')
        self.assertContains(response, "Active Election TG")
        self.assertNotContains(response, "Active Election AP") # AP election hidden

    def test_admin_dashboard_access(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/admin_dashboard.html')
        
        # Should contain AP and TG elections
        self.assertContains(response, "Active Election AP")
        self.assertContains(response, "Active Election TG")

    def test_admin_add_candidate_success(self):
        self.client.force_login(self.admin_user)
        
        self.assertEqual(self.active_election.candidates.count(), 1)
        
        response = self.client.post(self.add_candidate_url, {
            'election_id': self.active_election.id,
            'name': 'New AP Leader',
            'party_affinity': 'New AP Party',
            'party_symbol': '⚖️'
        })
        self.assertRedirects(response, self.admin_dashboard_url)
        
        # Verify candidate created with symbol
        self.assertEqual(self.active_election.candidates.count(), 2)
        new_cand = Candidate.objects.get(name='New AP Leader')
        self.assertEqual(new_cand.party_symbol, '⚖️')

    def test_admin_remove_candidate_success(self):
        self.client.force_login(self.admin_user)
        
        remove_url = reverse('remove_candidate', args=[self.candidate_active.id])
        response = self.client.post(remove_url)
        self.assertRedirects(response, self.admin_dashboard_url)
        
        # Verify candidate is deleted
        with self.assertRaises(Candidate.DoesNotExist):
            self.candidate_active.refresh_from_db()

    def test_non_admin_cannot_manage_candidates(self):
        self.client.force_login(self.voter_user)
        
        # Try add
        response = self.client.post(self.add_candidate_url, {
            'election_id': self.active_election.id,
            'name': 'Hack Candidate',
            'party_affinity': 'Hack Party'
        })
        # Should redirect with error
        self.assertRedirects(response, self.voter_dashboard_ap_url)
        self.assertEqual(Candidate.objects.filter(name='Hack Candidate').count(), 0)

        # Try remove
        remove_url = reverse('remove_candidate', args=[self.candidate_active.id])
        response = self.client.post(remove_url)
        self.assertRedirects(response, self.voter_dashboard_ap_url)
        # Should NOT be deleted
        self.candidate_active.refresh_from_db() # Should not raise error

    def test_toggle_election_status_by_admin(self):
        self.client.force_login(self.admin_user)
        self.assertTrue(self.active_election.is_active)
        
        response = self.client.post(self.toggle_election_url)
        self.assertRedirects(response, self.admin_dashboard_url)
        
        self.active_election.refresh_from_db()
        self.assertFalse(self.active_election.is_active)
