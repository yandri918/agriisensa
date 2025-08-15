from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os
from datetime import datetime
import cv2
import numpy as np

# Import CV modules
from cv_analysis.leaf_analyzer import LeafAnalyzer
from cv_analysis.disease_classifier import DiseaseClassifier

app = Flask(__name__)

# Load model ML
model_path = os.path.join('models', 'yield_model.pkl')
predictor = None

try:
    if os.path.exists(model_path):
        predictor = joblib.load(model_path)
        print("✅ Model berhasil dimuat")
    else:
        print("⚠️ File model tidak ditemukan")
except Exception as e:
    print(f"❌ Error memuat model: {e}")
    predictor = None

# Inisialisasi CV analyzer
leaf_analyzer = LeafAnalyzer()
disease_classifier = DiseaseClassifier()

# Database handler
class HistoricalDataManager:
    def __init__(self, db_path='data/historical.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal DATE,
                    pH REAL,
                    N_mg_kg INTEGER,
                    P_mg_kg INTEGER,
                    K_persen REAL,
                    hasil_kg REAL,
                    cuaca TEXT,
                    musim TEXT,
                    jenis_tanaman TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error membuat database: {e}")
    
    def save_prediction(self, data_dict):
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO historical_data 
                (tanggal, pH, N_mg_kg, P_mg_kg, K_persen, hasil_kg, cuaca, musim, jenis_tanaman)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data_dict.get('tanggal'),
                data_dict.get('pH'),
                data_dict.get('N_mg_kg'),
                data_dict.get('P_mg_kg'),
                data_dict.get('K_persen'),
                data_dict.get('hasil_kg'),
                data_dict.get('cuaca'),
                data_dict.get('musim'),
                data_dict.get('jenis_tanaman')
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error menyimpan data historis: {e}")

# Inisialisasi database
db_manager = HistoricalDataManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Ambil input dari form
        pH = float(request.form.get('ph', 0))
        n = float(request.form.get('n', 0))
        p = float(request.form.get('p', 0))
        k = float(request.form.get('k', 0))
        cuaca = request.form.get('cuaca', 'hujan')
        musim = request.form.get('musim', 'kemarau')
        jenis_tanaman = request.form.get('jenis_tanaman', 'cabai')
        
        # Upload gambar jika ada
        leaf_analysis = {}
        disease_result = {}
        
        if 'leaf_image' in request.files:
            file = request.files['leaf_image']
            if file and file.filename:
                # Simpan gambar
                upload_folder = 'uploads'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # Analisis warna daun
                leaf_status = leaf_analyzer.analyze_leaf_color(file_path)
                leaf_analysis = {
                    "color_analysis": leaf_status,
                    "image_path": filename
                }
                
                # Prediksi penyakit
                disease_result = disease_classifier.predict_disease(file_path)
        
        # Prediksi hasil panen
        hasil = 0
        model_used = "Fallback (Sederhana)"
        
        if predictor:
            try:
                # Encode cuaca dan musim
                cuaca_map = {'hujan': 0, 'kemarau': 1}
                musim_map = {'kemarau': 0, 'hujan': 1}
                
                cuaca_encoded = cuaca_map.get(cuaca, 0)
                musim_encoded = musim_map.get(musim, 0)
                
                # Prediksi
                prediction = predictor.predict([[pH, n, p, k, cuaca_encoded, musim_encoded]])
                hasil = prediction[0]
                model_used = "Machine Learning (ML)"
            except Exception as e:
                print(f"❌ Error prediksi ML: {e}")
                hasil = 3.8 if pH < 5.5 else 4.8
        else:
            hasil = 3.8 if pH < 5.5 else 4.8
        
        # Rekomendasi
        rekomendasi = []
        if pH < 5.5:
            rekomendasi.append("Tambahkan dolomit")
        if n < 25:
            rekomendasi.append("Butuh MOL untuk nitrogen")
        if p < 15:
            rekomendasi.append("Pupuk fosfat atau kompos tinggi P")
        if k < 0.30:
            rekomendasi.append("Butuh pupuk kalium")

        status = "🔴 Kritis" if pH < 5.5 or n < 20 or p < 10 else "🟡 Sedang" if pH < 5.8 else "🟢 Sehat"

        # Simpan data historis
        try:
            historical_data = {
                'tanggal': datetime.now().strftime('%Y-%m-%d'),
                'pH': pH,
                'N_mg_kg': n,
                'P_mg_kg': p,
                'K_persen': k,
                'hasil_kg': hasil,
                'cuaca': cuaca,
                'musim': musim,
                'jenis_tanaman': jenis_tanaman
            }
            db_manager.save_prediction(historical_data)
        except Exception as e:
            print(f"❌ Error menyimpan historis: {e}")

        return render_template('result.html',
                               ph=pH, n=n, p=p, k=k,
                               hasil=round(hasil, 2),
                               status=status,
                               rekomendasi=rekomendasi,
                               cuaca=cuaca,
                               musim=musim,
                               jenis_tanaman=jenis_tanaman,
                               model_used=model_used,
                               tanggal=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                               leaf_analysis=leaf_analysis,
                               disease_result=disease_result)
    except Exception as e:
        return f"<h3>Error: {str(e)}</h3><br><a href='/'>Kembali</a>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
