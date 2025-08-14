import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

def create_sample_data():
    """Membuat data contoh untuk pelatihan"""
    data = {
        'pH': [5.2, 5.5, 5.8, 6.0, 6.2, 6.4, 5.3, 5.7, 6.1, 5.0],
        'N_mg_kg': [18, 20, 25, 28, 30, 27, 19, 24, 29, 16],
        'P_mg_kg': [9, 10, 15, 18, 20, 19, 11, 14, 19, 8],
        'K_persen': [0.25, 0.27, 0.30, 0.32, 0.35, 0.33, 0.26, 0.29, 0.34, 0.23],
        'cuaca': ['hujan', 'hujan', 'hujan', 'hujan', 'hujan', 'hujan', 'kemarau', 'kemarau', 'kemarau', 'kemarau'],
        'musim': ['kemarau', 'kemarau', 'kemarau', 'kemarau', 'kemarau', 'kemarau', 'hujan', 'hujan', 'hujan', 'hujan'],
        'hasil_kg': [3.8, 4.1, 4.5, 4.8, 5.0, 4.7, 3.9, 4.4, 4.9, 3.5]
    }
    return pd.DataFrame(data)

def create_model():
    """Membuat model prediksi hasil panen"""
    
    # Buat data contoh
    df = create_sample_data()
    
    # Encode kategorikal data
    df['cuaca_encoded'] = df['cuaca'].map({'hujan': 0, 'kemarau': 1})
    df['musim_encoded'] = df['musim'].map({'kemarau': 0, 'hujan': 1})
    
    # Siapkan fitur
    features = ['pH', 'N_mg_kg', 'P_mg_kg', 'K_persen', 'cuaca_encoded', 'musim_encoded']
    X = df[features]
    y = df['hasil_kg']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Latih model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluasi
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error: {mae}")
    
    # Simpan model
    model_dir = 'models'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    joblib.dump(model, os.path.join(model_dir, 'yield_model.pkl'))
    print("✅ Model berhasil disimpan sebagai yield_model.pkl")
    
    return model

if __name__ == "__main__":
    model = create_model()
    print("Model siap digunakan!")