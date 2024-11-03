# Computer-Vision-Suite for Raspberry Pi 5 

> **동아대학교** <br/>
**개발기간: 2022.03 ~ 2022.10** <br/>
**개발인원: 4명** <br/>

> **Dong-A University** <br>
**Development Period: March 2022 - October 2022** <br>
**Team Size: 4 Developers**


## Project Overview
위 저장소는 새롭게 출시된 라즈베리 파이 5 환경에서 다양한 컴퓨터 비전모델들을 시험하고 싶어하는 사용자를 위해 만들었습니다. <br>

여러 컴퓨터 비전 모델들을 하나의 환경에서 구동시키기 위해, 도커 시스템을 이용하여 모델별로 독립된 환경을 구축하였습니다.<br>
또한 사용자는 Web UI를 통해 여러 모델들을 선택하고 실행할 수 있도록 WebRTC 통신 기반 웹서버를 구축하였습니다.<br>


<br>
This repository was developed for users interested in testing various computer vision models on the new Raspberry Pi 5 platform. <br>
To enable multiple models to run within a single environment, each model operates within an isolated Docker container.<br>
Additionally, we implemented a WebRTC-based web server, allowing users to select and run different models directly through a web UI. <br>This suite provides flexibility for experimenting with and benchmarking various computer vision applications on a compact, versatile platform.


---

## Stacks 🐈

### Environment
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Github](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)             

### Vision model framework
![onnx](https://img.shields.io/badge/onnx-005CED?style=for-the-badge&logo=onnx&logoColor=white)
![tensorflow](https://img.shields.io/badge/tensorflow-F98309?style=for-the-badge&logo=tensorflow&logoColor=white)     

### Development
![aiohttp](https://img.shields.io/badge/aiohttp-00B388?style=for-the-badge&logo=aiohttp&logoColor=white)
![opencv](https://img.shields.io/badge/opencv-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![webRTC](https://img.shields.io/badge/webRTC-29ABE2?style=for-the-badge&logo=webRTC&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=Javascript&logoColor=white)


---

## ⭐️Getting Started Guide
### Requirements
For building and running the application you need:

- Hardware: [Raspberry Pi 5 (Model B recommended)](https://www.raspberrypi.com/products/raspberry-pi-5/), [Raspberry Pi Camera Module V2](https://www.raspberrypi.com/products/camera-module-v2/)

- Operating System: Raspberry Pi OS or any Debian-based OS

- Required Software: Docker, Docker Compose, Python 3.7 or higher


### Installation
``` bash
$ git clone https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision.git
$ cd Raspberry-Pi-5-Computer-Vision/DOCKERFILE
```

#### Install Docker
```
$ sudo apt-get update

$ sudo apt-get upgrade

$ curl -fsSL https://get.docker.com -o get-docker.sh

$ sudo sh get-docker.sh

$ docker --version // Check Docker version to confirm installation
```

#### Install Docker Compose
```
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/dockercompose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

$ sudo chmod +x /usr/local/bin/docker-compose

$ sudo chmod 666 /var/run/docker.sock
```

### Run
```
docker-compose up --build
```


## 화면 구성 📺

---
## 주요 기능 📦

---
## 아키텍쳐

### Directory Structure
```bash
├── README.md
├── DOCKERFILE : 
│   ├── README.md
│   ├── web :
│   │   ├── src :
│   │   │    ├──static
│   │   │    │   └──client.js
│   │   │    ├──templates
│   │   │    │   └──index.html
│   │   │    └──app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── onnx : 
│   │   ├── src :
│   │   │    ├──static
│   │   │    │   └──client.js
│   │   │    ├──templates
│   │   │    │   └──index.html
│   │   │    ├──app.py
│   │   │    ├──labels.txt
│   │   │    ├──onnx_ssd_object_detection.py
│   │   │    └──onnx_yolo_object_detection.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── tflite
│   │   ├── src :
│   │   │    ├──static
│   │   │    │   └──client.js
│   │   │    ├──templates
│   │   │    │   └──index.html
│   │   │    ├──app.py
│   │   │    ├──labels.txt
│   │   │    └──tflite_object_detection.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └──  docker-compose.yml
└── 실증적 sw프로젝트 : 주간 회의록 및 자료
```
