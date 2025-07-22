# 멀티테넌시 관리 시스템 - 프론트엔드 Dockerfile

# 빌드 스테이지
FROM node:18-alpine AS builder

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 프로덕션 빌드
RUN npm run build

# 프로덕션 스테이지
FROM nginx:alpine

# nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/nginx.conf

# 빌드된 파일을 nginx로 복사
COPY --from=builder /app/.next /usr/share/nginx/html

# 정적 파일 복사
COPY --from=builder /app/public /usr/share/nginx/html/public

# 포트 노출
EXPOSE 80

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# nginx 시작
CMD ["nginx", "-g", "daemon off;"] 