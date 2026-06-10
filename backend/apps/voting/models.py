from django.db import models
from apps.authentication.models import CustomUser
from apps.elections.models import Election, Candidate

class Vote(models.Model):
    voter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('voter', 'election')