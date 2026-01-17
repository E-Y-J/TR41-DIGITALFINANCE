FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install System Dependencies (Debian version)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
