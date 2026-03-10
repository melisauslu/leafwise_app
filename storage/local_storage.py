# storage/local_storage.py
import os

class LocalStorage:
    def __init__(self):
        self.dir = "uploads"  # Fotoğraflar buraya kaydedilecek
        os.makedirs(self.dir, exist_ok=True)

    def save_photo(self, image_data: bytes, filename: str, metadata: dict = None) -> str:
        """
        Fotoğrafı localde kaydeder.
        metadata şimdilik kullanılmıyor, ileride DB'ye eklenebilir.
        """
        path = os.path.join(self.dir, filename)
        with open(path, "wb") as f:
            f.write(image_data)
        print(f"[LocalStorage] Kaydedildi: {path}")
        return path
