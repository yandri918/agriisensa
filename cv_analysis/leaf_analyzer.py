import cv2
import numpy as np
from PIL import Image
import os

class LeafAnalyzer:
    def __init__(self):
        pass
    
    def analyze_leaf_color(self, image_path):
        """
        Analisis warna daun menggunakan OpenCV
        """
        try:
            # Baca gambar
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Gagal membaca gambar"}
            
            # Konversi ke RGB (OpenCV menggunakan BGR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Konversi ke HSV untuk analisis warna
            hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
            
            # Hitung rata-rata warna
            avg_color = np.mean(img_rgb, axis=(0, 1))
            avg_hsv = np.mean(hsv, axis=(0, 1))
            
            # Analisis warna dominan
            if avg_hsv[0] < 30 and avg_hsv[1] > 50:  # Hijau
                color_status = "Hijau Sehat"
            elif avg_hsv[0] > 30 and avg_hsv[0] < 90 and avg_hsv[1] > 50:  # Kuning
                color_status = "Kuning (Stres)"
            elif avg_hsv[0] > 90:  # Biru/Abu-abu
                color_status = "Biru/Abu-abu (Kemungkinan Penyakit)"
            else:
                color_status = "Warna Tidak Dikenal"
            
            return {
                "status": color_status,
                "average_rgb": [int(avg_color[0]), int(avg_color[1]), int(avg_color[2])],
                "average_hsv": [int(avg_hsv[0]), int(avg_hsv[1]), int(avg_hsv[2])]
            }
            
        except Exception as e:
            return {"error": f"Error analisis warna: {str(e)}"}
