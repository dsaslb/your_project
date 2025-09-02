.PHONY: help install install-dev test test-unit test-integration test-api test-performance lint format clean run dev setup-db migrate docker-build docker-run docker-compose-up docker-compose-down logs monitor security-check

help: ## 도움말 표시
	@echo "사용 가능한 명령어:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 프로덕션 의존성 설치
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev: ## 개발 의존성 설치
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy isort bandit safety
	@echo "개발 환경 설정 완료"

setup-db: ## 데이터베이스 설정
	flask db upgrade

migrate: ## 데이터베이스 마이그레이션
	flask db migrate -m "Auto migration"
	flask db upgrade

test: ## 모든 테스트 실행
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

test-unit: ## 단위 테스트 실행
	pytest tests/unit/ -v -m unit

test-integration: ## 통합 테스트 실행
	pytest tests/integration/ -v -m integration

test-api: ## API 테스트 실행
	pytest tests/api/ -v -m api

test-performance: ## 성능 테스트 실행
	pytest tests/performance/ -v -m performance

test-security: ## 보안 테스트 실행
	pytest tests/ -v -m security

lint: ## 코드 린팅
	flake8 . --max-line-length=120 --extend-ignore=E203,W503
	black --check --diff . --line-length=120
	isort --check-only --diff . --profile=black
	mypy . --ignore-missing-imports --no-strict-optional

format: ## 코드 포맷팅
	black . --line-length=120
	isort . --profile=black

security-check: ## 보안 검사
	bandit -r . -f json -o bandit-report.json
	safety check --json --output safety-report.json

clean: ## 캐시 및 임시 파일 정리
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

run: ## 프로덕션 서버 실행 (Gunicorn)
	gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent --worker-connections 1000 --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app

dev: ## 개발 서버 실행
	export FLASK_ENV=development
	export FLASK_DEBUG=1
	python app.py

run-dev: ## 개발 서버 실행 (자동 재시작)
	export FLASK_ENV=development
	export FLASK_DEBUG=1
	flask run --host=0.0.0.0 --port=5000 --reload

docker-build: ## Docker 이미지 빌드
	docker build -t your-program-backend .

docker-run: ## Docker 컨테이너 실행
	docker run -p 5000:5000 your-program-backend

docker-compose-up: ## Docker Compose로 서비스 실행
	docker-compose up -d

docker-compose-down: ## Docker Compose 서비스 중지
	docker-compose down

logs: ## 로그 확인
	tail -f logs/app.log

monitor: ## 시스템 모니터링
	ps aux | grep python
	netstat -tlnp | grep :5000

check: ## 전체 시스템 점검
	@echo "=== 코드 품질 검사 ==="
	$(MAKE) lint
	@echo "=== 보안 검사 ==="
	$(MAKE) security-check
	@echo "=== 테스트 실행 ==="
	$(MAKE) test
	@echo "=== 모든 검사 완료 ==="

optimize: ## 시스템 최적화
	@echo "=== 캐시 정리 ==="
	$(MAKE) clean
	@echo "=== 의존성 업데이트 ==="
	pip install --upgrade pip
	pip install -r requirements.txt --upgrade
	@echo "=== 최적화 완료 ==="

backup: ## 데이터베이스 백업
	@echo "=== 데이터베이스 백업 중 ==="
	mkdir -p backups
	cp instance/app.db backups/app_backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "=== 백업 완료 ==="

restore: ## 데이터베이스 복원 (백업 파일명을 BACKUP_FILE 변수로 지정)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "사용법: make restore BACKUP_FILE=backups/app_backup_20240101_120000.db"; exit 1; fi
	@echo "=== 데이터베이스 복원 중: $(BACKUP_FILE) ==="
	cp $(BACKUP_FILE) instance/app.db
	@echo "=== 복원 완료 ==="

logs-clean: ## 로그 파일 정리
	@echo "=== 로그 파일 정리 중 ==="
	find logs/ -name "*.log" -mtime +7 -delete
	@echo "=== 로그 정리 완료 ==="

health-check: ## 시스템 상태 확인
	@echo "=== 시스템 상태 확인 ==="
	curl -f http://localhost:5000/health || echo "서버가 실행되지 않았습니다"
	@echo "=== 상태 확인 완료 ===" 