FROM debian:bullseye

RUN apt-get update && apt-get install -y --no-install-recommends gnupg curl ca-certificates

# Add Raspberry Pi archive signing key
RUN curl -fsSL https://archive.raspberrypi.org/debian/raspberrypi.gpg.key | gpg --dearmor -o /usr/share/keyrings/raspi-archive-keyring.gpg

# Add Raspberry Pi repository
RUN echo 'deb [signed-by=/usr/share/keyrings/raspi-archive-keyring.gpg] http://archive.raspberrypi.org/debian/ bullseye main' > /etc/apt/sources.list.d/raspi.list

RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y --no-install-recommends \
        python3-pip \
        python3-picamera2 \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------------------------
# Build and run application
# ------------------------------------------------------------------------------------------------
# Set the working directory
WORKDIR /app



# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python files
COPY camera_capture /app/camera_capture

# Set the entry point
CMD ["python3", "/app/camera_capture/main.py"]
