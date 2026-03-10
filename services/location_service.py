# services/location_service.py

"""
Konum Servisi - GPS koordinatlarından şehir bilgisi al
Nominatim (OpenStreetMap) Reverse Geocoding API kullanıyor
"""

import requests
from typing import Optional, Dict

def get_city_from_coordinates(
    latitude: float, 
    longitude: float
) -> Optional[Dict]:
    """
    GPS koordinatlarından şehir bilgisi al (Reverse Geocoding)
    
    Args:
        latitude: Enlem (-90 ile 90 arası)
        longitude: Boylam (-180 ile 180 arası)
    
    Returns:
        dict: {
            'city': 'İzmir',
            'country': 'Turkey',
            'full_address': 'İzmir, Türkiye'
        }
        veya None (hata durumunda)
    
    Örnek:
        >>> city_info = get_city_from_coordinates(38.4192, 27.1287)
        >>> print(city_info['city'])
        'İzmir'
    """
    try:
        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/reverse"
        
        # Parametreler
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'accept-language': 'tr'  # Türkçe sonuç
        }
        
        # User-Agent zorunlu (Nominatim kuralı)
        headers = {
            'User-Agent': 'TarimAI/1.0'
        }
        
        # İstek gönder
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=5
        )
        
        # Başarılı yanıt kontrolü
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # Şehir bilgisini çıkar (öncelik sırasıyla)
            city = (
                address.get('province') or      # İl (Türkiye için)
                address.get('state') or         # Eyalet
                address.get('city') or          # Şehir
                address.get('town') or          # Kasaba
                address.get('village') or       # Köy
                'Bilinmeyen'
            )
            
            return {
                'city': city,
                'country': address.get('country', 'Turkey'),
                'full_address': data.get('display_name', '')
            }
        
        else:
            print(f" Nominatim HTTP {response.status_code}")
            return None
        
    except requests.exceptions.Timeout:
        print(" Nominatim zaman aşımı (timeout)")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f" Nominatim bağlantı hatası: {e}")
        return None
        
    except Exception as e:
        print(f" Konum servisi hatası: {e}")
        return None
