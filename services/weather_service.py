# services/weather_service.py

"""
Hava Durumu Servisi - OpenWeatherMap API
- Anlık hava durumu
- 5 günlük 3 saatlik tahmin
"""

import requests
import os
from typing import Optional, Dict, List
from datetime import datetime

def get_weather(city: str) -> Optional[Dict]:
    """
    Şehir için ANLIK hava durumu al
    
    Args:
        city: Şehir adı (örn: "İzmir")
    
    Returns:
        dict: {
            'temperature': 18.5,
            'humidity': 65,
            'will_rain': False,
            'description': 'açık'
        }
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            print(" OPENWEATHER_API_KEY environment variable bulunamadı!")
            return None
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        
        params = {
            'q': f"{city},TR",
            'appid': api_key,
            'units': 'metric',
            'lang': 'tr'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Yağmur kontrolü
            will_rain = (
                'rain' in data or 
                'drizzle' in data or
                data.get('weather', [{}])[0].get('main', '').lower() in ['rain', 'drizzle', 'thunderstorm']
            )
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'will_rain': will_rain,
                'description': data['weather'][0]['description'] if data.get('weather') else 'Bilinmiyor'
            }
        
        elif response.status_code == 404:
            print(f" Şehir bulunamadı: {city}")
            return None
        
        elif response.status_code == 401:
            print(" OpenWeather API key geçersiz!")
            return None
        
        else:
            print(f" OpenWeather HTTP {response.status_code}")
            return None
        
    except Exception as e:
        print(f" Hava durumu hatası: {e}")
        return None


def get_weather_forecast(city: str, hours: int = 24) -> Optional[Dict]:
    """
    Şehir için İLERİ SAATLERİN hava tahmini al
    
    OpenWeather 5 günlük / 3 saatlik tahmin veriyor:
    - Her 3 saatte bir veri noktası
    - 5 gün × 8 veri = 40 veri noktası
    
    Args:
        city: Şehir adı (örn: "İzmir")
        hours: Kaç saat sonrasına kadar (default: 24 saat = 8 veri noktası)
    
    Returns:
        dict: {
            'will_rain_soon': True/False,  # İlerleyen saatlerde yağmur var mı?
            'rain_probability': 60,         # Yağmur olasılığı (%)
            'max_temp': 28.5,              # En yüksek sıcaklık
            'min_temp': 15.2,              # En düşük sıcaklık
            'hourly_forecast': [           # Saatlik detay
                {
                    'time': '2025-01-29 15:00',
                    'temp': 18.5,
                    'rain': True,
                    'description': 'hafif yağmur'
                },
                ...
            ]
        }
    
    Örnek Kullanım:
        >>> forecast = get_weather_forecast("İzmir", hours=24)
        >>> if forecast['will_rain_soon']:
        >>>     print("24 saat içinde yağmur bekleniyor!")
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            print(" OPENWEATHER_API_KEY environment variable bulunamadı!")
            return None
        
        # OpenWeather 5 günlük tahmin endpoint'i
        url = "https://api.openweathermap.org/data/2.5/forecast"
        
        params = {
            'q': f"{city},TR",
            'appid': api_key,
            'units': 'metric',
            'lang': 'tr'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            print(f" Forecast API HTTP {response.status_code}")
            return None
        
        data = response.json()
        
        # Kaç veri noktası alalım? (3 saatlik aralıklar)
        num_points = min(hours // 3, len(data.get('list', [])))
        
        if num_points == 0:
            return None
        
        # Verileri işle
        forecast_list = data['list'][:num_points]
        
        temps = []
        will_rain = False
        rain_count = 0
        hourly_forecast = []
        
        for item in forecast_list:
            # Sıcaklık
            temp = item['main']['temp']
            temps.append(temp)
            
            # Yağmur kontrolü
            has_rain = (
                'rain' in item or
                item.get('weather', [{}])[0].get('main', '').lower() in ['rain', 'drizzle', 'thunderstorm']
            )
            
            if has_rain:
                will_rain = True
                rain_count += 1
            
            # Saatlik detay
            hourly_forecast.append({
                'time': item['dt_txt'],  # "2025-01-29 15:00:00"
                'temp': temp,
                'humidity': item['main']['humidity'],
                'rain': has_rain,
                'description': item['weather'][0]['description'] if item.get('weather') else 'Bilinmiyor'
            })
        
        # Yağmur olasılığı (%)
        rain_probability = int((rain_count / num_points) * 100)
        
        return {
            'will_rain_soon': will_rain,
            'rain_probability': rain_probability,
            'max_temp': max(temps) if temps else None,
            'min_temp': min(temps) if temps else None,
            'avg_temp': sum(temps) / len(temps) if temps else None,
            'hourly_forecast': hourly_forecast,
            'forecast_hours': hours
        }
        
    except Exception as e:
        print(f" Forecast hatası: {e}")
        return None


def get_extended_weather(city: str) -> Optional[Dict]:
    """
    Gelişmiş hava durumu - Anlık + Tahmin birlikte
    
    Bu fonksiyon iki API'yi birleştiriyor:
    1. Anlık hava durumu
    2. 24 saatlik tahmin
    
    Args:
        city: Şehir adı
    
    Returns:
        dict: {
            'current': {...},      # Anlık
            'forecast': {...},     # Tahmin
            'advice': {            # İlaçlama tavsiyesi
                'can_spray': True/False,
                'reason': '...'
            }
        }
    
    Kullanım:
        >>> weather = get_extended_weather("İzmir")
        >>> if weather['advice']['can_spray']:
        >>>     print("İlaçlama yapılabilir")
        >>> else:
        >>>     print(weather['advice']['reason'])
    """
    try:
        # 1. Anlık hava
        current = get_weather(city)
        
        # 2. 24 saatlik tahmin
        forecast = get_weather_forecast(city, hours=24)
        
        if not current or not forecast:
            return None
        
        # 3. İlaçlama tavsiyesi oluştur
        can_spray = True
        reasons = []
        
        # Şu an yağmur var mı?
        if current.get('will_rain'):
            can_spray = False
            reasons.append("Şu anda yağmur var")
        
        # Yakın zamanda yağmur olacak mı?
        if forecast.get('will_rain_soon'):
            can_spray = False
            reasons.append(f"Önümüzdeki 24 saatte yağmur bekleniyor (%{forecast['rain_probability']} olasılık)")
        
        # Sıcaklık çok yüksek mi? (kükürt yanığı riski)
        if current.get('temperature', 0) > 30:
            can_spray = False
            reasons.append("Sıcaklık 30°C üzerinde (kükürt kullanımı riskli)")
        
        # Önümüzdeki saatlerde çok sıcak olacak mı?
        if forecast.get('max_temp', 0) > 32:
            can_spray = False
            reasons.append(f"Önümüzdeki saatlerde sıcaklık {forecast['max_temp']:.1f}°C'ye çıkacak")
        
        advice = {
            'can_spray': can_spray,
            'reason': '; '.join(reasons) if reasons else 'Hava koşulları ilaçlama için uygun'
        }
        
        return {
            'current': current,
            'forecast': forecast,
            'advice': advice
        }
        
    except Exception as e:
        print(f" Extended weather hatası: {e}")
        return None


def format_forecast_summary(forecast: Dict) -> str:
    """
    Tahmin özetini insan okunabilir metne çevir
    
    Args:
        forecast: get_weather_forecast() sonucu
    
    Returns:
        str: "Önümüzdeki 24 saatte %60 olasılıkla yağmur bekleniyor..."
    """
    if not forecast:
        return "Hava tahmini alınamadı"
    
    summary = f"Önümüzdeki {forecast['forecast_hours']} saat için:\n"
    
    # Yağmur
    if forecast['will_rain_soon']:
        summary += f"• Yağmur bekleniyor (%{forecast['rain_probability']} olasılık)\n"
    else:
        summary += "• Yağmur beklenmiyor\n"
    
    # Sıcaklık
    summary += f"• Sıcaklık: {forecast['min_temp']:.1f}°C - {forecast['max_temp']:.1f}°C arası\n"
    
    # İlk yağmur ne zaman?
    if forecast['will_rain_soon']:
        for item in forecast['hourly_forecast']:
            if item['rain']:
                summary += f"• İlk yağmur: {item['time']}\n"
                break
    
    return summary
