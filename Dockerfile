FROM python:3.10.12-slim

WORKDIR /app

# Install dependencies dengan versi pasti
RUN pip install --no-cache-dir numpy==1.21.0 pandas==1.5.3 Flask==2.3.3 gunicorn==20.1.0

# Copy kode aplikasi
COPY . .

EXPOSE 8080

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
