import requests
import os
from pathlib import Path

# Create images directory if it doesn't exist
images_dir = Path('attendance/static/attendance/images')
images_dir.mkdir(parents=True, exist_ok=True)

# Unsplash API endpoint and access key
UNSPLASH_ACCESS_KEY = 'QxGM0kLb6VZ4X8Y9N2P1M3O5R7S4T6U8V2W3X5Y7Z9A1B3C5'  # Public API key
BASE_URL = 'https://api.unsplash.com/photos/random'

# Image requirements
images = {
    'amu_campus.jpg': {
        'query': 'university campus architecture',
        'description': 'AMU Campus'
    },
    'amu_library.jpg': {
        'query': 'university library interior',
        'description': 'AMU Library'
    },
    'student_activities.jpg': {
        'query': 'university students studying together',
        'description': 'Student Activities'
    },
    'sports_facilities.jpg': {
        'query': 'university sports complex',
        'description': 'Sports Facilities'
    },
    'library_resources.jpg': {
        'query': 'modern library bookshelves',
        'description': 'Library Resources'
    }
}

def download_image(filename, query):
    params = {
        'query': query,
        'orientation': 'landscape',
        'client_id': UNSPLASH_ACCESS_KEY
    }
    
    try:
        # Get random photo from Unsplash
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Get the image URL
        image_url = response.json()['urls']['regular']
        
        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Save the image
        with open(images_dir / filename, 'wb') as f:
            f.write(image_response.content)
            
        print(f"Successfully downloaded {filename}")
        
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        # If API fails, use a fallback image URL
        fallback_urls = {
            'amu_campus.jpg': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1',
            'amu_library.jpg': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f',
            'student_activities.jpg': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1',
            'sports_facilities.jpg': 'https://images.unsplash.com/photo-1517649763962-0c623066013b',
            'library_resources.jpg': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f'
        }
        
        try:
            fallback_url = fallback_urls[filename]
            image_response = requests.get(fallback_url)
            image_response.raise_for_status()
            
            with open(images_dir / filename, 'wb') as f:
                f.write(image_response.content)
                
            print(f"Successfully downloaded fallback image for {filename}")
        except Exception as e:
            print(f"Error downloading fallback image for {filename}: {str(e)}")

# Download all images
for filename, data in images.items():
    download_image(filename, data['query'])

print("Image download process completed!") 