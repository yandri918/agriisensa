# create_dummy_model.py
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import numpy as np
import os

def create_dummy_model():
    """
    Membuat model dummy yang kompatibel untuk deployment di Render
    """
    try:
        print("🔧 Membuat model dummy untuk deteksi penyakit daun...")
        
        # Load base model dengan parameter yang kompatibel
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Freeze base model
        base_model.trainable = False
        
        # Tambahkan layer kustom
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        predictions = Dense(5, activation='softmax')(x)  # 5 kelas penyakit
        
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Simpan model
        model.save('models/leaf_disease_model.h5')
        print("✅ Model dummy deteksi penyakit daun berhasil dibuat")
        print("📁 File disimpan di: models/leaf_disease_model.h5")
        
        # Buat juga file dummy untuk yield model
        # Karena file ini akan diakses oleh sistem, kita buat file kosong
        with open('models/yield_model.pkl', 'w') as f:
            f.write("dummy_model_file")
        print("✅ File dummy yield_model.pkl berhasil dibuat")
        
        return model
        
    except Exception as e:
        print(f"❌ Error membuat model: {e}")
        # Buat file kosong sebagai fallback
        try:
            with open('models/leaf_disease_model.h5', 'w') as f:
                f.write("")
            with open('models/yield_model.pkl', 'w') as f:
                f.write("")
            print("⚠️ File dummy dibuat sebagai fallback")
        except Exception as e2:
            print(f"❌ Gagal membuat file dummy: {e2}")
        return None

if __name__ == "__main__":
    # Buat model dummy saat deploy
    model = create_dummy_model()
    if model:
        print("🔧 Model siap digunakan untuk deteksi penyakit daun")
    else:
        print("❌ Gagal membuat model")
