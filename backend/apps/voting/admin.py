from django.contrib import admin
from .models import Vote

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        self.request = request
        if request.user.is_superuser:
            return ('id', 'display_voter', 'election', 'display_candidate')
        return ('id', 'election', 'display_candidate_masked')

    def display_voter(self, obj):
        if hasattr(self, 'request') and self.request.user.is_superuser:
            voter_name = obj.voter.get_full_name()
            suffix = f" ({voter_name})" if voter_name else ""
            return f"{obj.voter.phone_number}{suffix}"
        return "[Protected]"
    display_voter.short_description = 'Voter'

    def display_candidate(self, obj):
        return obj.candidate.name
    display_candidate.short_description = 'Candidate'

    def display_candidate_masked(self, obj):
        return "[Protected]"
    display_candidate_masked.short_description = 'Candidate'

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('voter', 'election', 'candidate')
        return ()

    def get_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('election',)
        return ('voter', 'election', 'candidate')
