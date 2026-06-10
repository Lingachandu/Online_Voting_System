from django.db import models

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=100)
    party_affinity = models.CharField(max_length=100, blank=True)
    votes_count = models.IntegerField(default=0)