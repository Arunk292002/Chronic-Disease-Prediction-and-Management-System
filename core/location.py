import requests
import time
import urllib.parse

def geocode_address(address):
    """Convert an address to latitude and longitude using OpenStreetMap (Nominatim)"""
    if not address.strip():
        return None, None
        
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }
    
    try:
        # Adding User-Agent header to comply with Nominatim usage policy
        headers = {"User-Agent": "HealthcareAssistantApp/1.0"}
        response = requests.get(url, params=params, headers=headers)
        
        # Respect Nominatim rate limits (max 1 request per second)
        time.sleep(1)
        
        if response.ok and response.json():
            location = response.json()[0]
            # Also return the formatted display name for verification
            display_name = location.get('display_name', '')
            return float(location['lat']), float(location['lon']), display_name
        return None, None, None
    except Exception as e:
        print(f"Error in OSM geocoding: {e}")
        return None, None, None

def get_nearby_hospitals(lat, lon, radius=5000, limit=10):
    """Get hospitals near a location using Overpass API (OpenStreetMap)"""
    user_lat, user_lon = lat, lon  # Preserve original coordinates

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{user_lat},{user_lon});
      way["amenity"="hospital"](around:{radius},{user_lat},{user_lon});
      relation["amenity"="hospital"](around:{radius},{user_lat},{user_lon});
      node["healthcare"="hospital"](around:{radius},{user_lat},{user_lon});
      way["healthcare"="hospital"](around:{radius},{user_lat},{user_lon});
      relation["healthcare"="hospital"](around:{radius},{user_lat},{user_lon});
    );
    out center;
    """

    try:
        url = "https://overpass-api.de/api/interpreter"
        headers = {"User-Agent": "HealthcareAssistantApp/1.0"}
        response = requests.post(url, data=query, headers=headers)

        hospitals = []
        if response.ok:
            data = response.json()
            for element in data.get("elements", []):
                if element.get("type") in ["way", "relation"]:
                    if "center" in element:
                        hosp_lat = element["center"]["lat"]
                        hosp_lon = element["center"]["lon"]
                    else:
                        continue
                else:
                    hosp_lat = element.get("lat")
                    hosp_lon = element.get("lon")

                tags = element.get("tags", {})
                name = tags.get("name", "Unnamed Hospital")

                address_parts = []
                if tags.get("addr:street"):
                    address_parts.append(tags.get("addr:street"))
                if tags.get("addr:housenumber"):
                    address_parts.append(tags.get("addr:housenumber"))
                if tags.get("addr:city"):
                    address_parts.append(tags.get("addr:city"))

                address = ", ".join(address_parts) if address_parts else "Address not available"
                phone = tags.get("phone", "")
                emergency = "Yes" if tags.get("emergency") == "yes" else "Unknown"

                hospitals.append({
                    "name": name,
                    "lat": hosp_lat,
                    "lon": hosp_lon,
                    "address": address,
                    "phone": phone,
                    "emergency": emergency
                })

            # Sort hospitals by proximity to original coordinates
            def calculate_distance(hospital):
                from math import radians, cos, sin, asin, sqrt
                lon1, lat1, lon2, lat2 = map(radians, [user_lon, user_lat, hospital["lon"], hospital["lat"]])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * asin(sqrt(a))
                r = 6371  # Earth radius in km
                return c * r

            for hospital in hospitals:
                hospital["distance"] = calculate_distance(hospital)

            hospitals.sort(key=lambda x: x["distance"])

            return hospitals[:limit]

        return []
    except Exception as e:
        print(f"Error fetching OSM hospitals: {e}")
        return []

def validate_address(address):
    """
    Validate if address exists and return suggestions if needed
    Improved to handle more specific address formats
    """
    if not address.strip():
        return False, [], None
    
    # Preprocessing to improve address matching
    # Remove extra whitespaces and standardize address format
    address = ' '.join(address.split())
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'addressdetails': 1,
        'limit': 5  # Get multiple results for suggestions
    }
    
    try:
        headers = {"User-Agent": "HealthcareAssistantApp/1.0"}
        response = requests.get(url, params=params, headers=headers)
        
        # Respect rate limits
        time.sleep(1)
        
        results = response.json() if response.ok else []
        
        # If no results, try different strategies
        if not results:
            # Strategy 1: Remove house number and try again
            no_house_number = ' '.join([part for part in address.split() if not part.replace(',','').isdigit()])
            
            params['q'] = no_house_number
            response = requests.get(url, params=params, headers=headers)
            time.sleep(1)
            results = response.json() if response.ok else []
        
        # If still no results, try more lenient search
        if not results:
            # Strategy 2: Use only city and state/region
            parts = address.split(',')
            if len(parts) >= 3:
                lenient_search = f"{parts[-3]}, {parts[-2]}, {parts[-1]}"
                params['q'] = lenient_search
                response = requests.get(url, params=params, headers=headers)
                time.sleep(1)
                results = response.json() if response.ok else []
        
        if not results:
            return False, [], None
        
        # If we have results, the first one is most relevant
        primary_result = results[0]
        
        # Create suggestions list
        suggestions = [item.get('display_name', '') for item in results]
        
        # Prioritize suggestions that are most similar to the original address
        def address_similarity_score(suggestion):
            # Count matching words
            suggestion_words = set(suggestion.lower().split())
            input_words = set(address.lower().split())
            return len(suggestion_words.intersection(input_words))
        
        suggestions.sort(key=address_similarity_score, reverse=True)
        
        return True, suggestions, primary_result
    except Exception as e:
        print(f"Error validating address: {e}")
        return False, [], None
def reverse_geocode_osm(lat, lon):
    """Get full address from coordinates using Nominatim reverse geocoding"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'zoom': 18,
        'addressdetails': 1
    }
    headers = {"User-Agent": "HealthcareAssistantApp/1.0"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        time.sleep(1)  # Respect rate limit
        if response.ok:
            data = response.json()
            return data.get("display_name", "Address not available")
        return "Address not available"
    except Exception as e:
        print(f"Error in reverse geocoding: {e}")
        return "Address not available"
import urllib.parse

def generate_google_maps_search_link(address):
    """
    Generate a Google Maps search link based on the hospital address.
    
    Args:
        address (str): Full address of the hospital
    
    Returns:
        str: Google Maps search URL
    """
    # URL encode the address
    encoded_address = urllib.parse.quote(address)
    
    # Generate Google Maps search URL
    return f"https://www.google.com/maps/search/?api=1&query={encoded_address}"

def generate_google_maps_directions_link(start_address, hospital_address):
    """
    Generate a Google Maps directions link between two addresses
    
    Args:
        start_address (str): Starting address (user's input address)
        hospital_address (str): Destination hospital address
    
    Returns:
        str: Google Maps directions URL
    """
    
    # URL encode both addresses
    encoded_start = urllib.parse.quote(start_address)
    encoded_hospital = urllib.parse.quote(hospital_address)
    
    # Generate Google Maps directions URL
    return f"https://www.google.com/maps/dir/?api=1&origin={encoded_start}&destination={encoded_hospital}"