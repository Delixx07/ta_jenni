# Dockerfile backend RCMS (FastAPI + SBERT).
# Catatan: image cukup besar karena torch/sentence-transformers.
FROM python:3.12-slim

# Dependency sistem minimal untuk psycopg2 & build wheel.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependency Python lebih dulu (manfaatkan cache layer).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi.
COPY . .

# Pra-unduh model SBERT saat build agar request pertama tidak lambat (opsional).
# Hilangkan baris ini bila ingin image lebih kecil / unduh saat runtime.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Jalankan migration lalu start server. $PORT diisi platform (default 8000).
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
