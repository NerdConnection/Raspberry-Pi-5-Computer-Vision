# Docker Commit & Build
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/bf7ee1be-9c91-4447-a08c-935f3ef0968c)
#### 기존 이미지를 수정하고 변경사항을 커밋하여 이미지를 저장하는 방법과 Dockerfile의 명세서를 따라 이미지를 빌드하는 방법이 있다.   
#### 도커 커밋은 실행 중인 컨테이너를 백업하는 용도로 많이 사용되며 도커 빌드는 Dockerfile을 기준으로 새로운 이미지를 생성할때 많이 사용된다. 
</br></br>

## 커밋을 통한 이미지 저장방법
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/123ff05d-4f76-4c20-abf5-916dacc84af7)
#### 도커 허브에서 이미지를 다운받은 다음 이미지를 실행시키면 독립된 컨테이너가 생성된다.   
#### 개발자는 생성된 컨테이너의 로직을 수정하고 이를 커밋을 통해 변경사항을 새로운 이미지에 저장할 수 있다.
</br></br>


#### 예시로 기존 yolov5-arm64 도커 이미지에 가중치 파일을 추가하고 이를 커밋하여 커스텀 이미지를 만들어 보자 </br>
#### yolov5 run을 통해 컨테이너를 생성한다.
```
# docker run
root@raspberrypi:~ $ sudo docker container run -it -d --name yolov5_2 ultralytics/yolov5:latest-arm64
a28db7390c265fe37212c8ba5f0740f2c0101a362dc191f4e9db0561591ed0d3
```
#### 컨테이너의 생성과 컨테이너의 파일을 확인해본다.
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/fc6d1ca4-f118-44d7-b786-10e94fae4280)


#### 생성된 yolov5이미지에는 가중치 파일이 없는 것을 확인할 수 있다.
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/029b2b67-2fc2-4370-b999-82a41fde45aa)


#### yolov5s.pt라는 가중치파일을 컨테이너 안에 저장한다.
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/5ee5e581-5612-4bd0-bc28-f5889a6d8d69)


#### 변경된 사항을 commit하여 새로운 myyoloimage라는 이름으로 이미지로 저장한다.
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/c030e343-cfb4-469a-99a5-7b2a791b8935)


#### 생성된 myyoloimage를 run하여 yolov5s.pt라는 가중치 파일이 존재하는지 확인한다.
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/68eb285b-0b48-4bb7-97f8-7599ea68b550)
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/098bfd57-5ef8-4a83-9a77-35a1eae1c111)



</br></br>
## Dockerfile로 build하여 생성하는 방법

#### dockerfile 작성
```
# 베이스 이미지 설정
FROM ubuntu:20.04

# 작업 디렉토리 설정
WORKDIR /usr/src/app

# yolov5s.pt 파일을 현재 디렉토리로 복사
COPY yolov5s.pt /usr/src/app/yolov5s.pt
```

#### dockerfile을 build해서 yolofromdockerfile 이라는 이름으로 이미지를 만들었다.
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/de68d394-1307-44cc-bbc4-33cd45b359c0)


#### 생성된 이미지를 run 해보면 yolov5s.pt라는 가중치파일이 추가됨을 확인할 수 있다.
![image](https://github.com/NerdConnection/Raspberry-Pi-5-Computer-Vision/assets/100738404/8647c137-d194-4631-9209-34511739df03)
