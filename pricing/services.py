"""
Restaurant Dynamic Pricing Services.

This module provides services for restaurant price analysis and dynamic pricing recommendations.
It integrates with Google Places API for restaurant data and OpenWeather API for weather conditions.

The pricing algorithm considers:
1. Current weather conditions (temperature and precipitation)
2. Restaurant busy levels
3. Competitor pricing in the area

Key Features:
- Restaurant search and details retrieval
- Weather data integration
- Dynamic pricing calculations
- Competitor analysis
"""

import os
import requests
from typing import Dict, List, Optional, Union
import json

class GooglePlacesService:
    """
    Service for interacting with Google Places API.
    
    This service handles all restaurant-related API calls including searching
    for restaurants, getting details, and finding nearby competitors.
    
    Attributes:
        api_key (str): Google Places API key from environment variables
        base_url (str): Base URL for Google Places API endpoints
    """

    def __init__(self):
        """Initialize the service with API key from environment variables."""
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = 'https://maps.googleapis.com/maps/api/place'

    def search_place(self, query: str, latitude: str, longitude: str) -> Dict:
        """
        Search for restaurants using the Google Places API.

        Args:
            query (str): Search query (restaurant name or keywords)
            latitude (str): Latitude coordinate for search center
            longitude (str): Longitude coordinate for search center

        Returns:
            Dict: API response containing search results or error message
                {
                    'results': [
                        {
                            'name': str,
                            'place_id': str,
                            'rating': float,
                            'price_level': int,
                            ...
                        }
                    ],
                    'error_message': Optional[str]
                }
        """
        try:
            url = f"{self.base_url}/textsearch/json"
            params = {
                'query': query,
                'location': f"{latitude},{longitude}",
                'radius': '5000',  # 5km radius
                'type': 'restaurant',
                'key': self.api_key
            }
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            return {'error_message': f"Failed to search place: {str(e)}"}

    def get_restaurant_details(self, place_id: str) -> Dict:
        """
        Get detailed information about a specific restaurant.

        Args:
            place_id (str): Google Places ID for the restaurant

        Returns:
            Dict: Detailed restaurant information
                {
                    'result': {
                        'name': str,
                        'formatted_address': str,
                        'rating': float,
                        'price_level': int,
                        'photos': List[Dict],
                        'geometry': Dict,
                        'opening_hours': Dict
                    },
                    'error_message': Optional[str]
                }
        """
        try:
            url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,rating,formatted_address,price_level,photos,geometry,opening_hours',
                'key': self.api_key
            }
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            return {'error_message': f"Failed to get place details: {str(e)}"}

    def search_nearby_restaurants(self, latitude: float, longitude: float) -> Dict:
        """
        Search for nearby restaurants within 1km radius.

        Args:
            latitude (float): Center point latitude
            longitude (float): Center point longitude

        Returns:
            Dict: Nearby restaurants information
                {
                    'results': [
                        {
                            'name': str,
                            'place_id': str,
                            'rating': float,
                            'price_level': int,
                            ...
                        }
                    ],
                    'error_message': Optional[str]
                }
        """
        try:
            url = f"{self.base_url}/nearbysearch/json"
            params = {
                'location': f"{latitude},{longitude}",
                'radius': '1000',  # 1km radius
                'type': 'restaurant',
                'key': self.api_key
            }
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            return {'error_message': f"Failed to search nearby restaurants: {str(e)}"}

    def get_place_busy_times(self, place_id: str) -> int:
        """
        Get current busy level for a restaurant.
        
        Note: This is currently a mock implementation. In production, this would
        integrate with Google Places API Premium for real-time popularity data.

        Args:
            place_id (str): Google Places ID for the restaurant

        Returns:
            int: Busy level percentage (0-100)
        """
        return 75  # Mock busy level for demonstration

class WeatherService:
    """
    Service for retrieving weather data from OpenWeather API.
    
    This service provides current weather conditions used in price calculations.
    
    Attributes:
        api_key (str): OpenWeather API key from environment variables
        base_url (str): Base URL for OpenWeather API
    """

    def __init__(self):
        """Initialize the service with API key from environment variables."""
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'

    def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """
        Get current weather data for a location.

        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude

        Returns:
            Dict: Current weather conditions
                {
                    'main': {
                        'temp': float,  # Temperature in Kelvin
                        'humidity': int,
                        ...
                    },
                    'weather': [{
                        'main': str,  # Weather condition (Rain, Snow, etc.)
                        'description': str
                    }]
                }
        """
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key
            }
            response = requests.get(self.base_url, params=params)
            return response.json()
        except Exception as e:
            return {'error': f"Failed to get weather data: {str(e)}"}

    @staticmethod
    def kelvin_to_fahrenheit(kelvin: float) -> float:
        """
        Convert temperature from Kelvin to Fahrenheit.

        Args:
            kelvin (float): Temperature in Kelvin

        Returns:
            float: Temperature in Fahrenheit
        """
        return (kelvin - 273.15) * 9/5 + 32

class PricingService:
    """
    Service for calculating dynamic menu item prices.
    
    This service implements the dynamic pricing algorithm that considers:
    1. Weather conditions (temperature and precipitation)
    2. Restaurant busy level
    3. Competitor pricing
    
    The pricing logic follows these rules:
    - If temperature < 45°F OR bad weather AND restaurant is busy (>70%):
        * Price = max(lowest_competitor_price * markup, base_price)
        * Markup ranges from 1.1 to 1.3 based on busy level
    - Otherwise:
        * Price = lowest_competitor_price
    """

    def calculate_price(
        self,
        base_price: float,
        weather_data: Dict,
        busy_level: int,
        competitor_prices: List[float]
    ) -> float:
        """
        Calculate the optimal price based on conditions and competition.

        Args:
            base_price (float): Original menu item price
            weather_data (Dict): Current weather conditions
                {
                    'temp': float,  # Temperature in Kelvin
                    'weather': [{'main': str}]  # Weather condition
                }
            busy_level (int): Current restaurant busy level (0-100)
            competitor_prices (List[float]): List of competitor prices for similar items

        Returns:
            float: Calculated optimal price

        Example:
            >>> service = PricingService()
            >>> weather = {'temp': 283.15, 'weather': [{'main': 'Rain'}]}
            >>> price = service.calculate_price(15.99, weather, 80, [14.99, 16.99])
            >>> print(f"${price:.2f}")  # $16.49
        """
        if not competitor_prices:
            return base_price

        lowest_price = min(competitor_prices)
        
        # Convert temperature from Kelvin to Fahrenheit
        temp_kelvin = weather_data.get('temp', 293.15)  # Default to 20°C
        temp_f = (temp_kelvin - 273.15) * 9/5 + 32
        
        # Check weather condition
        weather_conditions = weather_data.get('weather', [{'main': 'Clear'}])[0].get('main', 'Clear')
        bad_weather = weather_conditions in ['Rain', 'Snow', 'Thunderstorm']
        
        # Define what "busier than usual" means (>70%)
        busier_than_usual = busy_level > 70
        
        # Apply pricing logic
        if (temp_f < 45 or bad_weather) and busier_than_usual:
            # Add 10-20% markup depending on how busy
            markup = 1.1 + (busy_level - 70) / 100  # 1.1 to 1.3 markup
            return max(lowest_price * markup, base_price)
        else:
            return lowest_price

    def get_sample_menu(self) -> List[Dict]:
        """
        Get a sample menu with base prices.

        Returns:
            List[Dict]: List of menu items with base prices
                [
                    {
                        'name': str,
                        'base_price': float
                    },
                    ...
                ]
        """
        return [
            {'name': 'Butter Chicken', 'base_price': 16.99},
            {'name': 'Chicken Tikka Masala', 'base_price': 15.99},
            {'name': 'Vegetable Biryani', 'base_price': 14.99},
            {'name': 'Naan', 'base_price': 3.99},
            {'name': 'Dal Makhani', 'base_price': 12.99},
            {'name': 'Palak Paneer', 'base_price': 13.99},
            {'name': 'Tandoori Roti', 'base_price': 2.99},
            {'name': 'Mango Lassi', 'base_price': 4.99},
        ]
