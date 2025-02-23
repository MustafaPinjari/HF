from django.contrib import admin
from .models import Facility, Course, Event, LibraryResource, CareerService, SupportService, ExtracurricularActivity, Alumni, TransportFacility, Booking, Book, BookRequest
from django.urls import path
from django.shortcuts import render, redirect

# Register your models here.
@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'created_by', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('name', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'credits', 'department')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'sponsor', 'budget', 'expenses', 'sponsorship_amount')
    list_filter = ('date', 'sponsor')
    search_fields = ('title', 'sponsor')
    readonly_fields = ('created_at',)
    fields = ('title', 'date', 'sponsor', 'image', 'budget', 'expenses', 
             'sponsorship_amount', 'utilization_details', 'expense_proof')

@admin.register(LibraryResource)
class LibraryResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'resource_type', 'availability')

@admin.register(CareerService)
class CareerServiceAdmin(admin.ModelAdmin):
    list_display = ('description',)

@admin.register(SupportService)
class SupportServiceAdmin(admin.ModelAdmin):
    list_display = ('description',)

@admin.register(ExtracurricularActivity)
class ExtracurricularActivityAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('name', 'graduation_year', 'linkedin_profile')

@admin.register(TransportFacility)
class TransportFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'facility', 'start_time', 'end_time', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'facility__name')

    actions = ['approve_bookings', 'reject_bookings']

    def approve_bookings(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "Selected bookings have been approved.")
    
    def reject_bookings(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected bookings have been rejected.")

    approve_bookings.short_description = "Approve selected bookings"
    reject_bookings.short_description = "Reject selected bookings"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pending-bookings/', self.admin_site.admin_view(self.pending_bookings), name='pending_bookings'),
        ]
        return custom_urls + urls

    def pending_bookings(self, request):
        bookings = Booking.objects.filter(status='pending')
        context = {
            'bookings': bookings,
            'title': 'Pending Bookings',
        }
        return render(request, 'facilities/pending_bookings.html', context)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'publication_year', 'available_copies', 'total_copies')
    search_fields = ('title', 'author', 'publisher')
    list_filter = ('publication_year', 'publisher')

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'request_date', 'due_date', 'status')
    list_filter = ('status', 'request_date')
    search_fields = ('book__title', 'user__username')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for book_request in queryset.filter(status='pending'):
            if book_request.book.available_copies > 0:
                book_request.status = 'approved'
                book_request.book.available_copies -= 1
                book_request.book.save()
                book_request.save()
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')
    reject_requests.short_description = "Reject selected requests"