# services/rag_service.py

"""
RAG Servisi - EKİP TARAFINDAN DOLDURULACAK

Şu an: Placeholder (boş şablon)
Ekip implement edince: ChromaDB + Embedding çalışacak
"""

class RAGService:
    """
    Retrieval Augmented Generation servisi
    
    NOTLAR:
    - Ekip bu dosyayı implement edecek
    - Interface değişmeyecek (retrieve metodu aynı kalacak)
    - Backend kodu değişmeden RAG entegre olacak
    """
    
    def __init__(self):
        """
        RAG servisini başlat
        
        TODO (EKİP): 
        - ChromaDB bağlantısı
        - Gemini Embedding API
        - Collection kontrolü
        """
        self.enabled = False
        print("⚠️  RAG servisi henüz aktif değil")
        print("   Ekip implement edince otomatik çalışacak")
    
    def retrieve(
        self, 
        disease: str, 
        city: str = None, 
        n_results: int = 5
    ) -> list:
        """
        Hastalık bilgilerini RAG'den çek
        
        Args:
            disease: Hastalık adı (örn: "Külleme")
            city: Şehir adı (opsiyonel, bölgesel filtreleme için)
            n_results: Kaç döküman döndürülsün (default: 5)
        
        Returns:
            list: Döküman listesi (string)
            
        TODO (EKİP):
            1. Query oluştur: f"{disease} hastalığı tedavi"
            2. Embedding oluştur (Gemini)
            3. ChromaDB'den sorgula
            4. Sonuçları döndür
            
        Örnek Implementation:
```
            query = f"{disease} hastalığı"
            embedding = genai.embed_content(query)
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results
            )
            return results['documents'][0]
```
        """
        if not self.enabled:
            # RAG henüz hazır değil, boş liste döndür
            return []
        
        # TODO: Ekip burayı implement edecek
        return []
    
    def is_ready(self) -> bool:
        """
        RAG hazır mı kontrol et
        
        Returns:
            bool: RAG kullanılabilir mi?
        """
        return self.enabled

# Singleton instance
rag_service = RAGService()
