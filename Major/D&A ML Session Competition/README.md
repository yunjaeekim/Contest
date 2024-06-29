### 🙇‍♂️ 
#####  최종본 코드에서 pipeline output이 제대로 안나오는 문제가 발생하여 nbviewer을 통해 해결했습니다. 코드를 보시려면 아래 url을 클릭해주세요.
- 최종본 코드 : https://nbviewer.org/github/yunjaeekim/Contest/blob/main/Major/D%26A%20ML%20Session%20Competition/ML_%EC%B5%9C%EC%A2%85%EB%B3%B8.ipynb

<br>

### 🏆 1. 프로젝트 주제 : 서울과 부산에 존재하는 아파트의 실제 거래 가격 예측 Competition

### 📋 2. 프로젝트 개요 
- 인원 : 4명(조장 : 김윤재 / 조원 : 백경린, 손아현, 홍예진)
- 일시 : 2023.11.10 ~ 2023.11.28
#### 📌 역할
- Train, day_care_center 전처리 및 column 생성
- 대출 금리 전처리 및 column 생성
- 데이터 병합 후 추가 column 생성
- Shap 라이브러리 사용 및 HistGradientBoostingRegressor 모델 생성

### 🗂️ 3. 데이터 셋
- 내부 데이터 : Train / day_care_center / park / Test
- 외부 데이터 : 전국초중학교위치표준데이터 / 전체_도시철도역사정보_20230915 / 대출 금리 / 서울 평균 소득 / 부산 평균 소득

### 🕵️‍♂️ 4. 분석 및 모델링 전략
- 💡 IDEA : 모델 하이퍼 파라미터 튜닝보다 column을 만드는 것이 실제 예측하는 데에 있어 도움을 많이 줄 것이라 생각하여, 외부 데이터를 많이 사용하자.

##### 🛠️ 데이터 전처리
- 결측치 처리 : 수치형만 있었기 때문에 주변 구 별 평균으로 대체
- 이상치 처리 : Min-Max Scaling을 적용

##### 🚀 Feature Engineering
1) 내부 데이터
   - 보육원(day_care_center) 데이터 : 구 별 통학 차량 비율 / 구 별 어린이집 종류(비율로 표현)
   - 공원(park) 데이터 : 동 별 공원의 비율
   - train,test 데이터 : top 10 시공사 아파트 여부 / 동일 아파트 수 / 빈도 수 top 25 아파트 여부 / 아파트 나이 / 거래 계절 / 이전 거래 여부 / 아파트 층 범주화 / 주상복합 여부 

    => 위의 2개의 데이터는 결측치가 너무 많아 column을 많이 만들 수 없었음.
2) 외부 데이터
   - 초중고 데이터 : 동 별 고등학교 수
   - 대출 금리 데이터 : 금리 변화율
   - 서울/ 부산 소득 데이터 : 동 별 평균 소득 금액

3) 데이터 병합 후
   - 각 column들 조합하여 추가로 파생 변수들을 생성

##### 🔄 Encoding
- 값이 얼마 없는 column : One-hot Encoding
- 고유값이 많은 column : Binary Encoding

##### 🎯 Modeling
- LGBM, XGboost,catboost, HistGradientBoostingRegressor 각 단일 모델과 Voting/ Ensembling 다 해본 결과,
- HistGradientBoostingRegressor 단일 모델이 성능이 제일 좋았다.

### 📝 5. 시사점
- 가설에 맞게 많은 외부 데이터 사용과 많은 column들을 생성해서 Competition 종합 2등을 차지하긴 했지만 1등과의 격차가 많이 컸다.
- 1등 코드를 분석해보니 주변 상권 데이터를 추가하고 나서 성능이 급격히 오른 것을 보아 외부 데이터 역시 잘 결정해야 하는 것을 깨달았다.
- 더 좋은 모델, 앙상블 방법이 많았을텐데 Column에 시간을 많이 쏟다보니 막상 modeling 부분을 신경쓰지 못한게 아쉬웠다.
- 파이프 라인을 사용하는 것이 시간과 코드 측면에서 효율적이었다.
