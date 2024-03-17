# 조현진

## Computer Vision Problem
<br/>

### Object Recognition
    
**이미지와 비디오에서 객체를 인식 + 분류하는 문제** 
    
- Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks
    - 기존의 객체 탐지 네트워크는 region proposal 알고리즘에 의존하여 객체의 위치를 가정하여 계산의 병목 현상에 직면
    - 본 논문에서는 Region Proposal Network(RPN)을 도입하여 convolution의 특징을 공유하고, anchor box를 사용하여 다양한 스케일과 종횡비에서 효율적으로 region proposal을 예측
    - → 빠른 속도로 정확도가 높은 객체 탐지를 달성

<br/>

### Image Classification
    
**이미지를 카테고리화, 라벨링 하는 것에 초점을 둔 문제**

- Sharpness-Aware Minimization for Efficiently Improving Generalization
    - loss값을 최적화하는 것에 과도하게 parameterized된 모델들은 오히려 성능이 떨어진다
    - loss value와 loss sharpness를 동시에 최소화하는 새로운 절차인  Sharpness-Aware Minimization (SAM) 소개

<br/>

### Object Detection
    
**이미지와 비디오에서 관심 있는 객체를 감지하고 찾는 문제**

1. 추론 속도를 우선시 하는 문제 - YOLO, SSD, RetinaNet
2. 탐지 정확도를 우선시 하는 문제 - Faster R-CNN, Mask R-CNN, Cascade R-CNN

<br/>

### Object Tracking
    
**초기에 감지한 객체에 대해 각각 고유한 ID를 할당한 후, 다음 비디오 프레임에 따라 추적하여 ID 할당을 유지하는 문제**

- HOTA, IDF1, Track-mAP
