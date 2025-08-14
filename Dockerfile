# Gunakan Python 3.10.12 sebagai base image
FROM python:3.10.12-slim

# Set working directory di dalam container
WORKDIR /app

# Salin requirements.txt dulu (untuk caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari laptop ke container
COPY . .

# Expose port (Render akan override, tapi wajib ada)
EXPOSE 8080

# Jalankan aplikasi dengan gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]