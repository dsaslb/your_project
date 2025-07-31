.PHONY: help install install-dev test test-unit test-integration test-api test-performance lint format clean run dev setup-db migrate

help: ## 도움말 표시
	@echo "사용 가능한 명령어:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 프로덕션 의존성 설치
	pip install -r requirements.txt

install-dev: ## 개발 의존성 설치
	pip install -r requirements-dev.txt
	pre-commit install

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

run: ## 프로덕션 서버 실행
	python app.py

dev: ## 개발 서버 실행
	export FLASK_ENV=development
	export FLASK_DEBUG=1
	python app.py

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