## 아키텍처
![11](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/c81884ac-9ef4-4d53-8410-bf1959fc274a)


## 예상흐름도
![13](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/5cbd5bd5-2f05-4e8f-877d-49814d30c45e)

1. 사용자가 특정한 AI Computer Vision (CV) 모델을 선택하여 Raspberry Pi(RPi)에서 이미지 분석을 요청합니다.
2. 사용자 요청은 서버에 도착하고, 서버는 API를 통해 이를 처리합니다.
3. 서버는 사용자가 요청한 AI CV 모델을 실행할 도커 컨테이너를 준비하고, 이를 위해 이미지 촬영 요청을 RPi로 전송합니다.
4. RPi는 CSI 카메라로 이미지를 촬영하고, 해당 이미지를 도커에 전달합니다.
5. 도커는 받은 이미지를 선택된 AI CV 모델로 분석하고, 결과를 서버로 전송합니다.
6. 서버는 분석된 결과를 데이터베이스에 저장합니다.
7. 마지막으로, 서버는 클라이언트에게 분석된 결과를 보내줍니다.
