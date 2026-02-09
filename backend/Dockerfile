FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
# Cache HuggingFace models in container
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface

WORKDIR /app

# Install System Dependencies (Debian version)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies (cached layer)
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Pre-download MiniLM model (intent classifier, ~80MB)
# This layer is cached - only rebuilds if above layers change
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
print('Downloading MiniLM...'); \
SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1'); \
print('MiniLM ready!')"

# Copy application code
COPY . .

# Note: Fine-tuned DistilBERT model (transaction_classification_model/)
# must be present in backend/app/ai/ before building, or mounted as volume.
# Run: python tools/download_model.py --check (to verify model status)
