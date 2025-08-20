# setup_models.py
import os
import sys

def setup_model_files():
    """
    Setup file model secara otomatis saat aplikasi dijalankan
    """
    # Pastikan folder models ada
    models_dir = 'models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print("📁 Folder models dibuat")
    
    # Cek dan buat file model jika tidak ada
    model_files = [
        'models/leaf_disease_model.h5',
        'models/yield_model.pkl'
    ]
    
    for file_path in model_files:
        if not os.path.exists(file_path):
            print(f"⚠️ File tidak ditemukan: {file_path}")
            # Buat file kosong sebagai placeholder
            try:
                with open(file_path, 'w') as f:
                    f.write("placeholder_file_for_model")
                print(f"✅ File dummy dibuat: {file_path}")
            except Exception as e:
                print(f"❌ Gagal membuat file {file_path}: {e}")
        else:
            print(f"✅ File ditemukan: {file_path}")

if __name__ == "__main__":
    setup_model_files()