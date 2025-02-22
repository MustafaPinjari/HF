from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('facilities/', views.facility_list, name='facility_list'),
    path('book/<int:facility_id>/', views.book_facility, name='book'),
    path('pending-bookings/', views.pending_bookings, name='pending_bookings'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('admin-bookings/', views.admin_bookings, name='admin_bookings'),
    path('approve-booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('courses/', views.course_list, name='course_list'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('library/', views.library_resources, name='library_resources'),
    path('career-services/', views.career_services, name='career_services'),
    path('support-services/', views.support_services, name='support_services'),
    path('extracurricular-activities/', views.extracurricular_activities, name='extracurricular_activities'),
    path('alumni-network/', views.alumni_network, name='alumni_network'),
    path('transport-facilities/', views.transport_facilities, name='transport_facilities'),
    path('events/create/', views.create_event, name='create_event'),
    path('manage/', views.manage_facilities, name='manage_facilities'),
    path('facilities/management/', views.facility_management, name='facility_management'),
]