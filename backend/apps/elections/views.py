from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Election
from apps.voting.models import Vote

@login_required
def voter_dashboard(request):
    elections = Election.objects.filter(is_active=True)
    voted = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)
    return render(request, 'elections/voter_dashboard.html', {'elections': elections, 'voted_elections': voted})

@login_required
def admin_dashboard(request):
    return render(request, 'elections/admin_dashboard.html', {'elections': Election.objects.all()})