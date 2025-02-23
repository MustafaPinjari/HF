from django.urls import path
from . import views

app_name = 'academic_integrity'

urlpatterns = [
    path('cases/', views.case_list, name='case_list'),
    path('cases/report/', views.report_case, name='report_case'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/<int:case_pk>/sanction/', views.add_sanction, name='add_sanction'),
    path('cases/<int:case_pk>/appeal/', views.submit_appeal, name='submit_appeal'),
    path('cases/<int:pk>/update/', views.update_case, name='update_case'),
]