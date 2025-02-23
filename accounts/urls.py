from django.urls import path
from . import views
from .views import CustomLoginView

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/confirmation/', views.logout_confirmation, name='logout_confirmation'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/faculty-sports/', views.faculty_sports_dashboard, name='faculty_sports_dashboard'),
    path('dashboard/faculty-lab/', views.faculty_lab_dashboard, name='faculty_lab_dashboard'),
    path('dashboard/faculty-transport/', views.faculty_transport_dashboard, name='faculty_transport_dashboard'),
    path('dashboard/faculty-hod/', views.faculty_hod_dashboard, name='faculty_hod_dashboard'),
    path('dashboard/faculty-teaching/', views.faculty_teaching_dashboard, name='faculty_teaching_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('register/', views.role_selection, name='role_selection'),
    path('register/<str:role>/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('submit_health_request/', views.submit_health_request, name='submit_health_request'),
    path('submit_leave_request/', views.submit_leave_request, name='submit_leave_request'),
    path('approve_booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('handle-book-request/<int:request_id>/', views.handle_book_request, name='handle_book_request'),
    path('handle-lab-complaint/<int:complaint_id>/', views.handle_lab_complaint, name='handle_lab_complaint'),
    path('broadcast-announcement/', views.broadcast_announcement, name='broadcast_announcement'),
    path('leave-request/<int:request_id>/review/', 
         views.review_leave_request, 
         name='review_leave_request'),
    path('student/<str:username>/', views.student_profile, name='student_profile'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.manage_course, name='add_course'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.manage_course, name='edit_course'),
    path('courses/<int:course_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('courses/<int:course_id>/grades/', views.update_grades, name='update_grades'),
]