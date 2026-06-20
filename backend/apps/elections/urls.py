from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/voter/', views.voter_dashboard, name='voter_dashboard'),
    path('dashboard/voter/ap/', views.voter_dashboard_ap, name='voter_dashboard_ap'),
    path('dashboard/voter/tg/', views.voter_dashboard_tg, name='voter_dashboard_tg'),
    path('dashboard/voter/chennai/', views.voter_dashboard_chennai, name='voter_dashboard_chennai'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('election/toggle/<int:election_id>/', views.toggle_election, name='toggle_election'),
    path('candidate/add/', views.add_candidate, name='add_candidate'),
    path('candidate/remove/<int:candidate_id>/', views.remove_candidate, name='remove_candidate'),
    path('voter/reset-face/<int:voter_id>/', views.reset_voter_face, name='reset_voter_face'),
    path('api/live-stats/', views.live_stats_api, name='live_stats_api'),
]