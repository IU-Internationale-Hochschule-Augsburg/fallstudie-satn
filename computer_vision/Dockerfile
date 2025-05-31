# Use official Python-Alpine image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    libffi-dev \
    openssl-dev \
    libjpeg-turbo-dev \
    openblas-dev \
    cmake \
    make \
    nasm \
    yasm \
    linux-headers \
    libcap-dev

# Install runtime dependencies
RUN apk add --no-cache \
    libjpeg \
    zlib \
    openblas

# Copy & install requirements with build isolation
COPY requirements.txt .
RUN pip install --no-cache-dir --use-pep517 --isolated -r requirements.txt

# Cleanup build dependencies
RUN apk del .build-deps

# Copy entire computer_vision directory
COPY . .

# Use Port 5000
EXPOSE 5000

# Label Image for Pipeline
LABEL org.opencontainers.image.source="https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn"

# Run application
CMD ["python", "main.py"]
