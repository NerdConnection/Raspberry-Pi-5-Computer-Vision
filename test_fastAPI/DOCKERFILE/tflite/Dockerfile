FROM debian:bookworm

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
RUN echo 'deb [signed-by=/usr/share/keyrings/raspi-archive-keyring.gpg] http://archive.raspberrypi.org/debian/ bookworm main' > /etc/apt/sources.list.d/raspi.list

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y --no-install-recommends \
        python3-pip \
        python3-picamera2 \
        libopencv-dev \
        python3-setuptools \
        python3-wheel \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /app

COPY requirements.txt .

RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY src /app/src

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]

