from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.elections.models import Election, Candidate
from .models import Vote

@login_required
def cast_vote(request, election_id):
    if request.method == "POST" and request.user.role == 'voter':
        candidate_id = request.POST.get('candidate')
        election = get_object_or_404(Election, id=election_id, is_active=True)
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)
        if not Vote.objects.filter(voter=request.user, election=election).exists():
            Vote.objects.create(voter=request.user, election=election, candidate=candidate)
            candidate.votes_count += 1; candidate.save()
    return redirect('voter_dashboard')