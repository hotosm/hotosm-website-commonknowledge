from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="info@hotosm.org")
GeolocatorError = GeocoderUnavailable
