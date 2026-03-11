# storage/__init__.py
from .local_storage import LocalStorage
from .cloud_storage import CloudStorage

# --------------------------------------------------
# STORAGE TİPİNİ SEÇ (False = Local, True = Cloud)
# --------------------------------------------------
USE_CLOUD = False  # True yaparsan cloud storage kullanılır

storage = CloudStorage() if USE_CLOUD else LocalStorage()
