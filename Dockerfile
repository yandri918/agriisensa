FROM python:3.10.12-slim

# Install dependencies sistem
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libxcomposite1 \
    libasound2 \
    libxtst6 \
    libgtk-3-0 \
    libgl1 \
    libglu1-mesa \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies dengan versi pasti
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==1.5.3 \
    Flask==2.3.3 \
    gunicorn==20.1.0 \
    joblib==1.3.2 \
    opencv-python-headless==4.8.1.78 \
    tensorflow==2.13.0 \
    keras==2.13.1 \
    scikit-learn==1.3.0 \
    Pillow==10.0.1

# Copy kode aplikasi
COPY . .

EXPOSE 8080

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
