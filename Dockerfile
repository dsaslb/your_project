# 멀티테넌시 관리 시스템 Docker 이미지
FROM python:3.10-slim

# 메타데이터
LABEL maintainer="your-email@example.com"
LABEL version="1.0.0"
LABEL description="멀티테넌시 관리 시스템 - 업종/브랜드/매장/직원 계층별 관리"

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 필요한 디렉토리 생성
RUN mkdir -p logs uploads backups

# 파일 권한 설정
RUN chmod +x scripts/deploy.sh
RUN chmod 755 logs uploads backups

# 포트 노출
EXPOSE 5000

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 애플리케이션 실행
CMD ["python", "app.py"] 