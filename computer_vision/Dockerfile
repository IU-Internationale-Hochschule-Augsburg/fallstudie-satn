# Use official Python-slim image (Debian)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libopenblas-dev \
    cmake \
    make \
    nasm \
    yasm \
    linux-headers-arm64 \
    libcap-dev

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy & install requirements with build isolation
COPY requirements.txt .
RUN pip install --no-cache-dir --use-pep517 --isolated -r requirements.txt

# Cleanup build dependencies
#  RUN apt-get remove -y .build-deps

# Copy entire computer_vision directory
COPY . .

# Use Port 5000
EXPOSE 5000

# Label Image for Pipeline
LABEL org.opencontainers.image.source="https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn"

# Run application
CMD ["python", "main.py"]
