from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from academic_integrity.models import CheatingCase, Sanction, Appeal
import random

class Command(BaseCommand):
    help = 'Creates test data for academic integrity system'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Create test users if they don't exist
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin.set_password('adminpass123')
        admin.save()

        faculty, _ = User.objects.get_or_create(
            username='faculty',
            defaults={'email': 'faculty@example.com'}
        )
        faculty.set_password('facultypass123')
        faculty.save()

        # Create some test students
        students = []
        for i in range(5):
            student, _ = User.objects.get_or_create(
                username=f'student{i}',
                defaults={'email': f'student{i}@example.com'}
            )
            student.set_password(f'studentpass{i}123')
            student.save()
            students.append(student)

        # Create test cases
        courses = ['Math 101', 'Physics 202', 'Chemistry 301', 'Biology 401']
        violation_types = ['exam_cheating', 'plagiarism', 'unauthorized_materials']
        severities = ['minor', 'moderate', 'major']
        statuses = ['pending', 'under_investigation', 'resolved']

        for student in students:
            for _ in range(random.randint(1, 3)):
                case = CheatingCase.objects.create(
                    student=student,
                    reported_by=faculty,
                    course=random.choice(courses),
                    exam_date=timezone.now().date(),
                    violation_type=random.choice(violation_types),
                    severity=random.choice(severities),
                    description=f'Test case for {student.username}',
                    status=random.choice(statuses)
                )

                # Add sanctions for some cases
                if case.status == 'resolved':
                    Sanction.objects.create(
                        case=case,
                        sanction_type='warning',
                        description='Test sanction',
                        start_date=timezone.now().date(),
                        issued_by=admin
                    )

                # Add appeals for some cases
                if random.choice([True, False]):
                    Appeal.objects.create(
                        case=case,
                        submitted_by=student,
                        grounds='Test appeal grounds',
                        status='pending'
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 