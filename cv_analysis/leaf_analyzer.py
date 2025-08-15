import cv2
import numpy as np
from PIL import Image
import os

class LeafAnalyzer:
    def __init__(self):
        self.colors = {
            'healthy': (34, 139, 34),    # Green
            'yellow': (255, 255, 0),     # Yellow
            'brown': (139, 69, 19),      # Brown
            'red': (255, 0, 0),          # Red
            'purple': (128, 0, 128)      # Purple
        }

    def analyze_leaf_color(self, image_path):
        """Analisis warna daun dengan OpenCV"""
        # Baca gambar
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Gambar tidak ditemukan"}
        
        # Konversi ke HSV untuk deteksi warna
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Threshold untuk warna hijau
        green_lower = np.array([35, 40, 40])
        green_upper = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        
        # Threshold untuk warna kuning
        yellow_lower = np.array([15, 40, 40])
        yellow_upper = np.array([35, 255, 255])
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        # Threshold untuk warna coklat
        brown_lower = np.array([0, 0, 0])
        brown_upper = np.array([180, 255, 100])
        brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
        
        # Hitung area
        green_area = cv2.countNonZero(green_mask)
        yellow_area = cv2.countNonZero(yellow_mask)
        brown_area = cv2.countNonZero(brown_mask)
        
        total_pixels = img.shape[0] * img.shape[1]
        
        # Analisis status
        if green_area > yellow_area and green_area > brown_area:
            return "Hijau Sehat"
        elif yellow_area > green_area and yellow_area > brown_area:
            return "Kuning (Stress Nutrisi)"
        elif brown_area > green_area and brown_area > yellow_area:
            return "Coklat (Kekurangan Air/Infeksi)"
        else:
            return "Warna Campuran (Perlu Perhatian)"

    def extract_leaf_features(self, image_path):
        """Ekstrak fitur daun untuk analisis lebih lanjut"""
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Gambar tidak ditemukan"}
        
        # Resize gambar
        resized = cv2.resize(img, (224, 224))
        
        # Normalisasi
        normalized = resized.astype(np.float32) / 255.0
        
        return {
            "shape": normalized.shape,
            "mean_intensity": np.mean(normalized),
            "std_intensity": np.std(normalized),
            "color_distribution": self.get_color_distribution(resized)
        }

    def get_color_distribution(self, img):
        """Hitung distribusi warna RGB"""
        hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
        
        return {
            "blue": hist_b.flatten().tolist(),
            "green": hist_g.flatten().tolist(),
            "red": hist_r.flatten().tolist()
        }