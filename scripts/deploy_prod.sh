#!/bin/bash
set -e

echo "[배포] Docker 이미지 빌드 및 컨테이너 재시작"
docker-compose down
docker-compose pull
docker-compose up -d --build

echo "[배포] 마이그레이션 및 캐시 정리"
docker-compose exec backend flask db upgrade || true
docker-compose exec backend flask clear-cache || true

echo "[배포] 완료" 