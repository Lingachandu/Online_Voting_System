from django.urls import path
from . import views
urlpatterns = [path('cast-vote/<int:election_id>/', views.cast_vote, name='cast_vote')]