from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.elections.models import Election, Candidate
from .models import Vote

@login_required
def cast_vote(request, election_id):
    if request.user.role != 'voter':
        messages.error(request, "Only voters are authorized to cast votes.")
        return redirect('admin_dashboard')

    if request.method == "POST":
        candidate_id = request.POST.get('candidate')
        election = get_object_or_404(Election, id=election_id, is_active=True)
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)
        if not Vote.objects.filter(voter=request.user, election=election).exists():
            Vote.objects.create(voter=request.user, election=election, candidate=candidate)
            candidate.votes_count += 1
            candidate.save()
            messages.success(request, f"Your vote for {candidate.name} has been cast successfully! ✓")
        else:
            messages.warning(request, "You have already voted in this election.")
    return redirect('voter_dashboard_ap' if request.user.state == 'ap' else 'voter_dashboard_tg')