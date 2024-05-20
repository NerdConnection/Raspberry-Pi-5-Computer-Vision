FROM debian:bullseye

# Install basic packages including X11, wget, and unzip
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    ca-certificates \
    xauth \
    x11-apps \
    wget \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add Raspberry Pi archive signing key
RUN curl -fsSL https://archive.raspberrypi.org/debian/raspberrypi.gpg.key | gpg --dearmor -o /usr/share/keyrings/raspi-archive-keyring.gpg

# Add Raspberry Pi repository
RUN echo 'deb [signed-by=/usr/share/keyrings/raspi-archive-keyring.gpg] http://archive.raspberrypi.org/debian/ bullseye main' > /etc/apt/sources.list.d/raspi.list

# Update and install additional packages
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y --no-install-recommends \
        python3-pip \
        python3-picamera2 \
        libopencv-dev \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/* 

RUN fuser -k /dev/video0 || true
# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ONNX model
COPY mobilenet_v2_float.onnx /app/

# Copy the label map file
COPY imagenet_classes.txt /app/

# Copy the Python script
COPY inference_mobilenet.py /app/

# Set the entry point to run the script with the model
CMD ["python3", "/app/inference_mobilenet.py"]
