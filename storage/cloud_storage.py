# storage/cloud_storage.py

class CloudStorage:
    def __init__(self):
        # Buraya cloud bağlantı ayarları eklenebilir
        pass

    def save_photo(self, image_data: bytes, filename: str, metadata: dict = None) -> str:
        """
        Fotoğrafı buluta kaydeder.
        Şimdilik demo olduğu için sadece isim döndürülüyor.
        """
        cloud_path = f"cloud://{filename}"
        print(f"[CloudStorage] Kaydedildi: {cloud_path}")
        return cloud_path
