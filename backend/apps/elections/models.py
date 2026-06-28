from django.db import models

class Election(models.Model):
    STATE_CHOICES = (
        ('ap', 'Andhra Pradesh'),
        ('tg', 'Telangana'),
        ('chennai', 'Chennai')
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='ap')
    is_active = models.BooleanField(default=True)

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=100)
    party_affinity = models.CharField(max_length=100, blank=True)
    party_symbol = models.CharField(max_length=50, blank=True, default="🗳️")
    party_color = models.CharField(max_length=7, blank=True, default="#4f46e5")
    votes_count = models.IntegerField(default=0)
    photo_url = models.TextField(blank=True, null=True)