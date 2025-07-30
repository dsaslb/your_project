# 멀티 스테이지 빌드를 위한 Dockerfile
FROM python:3.10-slim as python-base

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# PATH에 Poetry 추가
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# 시스템 의존성 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -

# 프론트엔드 빌드 스테이지
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# 프론트엔드 의존성 설치
COPY frontend/package*.json ./
RUN npm ci --only=production

# 프론트엔드 소스 복사 및 빌드
COPY frontend/ ./
RUN npm run build

# 백엔드 빌드 스테이지
FROM python-base as backend-builder

WORKDIR /app

# Poetry 설정 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry install --no-dev --no-root

# 애플리케이션 소스 복사
COPY . .

# 프론트엔드 빌드 결과 복사
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# 프로덕션 스테이지
FROM python:3.10-slim as production

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    FLASK_APP=app.py

# 시스템 의존성 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 비root 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 및 가상환경 복사
COPY --from=backend-builder $POETRY_HOME $POETRY_HOME
COPY --from=backend-builder $PYSETUP_PATH $PYSETUP_PATH

# PATH 설정
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# 애플리케이션 파일 복사
COPY --from=backend-builder /app /app

# 권한 설정
RUN chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 5000

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 애플리케이션 실행
CMD ["python", "app.py"] 