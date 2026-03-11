# services/retrieval_service.py

"""
Retrieval Service - RAG Retrieval Layer

Akış:
1. Vision model hastalık tespit eder: "Külleme"
2. Retrieval service bilgi tabanında arama yapar:
   - Filter: plant="Domates" AND disease="Külleme"
   - Vector similarity search
   - Top-k döküman döndür
3. Generation service bu dökümanları kullanarak tavsiye yazar
"""

import os
from typing import List, Dict, Optional

class RetrievalService:
    """
    RAG Retrieval Servisi
    
    Metadata filtering + Semantic search ile
    hastalık hakkında en alakalı dökümanları bulur
    """
    
    def __init__(self):
        """
        Retrieval service başlat
        
        RAG ekibi rag/ klasörünü tamamlayana kadar
        bu servis "mock mode" (simülasyon) çalışır
        """
        print(" Retrieval Service başlatılıyor...")
        
        # RAG hazır mı kontrol et
        try:
            # RAG ekibi bu modülleri yazacak
            from rag.embedding import embedding_service
            from rag.vector_store import get_vector_store
            
            self.embedding_service = embedding_service
            self.vector_store = get_vector_store()
            self.enabled = True
            
            print(f"    RAG aktif: {self.vector_store.count()} döküman")
            
        except ImportError as e:
            print(f"     RAG modülleri yok: {e}")
            print("    Mock mode (simülasyon)")
            
            self.embedding_service = None
            self.vector_store = None
            self.enabled = False
        
        print(" Retrieval Service hazır")
    
    def retrieve(
        self,
        disease: str,
        plant: str = "Domates",
        top_k: int = 5
    ) -> List[Dict]:
        """
        Hastalık bilgilerini RAG'den çek
        
        Args:
            disease: Hastalık adı (Vision'dan gelir)
                    Örn: "Külleme", "Erken Yanıklık"
            plant: Bitki türü
                   Örn: "Domates", "Biber", "Patlıcan"
            top_k: Kaç döküman döndürülsün (default: 5)
        
        Returns:
            List[Dict]: [
                {
                    'text': 'Kükürt bazlı fungisit 200-300g/100L...',
                    'source': 'T.C. Tarım Bakanlığı 2024',
                    'score': 0.91,
                    'metadata': {
                        'plant': 'Domates',
                        'disease': 'Külleme'
                    }
                },
                ...
            ]
        
        Akış:
        1. Query oluştur: "Domates Külleme tedavi"
        2. Query'yi embedding'e çevir (1024D vector)
        3. Vector DB'de ara (metadata filtering ile)
        4. En alakalı top-k dökümanı döndür
        """
        
        print(f"    Retrieval: {plant} - {disease}")
        
        # RAG aktif mi?
        if not self.enabled:
            print("     RAG yok, boş liste döndürülüyor")
            return self._mock_retrieve(disease, plant)
        
        # 1. QUERY OLUŞTUR
        # Arama sorgusu: bitki + hastalık + anahtar kelime
        query = f"{plant} {disease} tedavi önleme ilaç"
        
        # 2. QUERY EMBEDDİNG
        # Query'yi 1024 boyutlu vektöre çevir
        query_embedding = self.embedding_service.encode_query(query)
        
        # 3. VECTOR SEARCH (METADATA FİLTERİNG İLE)
        # Vector DB'de ara:
        # - plant_name = "Domates" filtresi
        # - disease_name = "Külleme" filtresi
        # - Cosine similarity > 0.7
        # - Top-k sonuç
        results = self.vector_store.search(
            query_embedding=query_embedding,
            plant_name=plant,
            disease_name=disease,
            top_k=top_k
        )
        
        # 4. SONUÇLARI FORMATLA
        if results:
            print(f"    {len(results)} döküman bulundu")
            
            # Debug: En yüksek skorları göster
            for i, result in enumerate(results[:3], 1):
                print(f"    {i}. Skor: {result['score']:.2f} - {result['source'][:50]}...")
        else:
            print("     Hiç döküman bulunamadı")
        
        # Formatlanmış sonuçlar
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result["chunk_text"],
                "source": result["source"],
                "score": result["score"],
                "metadata": {
                    "plant": result["plant_name"],
                    "disease": result["disease_name"]
                }
            })
        
        return formatted_results
    
    def _mock_retrieve(self, disease: str, plant: str) -> List[Dict]:
        """
        Mock mode: RAG yokken simülasyon data döndür
        
        RAG ekibi rag/ klasörünü tamamlayana kadar
        bu fonksiyon çalışır
        """
        
        # Simülasyon: Hastalığa göre mock data
        mock_data = {
            "Külleme": {
                "text": """
Külleme fungal bir hastalıktır. Yapraklarda beyaz pudra 
görünümü oluşturur. Tedavide kükürt bazlı fungisitler 
etkilidir. Önerilen doz: 200-300 g/100L su. 
Uygulama: 7-10 gün arayla 3-4 kez. 
DİKKAT: Sıcaklık 30°C üzerindeyken kükürt uygulamayın, 
yaprak yanığı riski vardır.
""",
                "source": "Mock Data - T.C. Tarım Bakanlığı"
            },
            "Erken Yanıklık": {
                "text": """
Erken yanıklık bacterial veya fungal kaynaklıdır. 
Yapraklarda kahverengi lekeler oluşur. Bakır oksiklorür 
veya bakır hidroksit etkilidir. Doz: 250-300 g/100L su. 
Yağmurdan 24 saat önce ilaçlama yapılmamalı.
""",
                "source": "Mock Data - Ege Üniversitesi"
            }
        }
        
        # Mock sonuç oluştur
        if disease in mock_data:
            return [{
                "text": mock_data[disease]["text"].strip(),
                "source": mock_data[disease]["source"],
                "score": 0.85,  # Mock score
                "metadata": {
                    "plant": plant,
                    "disease": disease
                }
            }]
        else:
            # Hastalık mock data'da yoksa boş
            return []
    
    def is_ready(self) -> bool:
        """
        RAG hazır mı?
        
        Returns:
            bool: True = RAG aktif, False = Mock mode
        """
        if not self.enabled:
            return False
        
        try:
            count = self.vector_store.count()
            return count > 0
        except:
            return False
    
    def get_stats(self) -> Dict:
        """
        Retrieval istatistikleri
        
        Returns:
            dict: {
                'status': 'active' / 'mock',
                'total_docs': 1500,
                'embedding_dim': 1024,
                'model': 'multilingual-e5-large'
            }
        """
        if not self.enabled:
            return {
                "status": "mock",
                "message": "RAG ekibi henüz rag/ klasörünü tamamlamadı"
            }
        
        try:
            return {
                "status": "active",
                "total_docs": self.vector_store.count(),
                "embedding_dim": self.embedding_service.get_dimension(),
                "model": "multilingual-e5-large"
            }
        except:
            return {
                "status": "error",
                "message": "RAG servisi hata veriyor"
            }

# Singleton
retrieval_service = RetrievalService()
