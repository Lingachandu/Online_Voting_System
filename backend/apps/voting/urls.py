from django.urls import path
from . import views
urlpatterns = [
    path('cast-vote/<int:election_id>/', views.cast_vote, name='cast_vote'),
    path('download-receipt/<int:election_id>/', views.download_receipt, name='download_receipt'),
]