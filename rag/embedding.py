# rag/embedding.py

"""
Embedding Servisi - multilingual-e5-large
Dimension: 1024
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

class EmbeddingService:
    """
    E5-Large Multilingual Embedding
    Türkçe optimizasyonu ile
    """
    
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        """
        Args:
            model_name: Embedding model adı
        """
        print(f"📦 Embedding model yükleniyor: {model_name}")
        
        self.model = SentenceTransformer(model_name)
        self.dimension = 1024  # E5-large dimension
        
        print(f"✅ Embedding hazır: {self.dimension}D")
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Query için embedding oluştur
        
        Args:
            query: Sorgu metni (örn: "domates külleme")
        
        Returns:
            np.ndarray: 1024 boyutlu embedding
        
        NOT: E5 modelleri için query prefix gerekli
        """
        # E5 için özel prefix
        prefixed_query = f"query: {query}"
        
        embedding = self.model.encode(prefixed_query, normalize_embeddings=True)
        return embedding
    
    def encode_document(self, text: str) -> np.ndarray:
        """
        Döküman için embedding oluştur
        
        Args:
            text: Döküman metni
        
        Returns:
            np.ndarray: 1024 boyutlu embedding
        
        NOT: E5 modelleri için passage prefix gerekli
        """
        # E5 için özel prefix
        prefixed_text = f"passage: {text}"
        
        embedding = self.model.encode(prefixed_text, normalize_embeddings=True)
        return embedding
    
    def encode_batch(self, texts: List[str], is_query: bool = False) -> np.ndarray:
        """
        Toplu embedding oluştur
        
        Args:
            texts: Metin listesi
            is_query: Query mu döküman mı?
        
        Returns:
            np.ndarray: (N, 1024) boyutlu embeddings
        """
        prefix = "query: " if is_query else "passage: "
        prefixed_texts = [f"{prefix}{text}" for text in texts]
        
        embeddings = self.model.encode(prefixed_texts, normalize_embeddings=True)
        return embeddings
    
    def get_dimension(self) -> int:
        """Embedding boyutunu döndür"""
        return self.dimension

# Singleton
embedding_service = EmbeddingService()
