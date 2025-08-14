import sqlite3
import pandas as pd
from datetime import datetime

class HistoricalDataManager:
    def __init__(self, db_path='data/historical.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        try:
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
            print(f"Error membuat database: {e}")
    
    def save_prediction(self, data_dict):
        try:
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
            print(f"Error menyimpan data historis: {e}")

# Inisialisasi database
db_manager = HistoricalDataManager()