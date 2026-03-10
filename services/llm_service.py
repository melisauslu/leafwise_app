# services/llm_service.py

"""
LLM Servisi - Gemini ile tavsiye oluşturma
Extended Weather (current + forecast + spray_advice) kullanıyor!
"""

import google.generativeai as genai
import os
from typing import Dict, Optional
from services.rag import rag_service

def generate_advice(
    disease: str,
    confidence: float,
    city: str,
    weather: Optional[Dict],
    plant: str
) -> str:
    """
    LLM ile tavsiye oluştur
    
    Args:
        disease: Hastalık adı
        confidence: Model güveni (%)
        city: Şehir
        weather: Extended weather (current + forecast + spray_advice)
        plant: Bitki türü
    
    Returns:
        str: Tavsiye metni
    
    NOT: weather parametresi artık extended_weather formatında gelir:
    {
        'current': {...},
        'forecast': {...},
        'advice': {...}
    }
    """
    
    # 1. RAG'DEN BİLGİ ÇEK
    print("    RAG sorgulanıyor...")
    rag_docs = rag_service.retrieve(disease, city)
    
    if rag_docs:
        print(f"    RAG'den {len(rag_docs)} döküman bulundu")
    else:
        if rag_service.is_ready():
            print("     RAG'de bu hastalık için bilgi bulunamadı")
        else:
            print("     RAG henüz aktif değil")
        print("    Gemini genel bilgi ile devam ediyor")
    
    # 2. GEMİNİ API KEY KONTROL
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("     GEMINI_API_KEY bulunamadı")
        print("    Statik tavsiye dönülüyor")
        return _generate_static_advice(disease, weather)
    
    # 3. GEMİNİ MODEL
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f" Gemini bağlantı hatası: {e}")
        return _generate_static_advice(disease, weather)
    
    # 4. PROMPT OLUŞTUR (Extended Weather ile)
    prompt = _build_prompt(disease, confidence, city, weather, plant, rag_docs)
    
    # 5. LLM ÇALIŞTIR
    try:
        print("    Gemini LLM çalışıyor...")
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"    LLM hatası: {e}")
        return _generate_static_advice(disease, weather)


def _build_prompt(
    disease: str,
    confidence: float,
    city: str,
    weather: Optional[Dict],
    plant: str,
    rag_docs: list
) -> str:
    """
    LLM için prompt oluştur (Extended Weather ile)
    """
    
    # TEMEL BİLGİLER
    prompt = f"""
Sen bir tarım danışmanısın. Çiftçiye kısa ve öz tavsiye ver.

TESPİT BİLGİLERİ:
- Hastalık: {disease}
- Güvenilirlik: %{confidence:.0f}
- Bitki: {plant}
- Konum: {city}
"""
    
    # HAVA DURUMU (EXTENDED FORMAT)
    if weather and 'current' in weather:
        # Extended weather formatı
        current = weather['current']
        forecast = weather['forecast']
        spray = weather['advice']
        
        prompt += f"""

HAVA DURUMU ANALİZİ:

ŞU AN (ANLIK):
- Sıcaklık: {current['temperature']}°C
- Nem: %{current['humidity']}
- Durum: {current['description']}
- Yağmur: {'Var' if current.get('will_rain') else 'Yok'}

ÖNÜMÜZDEKİ 24 SAAT (TAHMİN):
- Sıcaklık Aralığı: {forecast['min_temp']:.1f}°C - {forecast['max_temp']:.1f}°C
- Ortalama Sıcaklık: {forecast['avg_temp']:.1f}°C
- Yağmur Olasılığı: %{forecast['rain_probability']}
- Yağmur Durumu: {'Yağmur bekleniyor' if forecast['will_rain_soon'] else 'Yağmur beklenmiyor'}

İLAÇLAMA DEĞERLENDİRMESİ:
{spray['reason']}
İlaçlama Uygun mu?: {'EVET' if spray['can_spray'] else 'HAYIR'}
"""
    elif weather:
        # Eski current-only format (geriye uyumlu)
        prompt += f"""

HAVA DURUMU:
- Sıcaklık: {weather.get('temperature', 'Bilinmiyor')}°C
- Nem: %{weather.get('humidity', 'Bilinmiyor')}
- Yağmur: {'Var' if weather.get('will_rain') else 'Yok'}
"""
    else:
        prompt += "\n\nHAVA DURUMU: Bilgi alınamadı\n"
    
    # RAG BİLGİSİNİ EKLE (VARSA)
    if rag_docs:
        prompt += f"""

BİLGİ TABANI (TARIM VERİTABANI):
ÖNEMLİ: Aşağıdaki bilgiler tarım uzmanlarından onaylanmış bilgilerdir.
Tavsiyelerini bu bilgilere göre ver. Doz, süre gibi detayları buradan al.

{_format_rag_docs(rag_docs)}

UYARI: Bilgi tabanında olmayan bilgi verme!
"""
    else:
        prompt += """

NOT: Bilgi tabanı mevcut değil. Genel tarım bilgine göre tavsiye ver.
"""
    
    # KURALLAR
    prompt += """

TAVSİYE KURALLARI:
1. KESİN DİL KULLANMA:
    "Kesinlikle yapın", "Mutlaka uygulayın"
    "Önerilir", "Yapılabilir", "Düşünülebilir"

2. HAVA DURUMU TAHMİNİNİ DİKKATE AL:
   - Önümüzdeki saatlerde yağmur gelecekse → İlaçlama YAPMAYIN
   - Yağmur durduktan 24-48 saat sonra → İlaçlama yapılabilir
   - Sıcaklık >30°C olacaksa → Kükürt KULLANMAYIN (yanık riski)
   - Yüksek nem → Hastalık yayılma riski var

3. İLAÇLAMA DEĞERLENDİRMESİNİ KULLAN:
   - "İlaçlama Uygun mu?: HAYIR" ise → Neden uygun olmadığını açıkla
   - "İlaçlama Uygun mu?: EVET" ise → Ne zaman yapabileceğini söyle

4. KISA VE ÖZ:
   - 5-7 cümle yeterli
   - Gereksiz detaya girme
   - Çiftçiye net bilgi ver

5. BİLGİ TABANI ÖNCELİKLİ:
   - Bilgi tabanında doz varsa onu kullan
   - Uydurma, tahmin etme

ÖNEMLİ: Hava tahminine göre akıllı karar ver!

TAVSİYE METNİ (5-7 cümle):
"""
    
    return prompt


def _format_rag_docs(rag_docs: list) -> str:
    """
    RAG dökümanlarını prompt için formatla
    """
    formatted = []
    
    for i, doc in enumerate(rag_docs[:3], 1):  # Max 3 döküman
        # Her dökümanı kısalt (LLM token limiti için)
        truncated = doc[:500] if len(doc) > 500 else doc
        formatted.append(f"Kaynak {i}:\n{truncated}\n")
    
    return "\n".join(formatted)


def _generate_static_advice(disease: str, weather: Optional[Dict]) -> str:
    """
    Fallback: Minimal hata mesajı
    """
    return f"""
{disease} hastalığı tespit edildi.

⚠️ Şu anda detaylı tavsiye oluşturulamıyor.

Lütfen:
1. İnternet bağlantınızı kontrol edin
2. Tekrar deneyin
3. Sorun devam ederse ziraat mühendisine danışın

Genel Uyarı: Hava durumunu kontrol edin, yağmur varsa ilaçlama yapmayın.
"""
