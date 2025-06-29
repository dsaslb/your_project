#!/usr/bin/env python3
"""환경별 .env 파일 생성 스크립트"""

import os


def create_env_file(filename, content):
    """UTF-8 인코딩으로 .env 파일 생성"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"생성됨: {filename}")


# 개발 환경 설정
dev_content = """# 개발 환경 설정
FLASK_ENV=development
DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///restaurant_dev.sqlite3

# 파일 업로드 설정
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# 이메일 설정 (개발용)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=
MAIL_PASSWORD=

# 로깅 설정
LOG_LEVEL=DEBUG
LOG_FILE=logs/restaurant_dev.log

# 캐시 설정
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# 세션 설정
PERMANENT_SESSION_LIFETIME=3600
SESSION_COOKIE_SECURE=0
"""

# 운영 환경 설정
prod_content = """# 운영 환경 설정
FLASK_ENV=production
DEBUG=0
SECRET_KEY=prod-secret-key-change-this
DATABASE_URL=sqlite:///restaurant_prod.sqlite3

# 파일 업로드 설정
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# 이메일 설정
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=
MAIL_PASSWORD=

# 로깅 설정
LOG_LEVEL=WARNING
LOG_FILE=logs/restaurant_prod.log

# 캐시 설정
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# 세션 설정
PERMANENT_SESSION_LIFETIME=3600
SESSION_COOKIE_SECURE=1
"""

# 테스트 환경 설정
test_content = """# 테스트 환경 설정
FLASK_ENV=test
DEBUG=1
SECRET_KEY=test-secret-key
DATABASE_URL=sqlite:///:memory:

# 파일 업로드 설정
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# 이메일 설정
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=
MAIL_PASSWORD=

# 로깅 설정
LOG_LEVEL=DEBUG
LOG_FILE=logs/restaurant_test.log

# 캐시 설정
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# 세션 설정
PERMANENT_SESSION_LIFETIME=3600
SESSION_COOKIE_SECURE=0
"""

if __name__ == "__main__":
    print("환경별 .env 파일 생성 중...")

    create_env_file(".env.development", dev_content)
    create_env_file(".env.production", prod_content)
    create_env_file(".env.test", test_content)

    print("\n모든 .env 파일이 생성되었습니다!")
