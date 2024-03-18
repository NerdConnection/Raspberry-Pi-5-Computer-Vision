# 조현진

## Computer Vision Problem
<br/>

### Object Recognition
    
**이미지와 비디오에서 객체를 인식 + 분류하는 문제** 
    
- Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks
    - 기존의 객체 탐지 네트워크는 region proposal 알고리즘에 의존하여 객체의 위치를 가정하여 계산의 병목 현상에 직면
    - 본 논문에서는 Region Proposal Network(RPN)을 도입하여 convolution의 특징을 공유하고, anchor box를 사용하여 다양한 스케일과 종횡비에서 효율적으로 region proposal을 예측
    - → 빠른 속도로 정확도가 높은 객체 탐지를 달성

- Occlusion : 다른 사물이 사물의 일부를 숨기거나 차단해서 인식에 문제가 발생하는 현상
    - 스트레오 매칭 : MRF-MAP 기반의 에너지 함수를 만들어, 그래프 컷으로 최적화하는 방법 (폐색 영역 보정)
    -> 색상과 공간의 유사성을 계산하는 함수를 정의하여 초기 깊이 정보를 예측
    - RPCA : 주성분 분석(PCA) 통계 절차를 수정한 것으로, 매우 손상된 관측 자료에서 낮은 순위의 행렬을 복구

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

  <br/>

### Variable lighting conditions
    
**빛(자연광, 인공광등)의 각도나 강도에 따른 사물 인식 문제**

- 히스토그램 균등화
    - 이미지 전체에서 가장 빈번한 강도 값을 재분배하여 이미지의 대비를 개선하는 방법
    - 동시에 감마 보정은 픽셀 값에 비선형 연산을 적용하여 이미지의 밝기를 조정

  <br/>

### Perception issues due to perspective

**원근법에 의한 사물 인식 문제**

- 카메라에 대한 거리, 각도 또는 크기에 따라 유사한 다른 물체로 인식할 수 있음
    - SIFT : arris corner의 scale 변화에 민감한 문제를 해결하기 위해 Difference of Gaussian(DoG)를 기반으로 scale 축으로도 코너성이 extrema인 점을 찾는 알고리즘
    - SURF : 연산량 문제를 GPGPU (General-Purpose computing on Graphics Processing Units) 기술을 이용한 병렬화를 통해 개선
            -> SIFT에 비해 속도가 개선된 SURF를 활용하여 영상 정렬을 수행하는 문제를 해결 가능

### Contextual understanding of Computer Vision 

- 이미지에서 개별 객체를 식별할 수는 있지만 객체 간의 관계를 이해하고 장면을 해석하는 것은 문제
    1. CSU, COS
    2. GNN, NLP 
