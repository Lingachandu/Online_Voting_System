from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Election, Candidate
from apps.voting.models import Vote
from apps.authentication.models import CustomUser

def seed_default_data():
    import datetime
    from .models import Election, Candidate
    
    current_year = datetime.datetime.now().year
    
    # 1. AP CM Election
    ap_election, created = Election.objects.get_or_create(
        state='ap',
        title=f'Andhra Pradesh CM Election {current_year}',
        defaults={
            'description': 'Election for the Chief Minister of Andhra Pradesh.',
            'is_active': True
        }
    )
    if not created:
        ap_election.description = 'Election for the Chief Minister of Andhra Pradesh.'
        ap_election.save()
        
    # Map AP Candidates
    c_naidu, _ = Candidate.objects.get_or_create(election=ap_election, name="Chandra Babu Naidu")
    c_naidu.party_affinity = "TDP"
    c_naidu.party_symbol = "🚲"
    c_naidu.party_color = "#eab308"
    c_naidu.photo_url = "/static/candidates/images/chandra_babu_naidu.jpg"
    c_naidu.save()
    
    c_jagan, _ = Candidate.objects.get_or_create(election=ap_election, name="Jagan")
    c_jagan.party_affinity = "YSRCP"
    c_jagan.party_symbol = "🪭"
    c_jagan.party_color = "#0284c7"
    c_jagan.photo_url = "/static/candidates/images/jagan.jpg"
    c_jagan.save()
    
    c_pawan, _ = Candidate.objects.get_or_create(election=ap_election, name="Pawan Kalyan (Janasena)")
    c_pawan.party_affinity = "Janasena Party"
    c_pawan.party_symbol = "🥃"
    c_pawan.party_color = "#dc2626"
    c_pawan.photo_url = "/static/candidates/images/pawan_kalyan.jpg"
    c_pawan.save()

    # 2. TG CM Election
    tg_election, created = Election.objects.get_or_create(
        state='tg',
        title=f'Telangana CM Election {current_year}',
        defaults={
            'description': 'Election for the Chief Minister of Telangana.',
            'is_active': True
        }
    )
    if not created:
        tg_election.description = 'Election for the Chief Minister of Telangana.'
        tg_election.save()
        
    # Map TG Candidates
    c_revanth, _ = Candidate.objects.get_or_create(election=tg_election, name="Revanth Reddy")
    c_revanth.party_affinity = "INC"
    c_revanth.party_symbol = "✋"
    c_revanth.party_color = "#059669"
    c_revanth.photo_url = "/static/candidates/images/revanth_reddy.png"
    c_revanth.save()
    
    c_kcr, _ = Candidate.objects.get_or_create(election=tg_election, name="KCR")
    c_kcr.party_affinity = "BRS"
    c_kcr.party_symbol = "🚗"
    c_kcr.party_color = "#db2777"
    c_kcr.photo_url = "/static/candidates/images/kcr.jpg"
    c_kcr.save()

    # 3. Chennai CM Election
    chennai_election, created = Election.objects.get_or_create(
        state='chennai',
        title=f'Chennai CM Election {current_year}',
        defaults={
            'description': 'Election for the Chief Minister of Tamil Nadu (Chennai).',
            'is_active': True
        }
    )
    if not created:
        chennai_election.description = 'Election for the Chief Minister of Tamil Nadu (Chennai).'
        chennai_election.save()
        
    # Map Chennai Candidates
    c_vijay, _ = Candidate.objects.get_or_create(election=chennai_election, name="Vijay")
    c_vijay.party_affinity = "TVK"
    c_vijay.party_symbol = "🦁"
    c_vijay.party_color = "#ca8a04"
    c_vijay.photo_url = "/static/candidates/images/vijay.jpg"
    c_vijay.save()
    
    c_stalin, _ = Candidate.objects.get_or_create(election=chennai_election, name="Stalin")
    c_stalin.party_affinity = "DMK"
    c_stalin.party_symbol = "☀️"
    c_stalin.party_color = "#ea580c"
    c_stalin.photo_url = "/static/candidates/images/stalin.jpg"
    c_stalin.save()



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
    elections_json_list = []

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
                'color': cand.party_color,
                'votes': v_count,
                'percent': round(percent, 1),
                'photo_url': cand.photo_url or '',
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
            win_status = "no_votes"
            winner_name = None
            winner_percent = 0
            winner_photo = ""
        elif is_tie:
            majority_status = "Tie between leading candidates"
            majority_percent = round((max_votes / total_votes * 100), 1)
            win_chances = "Inconclusive (Tie)"
            win_status = "tie"
            winner_name = None
            winner_percent = majority_percent
            winner_photo = ""
        else:
            majority_status = f"{majority_cand.name} ({majority_cand.party_affinity})"
            majority_percent = round((max_votes / total_votes * 100), 1)
            winner_name = majority_status
            winner_percent = majority_percent
            winner_photo = majority_cand.photo_url or ""

            # Win chances projection:
            if majority_percent >= 50:
                win_chances = f"Strong Win Probability ({majority_percent}%)"
                win_status = "strong_win"
            else:
                win_chances = f"Leading Candidate ({majority_percent}%)"
                win_status = "leading"

        election_data.append({
            'election': election,
            'candidates': cand_list,
            'total_votes': total_votes,
            'majority_status': majority_status,
            'majority_percent': majority_percent,
            'win_chances': win_chances,
            'win_status': win_status,
            'winner_name': winner_name or '',
            'winner_percent': winner_percent,
            'winner_photo': winner_photo,
        })

        elections_json_list.append({
            'election_id': election.id,
            'title': election.title,
            'state': election.state,
            'is_active': election.is_active,
            'total_votes': total_votes,
            'candidates': cand_list,
            'win_status': win_status,
            'winner_name': winner_name or '',
            'winner_percent': winner_percent,
            'winning_label': win_chances,
            'winner_photo': winner_photo,
        })

    # State-wise statistics
    def get_state_stats(state_code):
        state_voters = CustomUser.objects.filter(role='voter', state=state_code).count()
        state_election = Election.objects.filter(state=state_code).first()
        state_votes = Vote.objects.filter(election=state_election).count() if state_election else 0
        state_turnout = round((state_votes / state_voters * 100), 1) if state_voters > 0 else 0
        return state_voters, state_votes, state_turnout

    ap_voters, ap_votes, ap_turnout = get_state_stats('ap')
    tg_voters, tg_votes, tg_turnout = get_state_stats('tg')
    chennai_voters, chennai_votes, chennai_turnout = get_state_stats('chennai')

    total_voters = CustomUser.objects.filter(role='voter').count()
    total_votes_system = Vote.objects.count()
    turnout_percent = round((total_votes_system / total_voters * 100), 1) if total_voters > 0 else 0

    audit_votes = Vote.objects.select_related('voter', 'election', 'candidate').order_by('-id')

    import json
    return render(request, 'elections/admin_dashboard.html', {
        'elections_data': election_data,
        'audit_votes': audit_votes,
        'elections': elections,
        'elections_json': json.dumps(elections_json_list),
        'ap_voters': ap_voters,
        'ap_votes': ap_votes,
        'ap_turnout': ap_turnout,
        'tg_voters': tg_voters,
        'tg_votes': tg_votes,
        'tg_turnout': tg_turnout,
        'chennai_voters': chennai_voters,
        'chennai_votes': chennai_votes,
        'chennai_turnout': chennai_turnout,
        'total_voters': total_voters,
        'total_votes_system': total_votes_system,
        'turnout_percent': turnout_percent,
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
        party_color = request.POST.get('party_color', '#4f46e5')
        
        photo_file = request.FILES.get('photo')
        photo_url = None
        if photo_file:
            import base64
            file_data = photo_file.read()
            encoded = base64.b64encode(file_data).decode('utf-8')
            mime_type = photo_file.content_type
            photo_url = f"data:{mime_type};base64,{encoded}"
            
        if not election_id or not name or not party_affinity:
            messages.error(request, "Please fill in all candidate details.")
            return redirect('admin_dashboard')
            
        election = get_object_or_404(Election, id=election_id)
        Candidate.objects.create(
            election=election,
            name=name,
            party_affinity=party_affinity,
            party_symbol=party_symbol,
            party_color=party_color,
            photo_url=photo_url
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


@login_required
def live_stats_api(request):
    """
    JSON API endpoint for live election statistics.
    Called by the admin dashboard JS every 30s for real-time updates.
    Returns: state-wise vote counts, percentages, winner, total votes.
    """
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    elections = Election.objects.all()
    result = []

    # Overall system stats
    total_voters = CustomUser.objects.filter(role='voter').count()
    total_votes_cast = Vote.objects.count()
    turnout_percent = round((total_votes_cast / total_voters * 100), 1) if total_voters > 0 else 0

    # State-wise totals
    state_data = {}
    for state_code, state_name in [('ap', 'Andhra Pradesh'), ('tg', 'Telangana'), ('chennai', 'Chennai')]:
        state_voters = CustomUser.objects.filter(role='voter', state=state_code).count()
        state_election = Election.objects.filter(state=state_code).first()
        state_votes = Vote.objects.filter(election=state_election).count() if state_election else 0
        state_turnout = round((state_votes / state_voters * 100), 1) if state_voters > 0 else 0
        state_data[state_code] = {
            'name': state_name,
            'total_voters': state_voters,
            'votes_cast': state_votes,
            'turnout_percent': state_turnout,
        }

    for election in elections:
        candidates = election.candidates.all()
        total_votes = Vote.objects.filter(election=election).count()
        cand_list = []
        winner_name = None
        winner_percent = 0
        is_tie = False
        max_votes = -1

        winner_photo = ''
        for cand in candidates:
            v_count = Vote.objects.filter(candidate=cand).count()
            percent = round((v_count / total_votes * 100), 1) if total_votes > 0 else 0
            cand_list.append({
                'id': cand.id,
                'name': cand.name,
                'party': cand.party_affinity,
                'symbol': cand.party_symbol,
                'color': cand.party_color,
                'votes': v_count,
                'percent': percent,
                'photo_url': cand.photo_url or '',
            })
            if v_count > max_votes:
                max_votes = v_count
                winner_name = f"{cand.name} ({cand.party_affinity})"
                winner_percent = percent
                winner_photo = cand.photo_url or ''
                is_tie = False
            elif v_count == max_votes and max_votes >= 0:
                is_tie = True

        if total_votes == 0 or is_tie:
            winner_photo = ''
            win_status = 'no_votes' if total_votes == 0 else 'tie'
            winning_label = 'No votes cast yet' if total_votes == 0 else 'Tie'
        elif winner_percent >= 50:
            win_status = 'strong_win'
            winning_label = f"Strong Win: {winner_name} ({winner_percent}%)"
        else:
            win_status = 'leading'
            winning_label = f"Leading: {winner_name} ({winner_percent}%)"

        result.append({
            'election_id': election.id,
            'title': election.title,
            'state': election.state,
            'is_active': election.is_active,
            'total_votes': total_votes,
            'candidates': cand_list,
            'win_status': win_status,
            'winning_label': winning_label,
            'winner_name': winner_name,
            'winner_percent': winner_percent,
            'winner_photo': winner_photo,
        })

    return JsonResponse({
        'elections': result,
        'state_data': state_data,
        'total_votes_system': total_votes_cast,
        'total_voters': total_voters,
        'turnout_percent': turnout_percent,
        'timestamp': __import__('datetime').datetime.now().strftime('%H:%M:%S'),
    })