FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libgtk2.0-dev \
    pkg-config \
    libhdf5-dev \
    curl \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install numpy opencv-python~=4.5.3.56
RUN pip install protobuf==3.20
RUN pip install tflite-support==0.4.0

COPY . /app
WORKDIR /app

RUN curl -L 'https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/image_classification/rpi/lite-model_efficientnet_lite0_uint8_2.tflite' -o ./efficientnet_lite0.tflite && \
    curl -L 'https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/image_classification/rpi/efficientnet_lite0_edgetpu.tflite' -o ./efficientnet_lite0_edgetpu.tflite

CMD ["python", "test.py"]
