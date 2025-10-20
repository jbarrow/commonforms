FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    CUDA_VISIBLE_DEVICES=

WORKDIR /app

# System deps (as needed by commonforms deps)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install web deps and project package
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn[standard]==0.30.6 jinja2==3.1.4 python-multipart==0.0.12 \
    && pip install --no-cache-dir -e .

# App working dir contains the web app module
WORKDIR /app/webapp/src

EXPOSE ${PORT}

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "${PORT}"]
