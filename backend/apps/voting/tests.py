from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.elections.models import Election, Candidate
from .models import Vote

User = get_user_model()

class VotingMechanismTests(TestCase):
    def setUp(self):
        self.voter_user = User.objects.create_user(phone_number="8888888888", role="voter", state="ap")
        self.voter_user2 = User.objects.create_user(phone_number="5555555555", role="voter", state="ap")
        self.admin_user = User.objects.create_superuser(phone_number="9876543210")
        
        self.active_election = Election.objects.create(title="Active Election", description="Active", is_active=True)
        self.inactive_election = Election.objects.create(title="Inactive Election", description="Inactive", is_active=False)
        
        self.candidate_a = Candidate.objects.create(election=self.active_election, name="Candidate A", party_affinity="Party A")
        self.candidate_b = Candidate.objects.create(election=self.active_election, name="Candidate B", party_affinity="Party B")
        self.candidate_inactive = Candidate.objects.create(election=self.inactive_election, name="Candidate Inactive", party_affinity="Party Inactive")
        
        self.cast_vote_active_url = reverse('cast_vote', args=[self.active_election.id])
        self.cast_vote_inactive_url = reverse('cast_vote', args=[self.inactive_election.id])

    def test_cast_vote_success_increments_count(self):
        self.client.force_login(self.voter_user)
        
        # Verify initial vote count is 0
        self.assertEqual(self.candidate_a.votes_count, 0)
        self.assertEqual(Vote.objects.filter(election=self.active_election).count(), 0)
        
        response = self.client.post(self.cast_vote_active_url, {
            'candidate': self.candidate_a.id
        })
        self.assertRedirects(response, reverse('voter_dashboard_ap'))
        
        # Verify candidate vote incremented and Vote record created
        self.candidate_a.refresh_from_db()
        self.assertEqual(self.candidate_a.votes_count, 1)
        self.assertTrue(Vote.objects.filter(voter=self.voter_user, election=self.active_election, candidate=self.candidate_a).exists())

    def test_prevent_double_voting(self):
        self.client.force_login(self.voter_user)
        
        # First vote
        self.client.post(self.cast_vote_active_url, {
            'candidate': self.candidate_a.id
        })
        self.candidate_a.refresh_from_db()
        self.assertEqual(self.candidate_a.votes_count, 1)
        
        # Second vote in same election for different candidate
        response = self.client.post(self.cast_vote_active_url, {
            'candidate': self.candidate_b.id
        })
        self.assertRedirects(response, reverse('voter_dashboard_ap'))
        
        # Verify no vote count change for candidate B and vote count for candidate A is still 1
        self.candidate_b.refresh_from_db()
        self.assertEqual(self.candidate_b.votes_count, 0)
        
        self.candidate_a.refresh_from_db()
        self.assertEqual(self.candidate_a.votes_count, 1)
        
        # Total votes in db is still 1
        self.assertEqual(Vote.objects.filter(election=self.active_election).count(), 1)

    def test_admin_cannot_vote(self):
        self.client.force_login(self.admin_user)
        
        response = self.client.post(self.cast_vote_active_url, {
            'candidate': self.candidate_a.id
        })
        # Admin gets redirected to admin dashboard with error
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertEqual(Vote.objects.count(), 0)
        
        self.candidate_a.refresh_from_db()
        self.assertEqual(self.candidate_a.votes_count, 0)

    def test_cannot_vote_in_inactive_election(self):
        self.client.force_login(self.voter_user)
        
        response = self.client.post(self.cast_vote_inactive_url, {
            'candidate': self.candidate_inactive.id
        })
        # Should return 404 since it's inactive
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Vote.objects.count(), 0)
