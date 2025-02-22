from django.core.mail import send_mail
from django.conf import settings

def send_booking_notification(booking):
    subject = f'New Facility Booking Request: {booking.facility.name}'
    message = f'''
    A new booking request has been submitted:
    
    Facility: {booking.facility.name}
    User: {booking.user.get_full_name()}
    Date: {booking.start_time.date()}
    Time: {booking.start_time.time()} - {booking.end_time.time()}
    Purpose: {booking.purpose}
    '''
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )

def send_complaint_notification(complaint):
    subject = f'New Complaint Submitted: {complaint.title}'
    message = f'''
    A new complaint has been submitted:
    
    Title: {complaint.title}
    By: {complaint.get_author_display()}
    Status: {complaint.status}
    Description: {complaint.description}
    '''
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )