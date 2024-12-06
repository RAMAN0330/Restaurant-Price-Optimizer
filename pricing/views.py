from django.shortcuts import render
from django.views import View
from datetime import datetime
from .services import GooglePlacesService, WeatherService, PricingService
from .models import Restaurant, MenuItem, WeatherData, BusyTimesData
import os

class PricingView(View):
    def __init__(self):
        self.google_service = GooglePlacesService()
        self.weather_service = WeatherService()
        self.pricing_service = PricingService()

    def get(self, request):
        search_query = request.GET.get('restaurant')
        selected_place_id = request.GET.get('place_id')
        
        if not search_query and not selected_place_id:
            # Show the initial search form
            return render(request, 'pricing/search.html')
        
        if search_query and not selected_place_id:
            # Search for restaurants and show results
            search_results = self.google_service.search_place(
                search_query,
                request.GET.get('latitude', '40.7631'),  # Default to Hicksville coordinates
                request.GET.get('longitude', '-73.5267')
            )
            
            context = {
                'search_query': search_query,
                'restaurants': search_results.get('results', []),
                'google_maps_api_key': os.getenv('GOOGLE_MAPS_API_KEY'),
                'error_message': search_results.get('error_message')
            }
            return render(request, 'pricing/search_results.html', context)
        
        # Get details for selected restaurant
        restaurant_details = self.google_service.get_restaurant_details(selected_place_id)
        
        if 'error_message' in restaurant_details:
            context = {'error': restaurant_details['error_message']}
            return render(request, 'pricing/error.html', context)

        # Safely get restaurant result
        result = restaurant_details.get('result', {})
        if not result:
            context = {'error': 'Unable to fetch restaurant details'}
            return render(request, 'pricing/error.html', context)

        # Safely get location data
        location = result.get('geometry', {}).get('location', {})
        latitude = location.get('lat', 40.7631)  # Default to Hicksville coordinates
        longitude = location.get('lng', -73.5267)
        
        try:
            # Get nearby restaurants
            nearby_restaurants = self.google_service.search_nearby_restaurants(
                latitude, 
                longitude
            )
            
            # Get current weather
            weather_data = self.weather_service.get_current_weather(
                latitude,
                longitude
            )
            
            # Get current busy level
            current_busy_level = self.google_service.get_place_busy_times(selected_place_id)
            
            # Get menu items (if available in Google Places API)
            menu_items = []
            if result.get('photos', []):  # Using photos as a proxy for having detailed data
                # Sample menu items since Google Places API doesn't provide menu items
                sample_menu_items = [
                    {'name': 'Butter Chicken', 'price': 16.99},
                    {'name': 'Chicken Tikka Masala', 'price': 15.99},
                    {'name': 'Vegetable Biryani', 'price': 14.99},
                    {'name': 'Naan', 'price': 3.99},
                ]
                
                # Calculate prices for sample menu items
                for item in sample_menu_items:
                    # Get competitor prices from nearby restaurants
                    competitor_prices = []
                    for restaurant in nearby_restaurants.get('results', [])[:5]:
                        if restaurant.get('price_level'):
                            competitor_price = item['price'] * (restaurant['price_level'] / 2)
                            competitor_prices.append(competitor_price)
                    
                    if competitor_prices:
                        new_price = self.pricing_service.calculate_price(
                            item['price'],
                            weather_data.get('main', {}),
                            current_busy_level,
                            competitor_prices
                        )
                        menu_items.append({
                            'name': item['name'],
                            'original_price': item['price'],
                            'new_price': new_price,
                            'price_change': ((new_price - item['price']) / item['price']) * 100
                        })
            
            context = {
                'restaurant_details': {
                    'name': result.get('name', 'Unknown Restaurant'),
                    'address': result.get('formatted_address', 'Address not available'),
                    'rating': result.get('rating', 'N/A'),
                    'total_ratings': result.get('user_ratings_total', 0),
                    'price_level': '₹' * result.get('price_level', 1) if result.get('price_level') else 'N/A',
                    'photos': result.get('photos', [])[:5]
                },
                'nearby_restaurants': [
                    {
                        'name': r.get('name', 'Unknown'),
                        'rating': r.get('rating', 'N/A'),
                        'total_ratings': r.get('user_ratings_total', 0),
                        'price_level': '₹' * r.get('price_level', 1) if r.get('price_level') else 'N/A',
                        'distance': r.get('distance', 'N/A')
                    }
                    for r in nearby_restaurants.get('results', [])[:5]
                ],
                'weather_data': {
                    'temperature_f': self.weather_service.kelvin_to_fahrenheit(
                        weather_data.get('main', {}).get('temp', 293.15)  # Default to 20°C
                    ),
                    'condition': weather_data.get('weather', [{}])[0].get('main', 'Unknown'),
                    'description': weather_data.get('weather', [{}])[0].get('description', 'Weather data not available')
                },
                'busy_level': current_busy_level if isinstance(current_busy_level, (int, float)) else 50,
                'menu_items': menu_items
            }
            
            return render(request, 'pricing/pricing.html', context)
            
        except Exception as e:
            context = {'error': f'An error occurred while analyzing the restaurant: {str(e)}'}
            return render(request, 'pricing/error.html', context)
