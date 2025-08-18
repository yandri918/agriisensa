import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import os

class DiseaseClassifier:
    def __init__(self, model_path='models/leaf_disease_model.h5'):
        self.model_path = model_path
        self.model = None
        self.class_names = ['Healthy', 'Bacterial Blight', 'Leaf Spot', 'Powdery Mildew', 'Root Rot']
        self.load_model()

    def load_model(self):
        """Muat model pre-trained"""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print("[SUCCESS] Model penyakit daun berhasil dimuat")
            else:
                print("[WARNING] File model tidak ditemukan")
                # Buat model dummy jika tidak ada
                self.create_dummy_model()
        except Exception as e:
            print(f"[ERROR] Error memuat model: {e}")
            self.create_dummy_model()

    def create_dummy_model(self):
        """Buat model dummy untuk testing"""
        print("🔧 Membuat model dummy...")
        
        # Load base model
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        base_model.trainable = False
        
        # Tambahkan layer kustom
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        predictions = Dense(5, activation='softmax')(x)
        
        self.model = Model(inputs=base_model.input, outputs=predictions)
        
        # Simpan model dummy
        self.model.save(self.model_path)
        print("[INFO] Model dummy penyakit daun disimpan")

    def predict_disease(self, image_path):
        """Prediksi penyakit daun"""
        if self.model is None:
            return {"error": "Model tidak tersedia"}
        
        try:
            # Load dan preprocess gambar
            img = image.load_img(image_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0
            
            # Prediksi
            predictions = self.model.predict(img_array)
            predicted_class = np.argmax(predictions[0])
            confidence = predictions[0][predicted_class]
            
            return {
                "disease": self.class_names[predicted_class],
                "confidence": float(confidence),
                "all_probabilities": dict(zip(self.class_names, predictions[0].tolist()))
            }
        except Exception as e:
            return {"error": f"Error prediksi: {str(e)}"}

    def get_disease_info(self, disease_name):
        """Dapatkan informasi penyakit"""
        disease_info = {
            "Healthy": "Daun sehat tanpa tanda penyakit",
            "Bacterial Blight": "Infeksi bakteri menyebabkan bercak hitam pada daun",
            "Leaf Spot": "Bercak coklat atau hitam pada daun",
            "Powdery Mildew": "Lapisan putih halus di permukaan daun",
            "Root Rot": "Akar membusuk, daun layu dan kuning"
        }
        return disease_info.get(disease_name, "Informasi tidak tersedia")
