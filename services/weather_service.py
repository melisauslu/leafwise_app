# services/weather_service.py

"""
Hava Durumu Servisi - OpenWeatherMap API
- Anlık hava durumu
- 5 günlük 3 saatlik tahmin
"""
import requests
import os
from typing import Optional, Dict

class WeatherService:
    def __init__(self):
        # API anahtarını çevresel değişkenden alıyoruz
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_full_analysis(self, city: str) -> Optional[Dict]:
        """
        Anlık hava durumu, tahmin ve ilaçlama tavsiyesini tek pakette toplar.
        """
        if not self.api_key:
            return {"error": "API anahtarı bulunamadı!"}

        try:
            # 1. Anlık Veriyi Çek
            current_url = f"{self.base_url}/weather"
            params = {'q': f"{city},TR", 'appid': self.api_key, 'units': 'metric', 'lang': 'tr'}
            res = requests.get(current_url, params=params, timeout=5)
            res.raise_for_status()
            data = res.json()

            # 2. Kritik Verileri Ayıkla
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed'] * 3.6  # m/s -> km/h dönüşümü
            description = data['weather'][0]['description']
            
            # Yağmur kontrolü (Hafif yağmur bile ilaçlamayı bozar)
            is_raining = 'rain' in data or 'snow' in data

            # 3. İlaçlama Tavsiyesi (Tarımsal Mantık)
            advice, reasons = self._generate_agronomic_advice(temp, humidity, wind_speed, is_raining)

            return {
                "city": city,
                "current": {
                    "temp": f"{temp}°C",
                    "humidity": f"%{humidity}",
                    "wind": f"{wind_speed:.1f} km/h",
                    "condition": description
                },
                "advice": {
                    "can_spray": advice,
                    "reason": reasons
                }
            }

        except Exception as e:
            return {"error": str(e)}



# Kullanım Örneği:
# weather = WeatherService()


