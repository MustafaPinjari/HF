from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_confirmation, name='logout_confirmation'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('submit_health_request/', views.submit_health_request, name='submit_health_request'),
    path('submit_leave_request/', views.submit_leave_request, name='submit_leave_request'),
]