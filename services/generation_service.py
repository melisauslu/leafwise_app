# services/generation_service.py

"""
Generation Service - LLM Generation Layer
Source-grounded answer generation
"""

import google.generativeai as genai
import os
from typing import List, Dict, Optional

class GenerationService:
    """
    LLM Generation Layer
    
    RAG retrieval sonuçlarını kullanarak
    kaynak-temelli tavsiye oluşturur
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.model = None
            self.enabled = False
    
    def generate(
        self,
        disease: str,
        confidence: float,
        plant: str,
        city: str,
        weather: Optional[Dict],
        rag_results: List[Dict]
    ) -> str:
        """
        Kaynak-temelli tavsiye oluştur
        
        Args:
            disease: Hastalık
            confidence: Vision model güveni
            plant: Bitki
            city: Konum
            weather: Hava durumu (extended)
            rag_results: RAG retrieval sonuçları
        
        Returns:
            str: Source-grounded advice
        """
        if not self.enabled:
            return self._fallback_advice(disease, rag_results)
        
        # Prompt oluştur
        prompt = self._build_prompt(
            disease, confidence, plant, city, weather, rag_results
        )
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"    Generation hatası: {e}")
            return self._fallback_advice(disease, rag_results)
    
    def _build_prompt(
        self,
        disease: str,
        confidence: float,
        plant: str,
        city: str,
        weather: Optional[Dict],
        rag_results: List[Dict]
    ) -> str:
        """LLM prompt oluştur"""
        
        prompt = f"""
Sen bir tarım uzmanısın. Çiftçiye kaynak-temelli tavsiye ver.

TESPİT:
- Bitki: {plant}
- Hastalık: {disease}
- Güven: %{confidence:.0f}
- Konum: {city}
"""
        
        # Hava durumu
        if weather and 'current' in weather:
            current = weather['current']
            forecast = weather['forecast']
            spray = weather['advice']
            
            prompt += f"""

HAVA DURUMU:
ŞU AN: {current['temperature']}°C, {current['description']}
24 SAAT: {forecast['min_temp']:.1f}°C - {forecast['max_temp']:.1f}°C
YAĞMUR: %{forecast['rain_probability']} olasılık
İLAÇLAMA: {spray['reason']}
"""
        
        # RAG kaynakları
        if rag_results:
            prompt += "\n\nBİLGİ KAYNAKLARI (TARIM VERİ TABANI):\n"
            for i, result in enumerate(rag_results[:3], 1):
                prompt += f"\nKaynak {i} (Skor: {result['score']:.2f}):\n"
                prompt += f"{result['text'][:500]}...\n"
            
            prompt += "\nÖNEMLİ: Sadece yukarıdaki kaynaklara dayanarak tavsiye ver!"
        
        # Kurallar
        prompt += """

KURALLAR:
1. Kaynaklara sadık kal, uydurma
2. Hava durumunu dikkate al
3. Step-by-step tavsiye ver
4. 5-7 cümle, kısa ve öz
5. "Kaynak X'e göre..." diyerek cite et

TAVSİYE:
"""
        
        return prompt
    
    def _fallback_advice(self, disease: str, rag_results: List[Dict]) -> str:
        """API yoksa basit tavsiye"""
        
        advice = f" {disease} tespit edildi.\n\n"
        
        if rag_results:
            advice += "Bilgi Kaynağı:\n"
            advice += f"{rag_results[0]['text'][:300]}...\n\n"
        
        advice += "Detaylı tavsiye için internet bağlantınızı kontrol edin."
        
        return advice

# Singleton
generation_service = GenerationService()
