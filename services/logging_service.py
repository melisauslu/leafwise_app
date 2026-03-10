# services/logging_service.py

import logging
import json
from datetime import datetime
from pathlib import Path

class BackendLogger:
    """Backend için logging servisi"""
    
    def __init__(self):
        # logs/ klasörü oluştur
        Path("logs").mkdir(exist_ok=True)
        
        # Log dosyası (her gün yeni dosya)
        log_file = f"logs/backend_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Logger ayarla
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        
        self.logger = logging.getLogger('TarimBackend')
        
        print(f" Logging aktif: {log_file}")
    
    def log_request(self, endpoint: str, data: dict):
        """API isteği logla"""
        log_data = {
            "type": "REQUEST",
            "endpoint": endpoint,
            "data": data
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_response(self, endpoint: str, status: int, duration: float):
        """API yanıtı logla"""
        log_data = {
            "type": "RESPONSE",
            "endpoint": endpoint,
            "status": status,
            "duration": round(duration, 2)
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_analysis(self, data: dict):
        """Analiz detaylarını logla"""
        log_data = {
            "type": "ANALYSIS",
            **data
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_error(self, error: str, details: dict = None):
        """Hata logla"""
        log_data = {
            "type": "ERROR",
            "error": error,
            "details": details or {}
        }
        self.logger.error(json.dumps(log_data, ensure_ascii=False))

# Singleton instance
logger = BackendLogger()
