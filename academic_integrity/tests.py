from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import CheatingCase, Sanction, Appeal
from django.utils import timezone

class AcademicIntegrityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create faculty user with permissions
        self.faculty_user = User.objects.create_user(
            username='faculty',
            email='faculty@example.com',
            password='facultypass123'
        )
        
        # Add necessary permissions to faculty user
        content_type = ContentType.objects.get_for_model(CheatingCase)
        permissions = Permission.objects.filter(content_type=content_type)
        self.faculty_user.user_permissions.add(*permissions)
        self.faculty_user.is_staff = True
        self.faculty_user.save()
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123'
        )
        
        # Create a test case
        self.test_case = CheatingCase.objects.create(
            student=self.student_user,
            reported_by=self.faculty_user,
            course='Test Course 101',
            exam_date=timezone.now().date(),
            violation_type='exam_cheating',
            severity='moderate',
            description='Test case description',
            status='pending'
        )
        
        # Set up the test client
        self.client = Client()

    def test_case_list_view(self):
        # Test unauthorized access
        response = self.client.get(reverse('academic_integrity:case_list'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Test faculty access with proper permissions
        self.client.login(username='faculty', password='facultypass123')
        response = self.client.get(reverse('academic_integrity:case_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_case_creation(self):
        self.client.login(username='faculty', password='facultypass123')
        
        # Create a test file for evidence
        test_file = SimpleUploadedFile(
            "test_evidence.txt",
            b"Test evidence content",
            content_type="text/plain"
        )
        
        case_data = {
            'student': self.student_user.id,
            'course': 'Math 101',
            'exam_date': timezone.now().date(),
            'violation_type': 'exam_cheating',
            'severity': 'moderate',
            'description': 'Test case creation',
            'evidence': test_file
        }
        
        response = self.client.post(
            reverse('academic_integrity:report_case'), 
            case_data,
            format='multipart'
        )
        self.assertEqual(CheatingCase.objects.count(), 2)
        
    def test_appeal_submission(self):
        self.client.login(username='student', password='studentpass123')
        
        # Create a test file for supporting evidence
        test_file = SimpleUploadedFile(
            "test_appeal.txt",
            b"Test appeal evidence",
            content_type="text/plain"
        )
        
        appeal_data = {
            'grounds': 'Test appeal grounds',
            'supporting_evidence': test_file
        }
        
        response = self.client.post(
            reverse('academic_integrity:submit_appeal', kwargs={'case_pk': self.test_case.pk}),
            appeal_data,
            format='multipart'
        )
        self.assertEqual(Appeal.objects.count(), 1)

    def test_sanction_addition(self):
        self.client.login(username='faculty', password='facultypass123')
        
        sanction_data = {
            'sanction_type': 'warning',
            'description': 'Test sanction',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date()
        }
        
        response = self.client.post(
            reverse('academic_integrity:add_sanction', kwargs={'case_pk': self.test_case.pk}),
            sanction_data
        )
        self.assertEqual(Sanction.objects.count(), 1)

    def tearDown(self):
        # Clean up uploaded files
        for case in CheatingCase.objects.all():
            if case.evidence:
                case.evidence.delete()
        for appeal in Appeal.objects.all():
            if appeal.supporting_evidence:
                appeal.supporting_evidence.delete()
