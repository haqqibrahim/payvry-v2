# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set non-interactive frontend for apt commands
ARG DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    cmake \
    gcc \
    g++ \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libopenblas-dev \
    liblapack-dev \
    ffmpeg \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dlib
RUN git clone https://github.com/davisking/dlib.git && \
    cd dlib && \
    mkdir build && cd build && \
    cmake .. -DDLIB_USE_CUDA=0 -DUSE_AVX_INSTRUCTIONS=1 && \
    cmake --build . && cd .. && \
    python3 setup.py install && \
    cd .. && rm -rf dlib

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Copy application files into the image
COPY . /app

# Expose the port your FastAPI app runs on (default is 8000)
EXPOSE 8000

# Start the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
