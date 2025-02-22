from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list, name='list'),
    path('create/', views.create_complaint, name='create'),
    path('<int:pk>/', views.complaint_detail, name='detail'),
    path('<int:pk>/respond/', views.add_response, name='respond'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
]