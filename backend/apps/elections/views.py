from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Election, Candidate
from apps.voting.models import Vote

def seed_default_data():
    from .models import Election, Candidate
    
    # 1. AP CM Election
    ap_election, created = Election.objects.get_or_create(
        state='ap',
        defaults={
            'title': 'Andhra Pradesh CM Election 2026',
            'description': 'Election for the Chief Minister of Andhra Pradesh.',
            'is_active': True
        }
    )
    if not ap_election.candidates.filter(name="Chandra Babu Naidu").exists():
        ap_election.candidates.all().delete()
        Candidate.objects.create(election=ap_election, name="Chandra Babu Naidu", party_affinity="TDP", party_symbol="🚲")
        Candidate.objects.create(election=ap_election, name="Jagan", party_affinity="YSRCP", party_symbol="🪭")
        Candidate.objects.create(election=ap_election, name="Pawan Kalyan (Janasena)", party_affinity="Janasena Party", party_symbol="🥃")

    # 2. TG CM Election
    tg_election, created = Election.objects.get_or_create(
        state='tg',
        defaults={
            'title': 'Telangana CM Election 2026',
            'description': 'Election for the Chief Minister of Telangana.',
            'is_active': True
        }
    )
    if not tg_election.candidates.filter(name="Revanth Reddy").exists():
        tg_election.candidates.all().delete()
        Candidate.objects.create(election=tg_election, name="Revanth Reddy", party_affinity="INC", party_symbol="✋")
        Candidate.objects.create(election=tg_election, name="KCR", party_affinity="BRS", party_symbol="🚗")

    # 3. Chennai CM Election
    chennai_election, created = Election.objects.get_or_create(
        state='chennai',
        defaults={
            'title': 'Chennai CM Election 2026',
            'description': 'Election for the Chief Minister of Tamil Nadu (Chennai).',
            'is_active': True
        }
    )
    if not chennai_election.candidates.filter(name="Vijay").exists():
        chennai_election.candidates.all().delete()
        Candidate.objects.create(election=chennai_election, name="Vijay", party_affinity="TVK", party_symbol="🦁")
        Candidate.objects.create(election=chennai_election, name="Stalin", party_affinity="DMK", party_symbol="☀️")

@login_required
def voter_dashboard(request):
    if request.user.role != 'voter':
        return redirect('admin_dashboard')
    seed_default_data()
    if request.user.state == 'ap':
        return redirect('voter_dashboard_ap')
    elif request.user.state == 'tg':
        return redirect('voter_dashboard_tg')
    else:
        return redirect('voter_dashboard_chennai')

@login_required
def voter_dashboard_ap(request):
    if request.user.role != 'voter':
        return redirect('admin_dashboard')
    seed_default_data()
    if request.user.state != 'ap':
        return redirect('voter_dashboard')
        
    elections = Election.objects.filter(is_active=True, state='ap')
    voted = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)
    return render(request, 'elections/voter_dashboard_ap.html', {
        'elections': elections,
        'voted_elections': voted,
        'voted_count': len(voted),
    })

@login_required
def voter_dashboard_tg(request):
    if request.user.role != 'voter':
        return redirect('admin_dashboard')
    seed_default_data()
    if request.user.state != 'tg':
        return redirect('voter_dashboard')
        
    elections = Election.objects.filter(is_active=True, state='tg')
    voted = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)
    return render(request, 'elections/voter_dashboard_tg.html', {
        'elections': elections,
        'voted_elections': voted,
        'voted_count': len(voted),
    })

@login_required
def voter_dashboard_chennai(request):
    if request.user.role != 'voter':
        return redirect('admin_dashboard')
    seed_default_data()
    if request.user.state != 'chennai':
        return redirect('voter_dashboard')
        
    elections = Election.objects.filter(is_active=True, state='chennai')
    voted = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)
    return render(request, 'elections/voter_dashboard_chennai.html', {
        'elections': elections,
        'voted_elections': voted,
        'voted_count': len(voted),
    })

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('voter_dashboard')
    seed_default_data()
    elections = Election.objects.all()
    election_data = []
    
    for election in elections:
        candidates = election.candidates.all()
        total_votes = Vote.objects.filter(election=election).count()
        
        cand_list = []
        majority_cand = None
        max_votes = -1
        is_tie = False
        
        for cand in candidates:
            v_count = Vote.objects.filter(candidate=cand).count()
            
            # Sync candidate vote count cached in DB if out of sync
            if cand.votes_count != v_count:
                cand.votes_count = v_count
                cand.save()
                
            percent = (v_count / total_votes * 100) if total_votes > 0 else 0
            
            cand_list.append({
                'id': cand.id,
                'name': cand.name,
                'party': cand.party_affinity,
                'symbol': cand.party_symbol,
                'votes': v_count,
                'percent': round(percent, 1),
            })
            
            if v_count > max_votes:
                max_votes = v_count
                majority_cand = cand
                is_tie = False
            elif v_count == max_votes and max_votes >= 0:
                is_tie = True
                
        if total_votes == 0:
            majority_status = "No votes cast yet"
            majority_percent = 0
            win_chances = "0%"
        elif is_tie:
            majority_status = "Tie between leading candidates"
            majority_percent = round((max_votes / total_votes * 100), 1)
            win_chances = "Inconclusive (Tie)"
        else:
            majority_status = f"{majority_cand.name} ({majority_cand.party_affinity})"
            majority_percent = round((max_votes / total_votes * 100), 1)
            
            # Win chances projection:
            if majority_percent >= 50:
                win_chances = f"Strong Win Probability ({majority_percent}%)"
            else:
                win_chances = f"Leading Candidate ({majority_percent}%)"
                
        election_data.append({
            'election': election,
            'candidates': cand_list,
            'total_votes': total_votes,
            'majority_status': majority_status,
            'majority_percent': majority_percent,
            'win_chances': win_chances,
        })
        
    audit_votes = Vote.objects.select_related('voter', 'election', 'candidate').order_by('-id')
    
    return render(request, 'elections/admin_dashboard.html', {
        'elections_data': election_data,
        'audit_votes': audit_votes,
        'elections': elections,
    })

@login_required
def toggle_election(request, election_id):
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to change election states.")
        return redirect('voter_dashboard')
        
    if request.method == "POST":
        election = get_object_or_404(Election, id=election_id)
        election.is_active = not election.is_active
        election.save()
        status_str = "opened" if election.is_active else "closed"
        messages.success(request, f"Election '{election.title}' has been successfully {status_str}!")
        
    return redirect('admin_dashboard')

@login_required
def add_candidate(request):
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to manage candidates.")
        return redirect('voter_dashboard_ap' if request.user.state == 'ap' else 'voter_dashboard_tg')
        
    if request.method == "POST":
        election_id = request.POST.get('election_id')
        name = request.POST.get('name')
        party_affinity = request.POST.get('party_affinity')
        party_symbol = request.POST.get('party_symbol', '🗳️')
        
        if not election_id or not name or not party_affinity:
            messages.error(request, "Please fill in all candidate details.")
            return redirect('admin_dashboard')
            
        election = get_object_or_404(Election, id=election_id)
        Candidate.objects.create(
            election=election,
            name=name,
            party_affinity=party_affinity,
            party_symbol=party_symbol
        )
        messages.success(request, f"Candidate '{name}' (with symbol {party_symbol}) has been successfully added to '{election.title}'!")
        
    return redirect('admin_dashboard')

@login_required
def remove_candidate(request, candidate_id):
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to manage candidates.")
        return redirect('voter_dashboard_ap' if request.user.state == 'ap' else 'voter_dashboard_tg')
        
    if request.method == "POST":
        candidate = get_object_or_404(Candidate, id=candidate_id)
        name = candidate.name
        election_title = candidate.election.title
        candidate.delete()
        messages.success(request, f"Candidate '{name}' has been successfully removed from '{election_title}'!")
        
    return redirect('admin_dashboard')

@login_required
def reset_voter_face(request, voter_id):
    """Admin-only: Reset a voter's stored face image to allow them to re-register."""
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to reset voter biometrics.")
        return redirect('voter_dashboard')
    
    if request.method == "POST":
        from apps.authentication.models import CustomUser
        try:
            voter = CustomUser.objects.get(id=voter_id, role='voter')
            voter.face_image = None
            voter.save()
            messages.success(request, f"✅ Face biometric reset for voter {voter.phone_number}. They may now login again.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Voter not found.")
    
    return redirect('admin_dashboard')