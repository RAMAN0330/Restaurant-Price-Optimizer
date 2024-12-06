from django.core.management.base import BaseCommand
from pricing.services import GooglePlacesService

class Command(BaseCommand):
    help = 'Find Google Place ID for a restaurant'

    def add_arguments(self, parser):
        parser.add_argument('restaurant_name', type=str, help='Name of the restaurant to search for')

    def handle(self, *args, **options):
        service = GooglePlacesService()
        # Village restaurant coordinates (Hicksville)
        latitude = 40.7631
        longitude = -73.5267
        
        results = service.search_place(options['restaurant_name'], latitude, longitude)
        
        if 'results' in results:
            self.stdout.write(self.style.SUCCESS('Search Results:'))
            for place in results['results']:
                self.stdout.write(f"\nName: {place.get('name')}")
                self.stdout.write(f"Address: {place.get('formatted_address')}")
                self.stdout.write(f"Place ID: {place.get('place_id')}")
                self.stdout.write('-' * 50)
        else:
            self.stdout.write(self.style.ERROR(f"Error: {results.get('error_message', 'No results found')}"))
