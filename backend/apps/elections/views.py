from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import JsonResponse
from .models import Election, Candidate
from apps.voting.models import Vote
from apps.authentication.models import CustomUser

def seed_default_data():
    from .models import Election, Candidate
    if Election.objects.exists():
        return
    import datetime
    current_year = datetime.datetime.now().year
    
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
    
    total_voters = CustomUser.objects.filter(role='voter', state='ap').count()
    total_voted = Vote.objects.filter(voter__state='ap').values('voter').distinct().count()
    turnout_pct = round((total_voted / total_voters * 100), 1) if total_voters > 0 else 0.0

    return render(request, 'elections/voter_dashboard.html', {
        'elections': elections,
        'voted_elections': voted,
        'voted_count': len(voted),
        'state_code': 'ap',
        'state_name': 'Andhra Pradesh',
        'aadhaar_prefix': '123',
        'helpline_phone': '1800-425-1234',
        'helpline_email': 'apelection@ap.gov.in',
        'turnout_pct': turnout_pct,
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
    
    total_voters = CustomUser.objects.filter(role='voter', state='tg').count()
    total_voted = Vote.objects.filter(voter__state='tg').values('voter').distinct().count()
    turnout_pct = round((total_voted / total_voters * 100), 1) if total_voters > 0 else 0.0

    return render(request, 'elections/voter_dashboard.html', {
        'elections': elections,
        'voted_elections': voted,
        'voted_count': len(voted),
        'state_code': 'tg',
        'state_name': 'Telangana',
        'aadhaar_prefix': '456',
        'helpline_phone': '1800-425-5678',
        'helpline_email': 'tgelection@telangana.gov.in',
        'turnout_pct': turnout_pct,
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
    
    total_voters = CustomUser.objects.filter(role='voter', state='chennai').count()
    total_voted = Vote.objects.filter(voter__state='chennai').values('voter').distinct().count()
    turnout_pct = round((total_voted / total_voters * 100), 1) if total_voters > 0 else 0.0

    return render(request, 'elections/voter_dashboard.html', {
        'elections': elections,
        'voted_elections': voted,
        'voted_count': len(voted),
        'state_code': 'chennai',
        'state_name': 'Chennai',
        'aadhaar_prefix': '789',
        'helpline_phone': '1800-425-7890',
        'helpline_email': 'chennaielection@tn.gov.in',
        'turnout_pct': turnout_pct,
    })

@login_required
@never_cache
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
def create_election(request):
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to perform this action.")
        return redirect('voter_dashboard')
        
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        state = request.POST.get('state')
        
        if not title or not state:
            messages.error(request, "Please fill in all election details.")
            return redirect('admin_dashboard')
            
        Election.objects.create(
            title=title,
            description=description,
            state=state,
            is_active=True
        )
        messages.success(request, f"Election '{title}' has been successfully created!")
        
    return redirect('admin_dashboard')

@login_required
def edit_election(request, election_id):
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to perform this action.")
        return redirect('voter_dashboard')
        
    election = get_object_or_404(Election, id=election_id)
    
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        state = request.POST.get('state')
        is_active_val = request.POST.get('is_active')
        
        if not title or not state:
            messages.error(request, "Please fill in all election details.")
            return redirect('admin_dashboard')
            
        election.title = title
        election.description = description
        election.state = state
        election.is_active = (is_active_val == 'True' or is_active_val == 'on' or is_active_val == '1')
        election.save()
        
        messages.success(request, f"Election '{title}' has been successfully updated!")
        
    return redirect('admin_dashboard')

@login_required
def delete_election(request, election_id):
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to perform this action.")
        return redirect('voter_dashboard')
        
    if request.method == "POST":
        election = get_object_or_404(Election, id=election_id)
        title = election.title
        election.delete()
        messages.success(request, f"Election '{title}' has been successfully deleted!")
        
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
@never_cache
def live_stats_api(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    elections = Election.objects.all()
    result = []

    total_voters = CustomUser.objects.filter(role='voter').count()
    total_votes_cast = Vote.objects.count()
    turnout_percent = round((total_votes_cast / total_voters * 100), 1) if total_voters > 0 else 0

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

    audit_list = []
    audit_votes = Vote.objects.select_related('voter', 'election', 'candidate').order_by('-id')[:50]
    
    is_superuser = request.user.is_superuser
    
    for vote in audit_votes:
        phone = vote.voter.phone_number
        aadhaar = vote.voter.aadhaar_number
        
        if is_superuser:
            phone_val = phone if phone else ""
            aadhaar_val = aadhaar if aadhaar else "-"
            voter_id_val = vote.voter.id
            vote_id_val = vote.id
            receipt_code = f"SEC-VOTE-{vote.id}-{vote.voter.id}"
            candidate_name = vote.candidate.name
            party_symbol = vote.candidate.party_symbol
            party_affinity = vote.candidate.party_affinity
            candidate_photo_url = vote.candidate.photo_url or ''
        else:
            phone_val = "[Protected]"
            aadhaar_val = "[Protected]"
            voter_id_val = "[Hidden]"
            vote_id_val = "[Hidden]"
            receipt_code = "SEC-VOTE-[Hidden]"
            candidate_name = "[Protected/Anonymous]"
            party_symbol = "🔒"
            party_affinity = "[Protected]"
            candidate_photo_url = ''

        audit_list.append({
            'vote_id': vote_id_val,
            'voter_id': voter_id_val,
            'receipt_code': receipt_code,
            'phone_number': phone_val,
            'aadhaar_number': aadhaar_val,
            'state': vote.voter.state or '',
            'election_title': vote.election.title,
            'candidate_name': candidate_name,
            'party_symbol': party_symbol,
            'party_affinity': party_affinity,
            'candidate_photo_url': candidate_photo_url,
        })

    return JsonResponse({
        'elections': result,
        'state_data': state_data,
        'total_votes_system': total_votes_cast,
        'total_voters': total_voters,
        'turnout_percent': turnout_percent,
        'audit_votes': audit_list,
        'is_superuser': is_superuser,
        'timestamp': __import__('datetime').datetime.now().strftime('%H:%M:%S'),
    })

@login_required
def verify_receipt_api(request):
    code = request.GET.get('code', '').strip()
    if not code.startswith('SEC-VOTE-'):
        return JsonResponse({'success': False, 'error': 'Invalid receipt code format.'})
    
    parts = code.split('-')
    if len(parts) < 4:
        return JsonResponse({'success': False, 'error': 'Invalid receipt code format.'})
    
    try:
        vote_id = int(parts[2])
        voter_id = int(parts[3])
        from apps.voting.models import Vote
        vote = Vote.objects.select_related('voter', 'election', 'candidate').get(id=vote_id, voter_id=voter_id)
        
        # Base details visible to everyone
        data = {
            'success': True,
            'vote_id': vote.id,
            'voter_id': vote.voter.id,
            'state': vote.voter.state,
            'election_title': vote.election.title,
        }
        
        # Access control based on user status
        if request.user.is_superuser:
            data.update({
                'phone_number': vote.voter.phone_number,
                'candidate_name': vote.candidate.name,
                'party_affinity': vote.candidate.party_affinity,
                'party_symbol': vote.candidate.party_symbol,
                'is_admin': True,
                'is_superuser': True,
            })
        elif vote.voter == request.user:
            data.update({
                'phone_number': vote.voter.phone_number,
                'candidate_name': vote.candidate.name,
                'party_affinity': vote.candidate.party_affinity,
                'party_symbol': vote.candidate.party_symbol,
                'is_admin': False,
                'is_superuser': False,
            })
        else:
            data.update({
                'phone_number': "[Protected]",
                'candidate_name': "[Protected/Anonymous]",
                'party_affinity': "[Protected]",
                'party_symbol': "🔒",
                'is_admin': False,
                'is_superuser': False,
            })
            
        return JsonResponse(data)
    except (ValueError, Vote.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Receipt code not found in voting registry.'})


@login_required
def remove_vote(request, vote_id):
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Only administrators are authorized to perform this action.'}, status=403)
        
    if request.method == "POST":
        from apps.voting.models import Vote
        vote = get_object_or_404(Vote, id=vote_id)
        candidate = vote.candidate
        if candidate.votes_count > 0:
            candidate.votes_count -= 1
            candidate.save()
        vote.delete()
        return JsonResponse({'success': True, 'message': 'Vote has been successfully removed.'})
        
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


@login_required
def remove_voter(request, voter_id):
    if request.user.role != 'admin':
        messages.error(request, "Only administrators are authorized to perform this action.")
        return redirect('voter_dashboard')
        
    if request.method == "POST":
        voter = get_object_or_404(CustomUser, id=voter_id, role='voter')
        from apps.voting.models import Vote
        votes = Vote.objects.filter(voter=voter)
        for vote in votes:
            candidate = vote.candidate
            if candidate.votes_count > 0:
                candidate.votes_count -= 1
                candidate.save()
        voter_phone = voter.phone_number
        voter.delete()
        messages.success(request, f"Voter account {voter_phone} and their votes have been successfully removed.")
        
    return redirect('admin_dashboard')