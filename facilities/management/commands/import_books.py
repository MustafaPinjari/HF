from django.core.management.base import BaseCommand
import csv
from facilities.models import Book

class Command(BaseCommand):
    help = 'Import books from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Match the CSV column names exactly
                    Book.objects.get_or_create(
                        title=row['Book Title'],
                        defaults={
                            'author': row['Book Author'],
                            'publication_year': int(row['Year of Publication']),
                            'publisher': row['Publisher'],
                            'book_link': row['Book Link (PDF)'],
                            'available_copies': 1,
                            'total_copies': 1
                        }
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully imported "{row["Book Title"]}"')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error importing "{row["Book Title"]}": {str(e)}')
                    )

        self.stdout.write(self.style.SUCCESS('Successfully imported books')) 