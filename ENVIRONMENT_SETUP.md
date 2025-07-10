# 🏪 레스토랑 관리 시스템 환경 설정 가이드

## 📋 개요

이 프로젝트는 **Conda + pip 혼합 환경**을 사용하여 다음과 같이 구성됩니다:

- **메인 환경 (pip)**: Flask, Alembic, 일반 웹 서비스
- **AI 환경 (별도 가상환경)**: TensorFlow, AI/ML 패키지
- **연동 방식**: REST API를 통한 통신

---

## 🚀 빠른 시작

### 1. 메인 환경 설정 (Flask + 웹 서비스)

```bash
# 1. Python 3.10 설치 확인
python --version  # Python 3.10.x

# 2. 메인 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. 메인 패키지 설치
pip install -r requirements.txt
```

### 2. AI 환경 설정 (TensorFlow + AI 패키지)

```bash
# 1. AI 전용 가상환경 생성
python -m venv ai_env

# 2. AI 환경 활성화
ai_env\Scripts\activate  # Windows
source ai_env/bin/activate  # Linux/Mac

# 3. AI 패키지 설치
pip install -r ai_requirements.txt
```

### 3. 서버 실행

```bash
# 터미널 1: 메인 Flask 서버
venv\Scripts\activate
python app.py

# 터미널 2: AI 예측 서버
ai_env\Scripts\activate
python ai_server.py
```

---

## 🔧 상세 설정

### 메인 환경 (requirements.txt)

```txt
# Flask 웹 프레임워크
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5

# 데이터베이스
alembic==1.13.1
SQLAlchemy==2.0.41

# 기타 웹 서비스
requests==2.31.0
aiohttp==3.9.1
```

### AI 환경 (ai_requirements.txt)

```txt
# 딥러닝/머신러닝
tensorflow==2.15.0
keras==2.15.0
scikit-learn==1.3.0

# 데이터 분석
numpy==1.24.3
pandas==2.3.0
matplotlib==3.7.2

# API 서버
fastapi==0.104.1
uvicorn==0.24.0
```

---

## 🔗 환경 연동

### 1. AI 서버 실행

```bash
# AI 환경에서
cd your_program_project
ai_env\Scripts\activate
python ai_server.py
```

**결과**: `http://localhost:8501`에서 AI 예측 API 서버 실행

### 2. 메인 앱에서 AI 호출

```python
# Flask 앱에서 AI 예측 사용
from ai_client import predict_weekly_sales, predict_menu_demand

# 매출 예측
sales_prediction = predict_weekly_sales(base_sales=1000)

# 메뉴 수요 예측
demand_prediction = predict_menu_demand(['burger', 'pizza', 'salad'])
```

### 3. API 엔드포인트

#### AI 서버 엔드포인트
- `GET /health` - 서버 상태 확인
- `POST /predict` - AI 예측 실행
- `GET /models` - 사용 가능한 모델 목록

#### 예시 요청
```bash
# 매출 예측
curl -X POST "http://localhost:8501/predict" \
  -H "Content-Type: application/json" \
  -d '{"data": {"days": 7, "base_sales": 1000}, "model_type": "sales_forecast"}'
```

---

## 🐳 Docker 지원 (선택사항)

### Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'
services:
  main-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - AI_SERVER_URL=http://ai-server:8501
  
  ai-server:
    build: 
      context: .
      dockerfile: Dockerfile.ai
    ports:
      - "8501:8501"
```

---

## 🔍 문제 해결

### 1. 패키지 충돌 문제

**증상**: TensorFlow 설치 시 alembic, exceptiongroup 등과 충돌

**해결**: AI 패키지는 별도 환경에서 관리

### 2. AI 서버 연결 실패

**확인사항**:
```bash
# AI 서버 상태 확인
curl http://localhost:8501/health

# 메인 앱에서 연결 테스트
python -c "from ai_client import is_ai_server_available; print(is_ai_server_available())"
```

### 3. 포트 충돌

**해결**: AI 서버 포트 변경
```python
# ai_server.py 수정
uvicorn.run(app, host="0.0.0.0", port=8502)  # 8501 → 8502
```

---

## 📚 개발 가이드

### 새로운 AI 모델 추가

1. **AI 환경에서 모델 개발**
```python
# ai_server.py에 새 모델 추가
def predict_new_feature(self, data):
    # TensorFlow 모델 로드 및 예측
    pass
```

2. **API 엔드포인트 추가**
```python
@app.post("/predict/new-feature")
async def predict_new_feature(request: PredictionRequest):
    # 새 모델 호출
    pass
```

3. **메인 앱에서 클라이언트 추가**
```python
# ai_client.py에 새 함수 추가
def predict_new_feature(data):
    return ai_client.predict_new_feature(data)
```

### 환경 업데이트

```bash
# 메인 환경 업데이트
pip install --upgrade -r requirements.txt

# AI 환경 업데이트
ai_env\Scripts\activate
pip install --upgrade -r ai_requirements.txt
```

---

## 🎯 운영 체크리스트

### 개발 환경
- [ ] Python 3.10 설치
- [ ] 메인 가상환경 생성 및 패키지 설치
- [ ] AI 가상환경 생성 및 패키지 설치
- [ ] 메인 서버 실행 확인
- [ ] AI 서버 실행 확인
- [ ] 환경 연동 테스트

### 프로덕션 환경
- [ ] 환경 변수 설정
- [ ] 데이터베이스 연결 확인
- [ ] AI 모델 파일 배포
- [ ] 로그 설정
- [ ] 모니터링 설정

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **로그 확인**: 각 서버의 로그 출력
2. **환경 확인**: 가상환경 활성화 상태
3. **포트 확인**: 5000 (메인), 8501 (AI) 포트 사용 가능 여부
4. **의존성 확인**: requirements.txt, ai_requirements.txt 패키지 설치 상태

---

**💡 팁**: 개발 시에는 두 개의 터미널을 사용하여 메인 서버와 AI 서버를 동시에 실행하세요! 
