# Base image with GPU support
FROM nvidia/cuda:11.4.1-cudnn8-devel-ubuntu20.04

# Set the debian frontend to avoid interactive prompts during installation
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update -y && apt-get install -y \
    git \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3 \
    python3-pip \
    gcc \
    python3-tk \
    ffmpeg \
    libopenblas-dev \
    liblapack-dev && \
    apt-get clean

# Install dlib with CUDA support
RUN git clone https://github.com/davisking/dlib.git && \
    cd dlib && \
    mkdir build && \
    cd build && \
    cmake .. -DDLIB_USE_CUDA=1 -DUSE_AVX_INSTRUCTIONS=1 && \
    cmake --build . && \
    cd .. && \
    python3 setup.py install && \
    cd .. && rm -rf dlib

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
