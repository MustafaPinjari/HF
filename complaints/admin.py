from django.contrib import admin
from django.forms.widgets import HiddenInput
from .models import Complaint
from django.core.mail import send_mail
from django.conf import settings
import logging
from django import forms
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class ComplaintAdminForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = '__all__'  # Ensure all fields are included

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        user = cleaned_data.get("user")

        if status == 'resolved' and not user:
            logger.debug(f"Validation Error: Status is 'resolved' but user is {user}")
            raise ValidationError("A user must be assigned to resolve the complaint.")

class ComplaintAdmin(admin.ModelAdmin):
    form = ComplaintAdminForm
    list_display = ('title', 'status', 'created_at', 'get_user_display')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')

    def get_user_display(self, obj):
        return "Anonymous" if obj.is_anonymous else obj.user.get_full_name()
    get_user_display.short_description = 'Submitted By'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.is_anonymous:
            # Hide the user field if the complaint is anonymous
            form.base_fields['user'].widget = HiddenInput()
        return form

    def save_model(self, request, obj, form, change):
        logger.debug(f"Saving complaint: {obj.title}, Status: {obj.status}, User: {obj.user}")
        
        # If the complaint is anonymous, ensure the user field is not set
        if obj.is_anonymous:
            obj.user = None  # Explicitly set user to None for anonymous complaints

        # Check if the status is being changed to 'resolved'
        if obj.status == 'resolved':
            # Assign a user in the backend (you can customize this logic)
            obj.user = request.user  # Assign the logged-in user

            # Only send email if user is assigned
            if obj.user:
                try:
                    send_mail(
                        'Your Complaint has been Resolved',
                        f'Hello {obj.user.get_full_name()},\n\nYour complaint "{obj.title}" has been resolved.',
                        settings.DEFAULT_FROM_EMAIL,
                        [obj.user.email],
                        fail_silently=False,
                    )
                    logger.info(f'Email sent to {obj.user.email} regarding complaint "{obj.title}".')
                except Exception as e:
                    logger.error(f'Error sending email: {e}')

        super().save_model(request, obj, form, change)

admin.site.register(Complaint, ComplaintAdmin)