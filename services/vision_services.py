# services/vision_service.py

"""
Vision Service - MobileNet Fine-tuned
Hastalık sınıflandırma
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import io
from typing import Dict, Tuple

class VisionService:
    """
    MobileNet tabanlı hastalık sınıflandırma
    
    TODO: Gerçek fine-tuned model yüklenecek
    """
    
    def __init__(self, model_path: str = None):
        """
        Model yükle
        
        Args:
            model_path: Fine-tuned model dosyası (.h5 veya SavedModel)
        """
        print(" Vision Service başlatılıyor...")
        
        # TODO: Gerçek model yükleme
        # self.model = tf.keras.models.load_model(model_path)
        
        # Şimdilik simülasyon
        self.model = None
        self.class_names = [
            "Tomato___Bacterial_spot",                        # 0
            "Tomato___Early_blight",                          # 1
            "Tomato___healthy",                               # 2  <- Sağlıklı olan artık burada!
            "Tomato___Late_blight",                           # 3
            "Tomato___Leaf_Mold",                             # 4
            "Tomato___Septoria_leaf_spot",                    # 5
            "Tomato___Spider_mites Two-spotted_spider_mite",  # 6
            "Tomato___Target_Spot",                           # 7
            "Tomato___Tomato_mosaic_virus",                   # 8
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus"          # 9
        ]

        print(" Vision Service hazır")
    
    def predict(self, image_bytes: bytes) -> Dict:
        """
        Hastalık tahmini yap
        
        Args:
            image_bytes: Fotoğraf bytes
        
        Returns:
            dict: {
                'disease': 'Külleme',
                'confidence': 0.85,
                'all_predictions': [...]
            }
        """
        # Görüntü ön işleme
        image = Image.open(io.BytesIO(image_bytes))
        image = image.resize((224, 224))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        # TODO: Gerçek model inference
        # predictions = self.model.predict(image_array)[0]
        
        # Simülasyon
        predictions = np.random.rand(len(self.class_names))
        predictions = predictions / predictions.sum()  # Normalize
        
        # En yüksek skorlu sınıf
        top_idx = np.argmax(predictions)
        disease = self.class_names[top_idx]
        confidence = float(predictions[top_idx])
        
        # Tüm tahminler
        all_predictions = [
            {"disease": name, "confidence": float(score)}
            for name, score in zip(self.class_names, predictions)
        ]
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            "disease": disease,
            "confidence": confidence,
            "all_predictions": all_predictions[:3]  # Top-3
        }

# Singleton

vision_service = VisionService()

