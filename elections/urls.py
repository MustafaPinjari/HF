from django.urls import path
from . import views

app_name = 'elections'

urlpatterns = [
    path('', views.election_list, name='election_list'),
    path('create/', views.election_create, name='create'),
    path('<int:election_id>/', views.election_detail, name='election_detail'),
    path('<int:election_id>/nominate/', views.submit_nomination, name='submit_nomination'),
    path('<int:election_id>/vote/<int:nomination_id>/', views.submit_vote, name='vote'),
    path('nominations/manage/', views.manage_nominations, name='manage_nominations'),
    path('nominations/<int:nomination_id>/review/', views.review_nomination, name='review_nomination'),
    path('<int:election_id>/register/', views.register_candidate, name='register_candidate'),
    path('<int:election_id>/delete/', views.delete_election, name='delete'),
    path('<int:election_id>/edit/', views.edit_election, name='edit'),
    path('<int:election_id>/vote_counts/', views.get_vote_counts, name='vote_counts'),
    path('<int:election_id>/apply/', views.apply_nomination, name='apply_nomination'),
]