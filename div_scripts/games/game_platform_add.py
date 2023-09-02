# Ujistěte se, že tento skript je umístěn ve stejném adresáři jako manage.py,
# nebo nastavte Django settings module jinak.

import os
import requests
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'div_app.settings')
application = get_wsgi_application()

from div_app.models import GamePlatform  # Změňte na název vaší aplikace

API_URL = "https://api.rawg.io/api/platforms"
API_KEY = "cab2943bd7714d0cb8511704d09c0ce7"  # Změňte na váš nový API klíč

def fetch_platforms(api_url, api_key):
    headers = {'User-Agent': 'MyApp/1.0.0 (by info@div.cz)', 'Authorization': f'Bearer {api_key}'}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Failed to get data: {response.status_code}")
        return None

platforms_data = fetch_platforms(API_URL, API_KEY)

if platforms_data:
    for platform in platforms_data:
        name = platform['name']
        GamePlatform.objects.create(Platform=name)

    print("Data successfully inserted.")
