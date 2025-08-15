import os
import sys
import io

# Set encoding untuk menghindari error Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from datetime import datetime

# Import CV modules
try:
    from cv_analysis.leaf_analyzer import LeafAnalyzer
    from cv_analysis.disease_classifier import DiseaseClassifier
    CV_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] CV modules not available: {e}")
    CV_MODULES_AVAILABLE = False

app = Flask(__name__)

# Load model ML
model_path = os.path.join('models', 'yield_model.pkl')
predictor = None

try:
    if os.path.exists(model_path):
        predictor = joblib.load(model_path)
        print("[SUCCESS] Model berhasil dimuat")
    else:
        print("[WARNING] File model tidak ditemukan")
except Exception as e:
    print(f"[ERROR] Error memuat model: {e}")
    predictor = None

# Inisialisasi CV analyzer jika tersedia
leaf_analyzer = None
disease_classifier = None

if CV_MODULES_AVAILABLE:
    try:
        leaf_analyzer = LeafAnalyzer()
        disease_classifier = DiseaseClassifier()
        print("[SUCCESS] CV modules berhasil dimuat")
    except Exception as e:
        print(f"[ERROR] Error memuat CV modules: {e}")
        CV_MODULES_AVAILABLE = False

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
            print(f"[ERROR] Error membuat database: {e}")
    
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
            print(f"[ERROR] Error menyimpan data historis: {e}")

# Inisialisasi database
db_manager = HistoricalDataManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate-area')
def calculate_area():
    return render_template('area_calculator.html')

@app.route('/map-calculator')
def map_calculator():
    return render_template('map_calculator.html')

@app.route('/calculate-area-result', methods=['POST'])
def calculate_area_result():
    try:
        # Ambil data dari form
        coordinates = request.form.get('coordinates', '')
        latitudes_str = request.form.get('latitudes', '')
        longitudes_str = request.form.get('longitudes', '')
        
        # Proses koordinat
        if coordinates:
            # Parse koordinat dari string
            coords = []
            pairs = coordinates.split(';')
            for pair in pairs:
                if ',' in pair:
                    lat, lon = pair.split(',')
                    coords.append((float(lat.strip()), float(lon.strip())))
            
            if len(coords) >= 3:
                # Hitung luas
                from area_calculator import AreaCalculator
                area = AreaCalculator.calculate_polygon_area(coords)
                area_hectare = round(area, 2)
            else:
                area_hectare = 0
                
        elif latitudes_str and longitudes_str:
            # Parse latitudes dan longitudes
            latitudes = [float(x.strip()) for x in latitudes_str.split(',')]
            longitudes = [float(x.strip()) for x in longitudes_str.split(',')]
            
            if len(latitudes) >= 3 and len(longitudes) >= 3:
                from area_calculator import AreaCalculator
                area_hectare = AreaCalculator.calculate_approximate_area(latitudes, longitudes)
            else:
                area_hectare = 0
        else:
            area_hectare = 0
        
        # Perhitungan biaya produksi (contoh data)
        cost_total = 15000000  # Rp 15 juta
        estimated_yield = 45000  # 45 ton
        roi = 150  # 150% ROI
        
        # Hitung biaya per hektar
        cost_per_hectare = AreaCalculator.calculate_cost_per_area(cost_total, area_hectare)
        
        # Hitung hasil panen per hektar
        yield_per_hectare = AreaCalculator.estimate_yield_per_area(estimated_yield, area_hectare)
        
        return render_template('area_result.html',
                               area=area_hectare,
                               cost_total=cost_total,
                               cost_per_hectare=cost_per_hectare,
                               estimated_yield=estimated_yield,
                               yield_per_hectare=yield_per_hectare,
                               roi=roi)
        
    except Exception as e:
        return f"<h3>Error: {str(e)}</h3><br><a href='/calculate-area'>Kembali</a>"

@app.route('/process-map-coordinates', methods=['POST'])
def process_map_coordinates():
    try:
        coordinates_str = request.form.get('coordinates', '')
        
        if coordinates_str:
            # Parse koordinat dari string
            coords = []
            pairs = coordinates_str.split(';')
            for pair in pairs:
                if ',' in pair:
                    lat, lon = pair.split(',')
                    coords.append((float(lat.strip()), float(lon.strip())))
            
            if len(coords) >= 3:
                # Hitung luas menggunakan fungsi yang sudah ada
                from area_calculator import AreaCalculator
                area = AreaCalculator.calculate_polygon_area(coords)
                area_hectare = round(area, 2)
                
                # Simpan ke database atau kirim ke frontend
                return f"Koordinat diterima. Luas: {area_hectare} hektar"
            else:
                return "Koordinat tidak cukup untuk menghitung luas"
        else:
            return "Tidak ada koordinat yang diterima"
            
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Ambil input dari form
        pH = float(request.form.get('ph', 0))
        n = float(request.form.get('n', 0))
        p = float(request.form.get('p', 0))
        k = float(request.form.get('k', 0))
        cuaca = request.form.get('cuaca', 'huj
