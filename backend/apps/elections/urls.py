from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/voter/', views.voter_dashboard, name='voter_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
]