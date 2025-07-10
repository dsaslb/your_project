#!/usr/bin/env python3
"""
운영 배포 자동화 스크립트
MVP 완성 후 운영 환경 배포를 위한 스크립트
"""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """명령어 실행 및 결과 확인"""
    print(f"\n🔧 {description}...")
    print(f"실행 명령: {command}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ 성공: {description}")
        if result.stdout:
            print(f"출력: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {description}")
        print(f"에러: {e.stderr}")
        return False


def check_environment():
    """환경 설정 점검"""
    print("\n🔍 환경 설정 점검 중...")

    # 필수 파일 확인
    required_files = [
        ".env.production",
        "requirements.txt",
        "app.py",
        "config.py",
        "models.py",
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ 누락된 파일들: {missing_files}")
        return False

    print("✅ 필수 파일 확인 완료")

    # Python 버전 확인
    python_version = sys.version_info
    if python_version.major < 3 or (
        python_version.major == 3 and python_version.minor < 8
    ):
        print(
            f"❌ Python 3.8 이상 필요 (현재: {python_version.major}.{python_version.minor})"
        )
        return False

    print(f"✅ Python 버전 확인 완료 ({python_version.major}.{python_version.minor})")
    return True


def install_dependencies():
    """의존성 설치"""
    print("\n📦 의존성 설치 중...")

    # 가상환경 확인
    if not os.path.exists("venv"):
        print("가상환경 생성 중...")
        if not run_command("python -m venv venv", "가상환경 생성"):
            return False

    # 가상환경 활성화 및 패키지 설치
    if os.name == "nt":  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"

    # 패키지 설치
    if not run_command(f"{pip_cmd} install -r requirements.txt", "패키지 설치"):
        return False

    return True


def setup_database():
    """데이터베이스 설정"""
    print("\n🗄️ 데이터베이스 설정 중...")

    # 마이그레이션 실행
    if not run_command("flask db upgrade", "데이터베이스 마이그레이션"):
        return False

    # 관리자 계정 생성 확인
    print("관리자 계정 확인 중...")
    if not run_command("flask create-admin", "관리자 계정 확인"):
        print("⚠️ 관리자 계정이 없습니다. 수동으로 생성해주세요.")

    return True


def setup_logging():
    """로깅 설정"""
    print("\n📝 로깅 설정 중...")

    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 로그 파일 권한 설정
    log_files = ["your_program_prod.log", "action.log"]
    for log_file in log_files:
        log_path = log_dir / log_file
        if not log_path.exists():
            log_path.touch()

    print("✅ 로깅 설정 완료")
    return True


def security_check():
    """보안 점검"""
    print("\n🔒 보안 점검 중...")

    # 환경 변수 확인
    env_vars = ["SECRET_KEY", "DATABASE_URL", "SLACK_WEBHOOK_URL"]

    missing_vars = []
    for var in env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️ 설정되지 않은 환경 변수: {missing_vars}")
        print("운영 환경에서 반드시 설정해주세요.")

    # 파일 권한 확인
    sensitive_files = [".env.production", "instance/"]
    for file in sensitive_files:
        if os.path.exists(file):
            print(f"✅ {file} 존재 확인")

    print("✅ 보안 점검 완료")
    return True


def create_startup_scripts():
    """시작 스크립트 생성"""
    print("\n🚀 시작 스크립트 생성 중...")

    # Windows 배치 파일
    windows_script = """@echo off
echo your_program Staff Management System 시작 중...
set FLASK_ENV=production
set FLASK_APP=app.py
cd /d "%~dp0"
call venv\\Scripts\\activate
python app.py
pause
"""

    with open("start_production.bat", "w", encoding="utf-8") as f:
        f.write(windows_script)

    # Linux/Mac 쉘 스크립트
    unix_script = """#!/bin/bash
echo "your_program Staff Management System 시작 중..."
export FLASK_ENV=production
export FLASK_APP=app.py
cd "$(dirname "$0")"
source venv/bin/activate
python app.py
"""

    with open("start_production.sh", "w", encoding="utf-8") as f:
        f.write(unix_script)

    # Unix 스크립트 실행 권한 설정
    if os.name != "nt":
        os.chmod("start_production.sh", 0o755)

    print("✅ 시작 스크립트 생성 완료")
    return True


def create_deployment_checklist():
    """배포 체크리스트 생성"""
    print("\n📋 배포 체크리스트 생성 중...")

    checklist = """# 🚀 운영 배포 체크리스트

## ✅ 사전 준비사항
- [ ] .env.production 파일 설정 완료
- [ ] 데이터베이스 백업 완료
- [ ] 도메인/SSL 인증서 준비
- [ ] 서버 리소스 확인 (CPU, RAM, 디스크)

## 🔧 환경 설정
- [ ] FLASK_ENV=production 설정
- [ ] SECRET_KEY 변경 (강력한 랜덤 키)
- [ ] DATABASE_URL 설정 (운영용 DB)
- [ ] SLACK_WEBHOOK_URL 설정 (선택사항)

## 🛡️ 보안 설정
- [ ] 방화벽 설정 (포트 5000 또는 80/443)
- [ ] SSL 인증서 설치
- [ ] 파일 권한 설정 (logs/, instance/ 등)
- [ ] 관리자 계정 비밀번호 변경

## 📊 모니터링 설정
- [ ] 로그 모니터링 설정
- [ ] Slack 알림 설정 (선택사항)
- [ ] 백업 스케줄 설정
- [ ] 성능 모니터링 설정

## 🚀 배포 실행
- [ ] 의존성 설치: pip install -r requirements.txt
- [ ] 데이터베이스 마이그레이션: flask db upgrade
- [ ] 관리자 계정 생성: flask create-admin
- [ ] 애플리케이션 시작: python app.py

## ✅ 배포 후 확인사항
- [ ] 웹사이트 접속 확인
- [ ] 로그인/로그아웃 테스트
- [ ] 주요 기능 동작 확인
- [ ] 로그 파일 생성 확인
- [ ] Slack 알림 테스트 (설정된 경우)

## 📞 문제 발생 시
- 로그 확인: logs/your_program_prod.log
- 데이터베이스 연결 확인
- 환경 변수 설정 재확인
- 서버 리소스 사용량 확인

---
배포 완료일: ___________
배포 담당자: ___________
"""

    with open("DEPLOYMENT_CHECKLIST.md", "w", encoding="utf-8") as f:
        f.write(checklist)

    print("✅ 배포 체크리스트 생성 완료")
    return True


def main():
    """메인 배포 프로세스"""
    print("🚀 your_program Staff Management System - 운영 배포 준비")
    print("=" * 60)

    # 1. 환경 점검
    if not check_environment():
        print("❌ 환경 점검 실패. 배포를 중단합니다.")
        return False

    # 2. 의존성 설치
    if not install_dependencies():
        print("❌ 의존성 설치 실패. 배포를 중단합니다.")
        return False

    # 3. 데이터베이스 설정
    if not setup_database():
        print("❌ 데이터베이스 설정 실패. 배포를 중단합니다.")
        return False

    # 4. 로깅 설정
    if not setup_logging():
        print("❌ 로깅 설정 실패. 배포를 중단합니다.")
        return False

    # 5. 보안 점검
    if not security_check():
        print("⚠️ 보안 점검에서 문제 발견. 확인 후 진행하세요.")

    # 6. 시작 스크립트 생성
    if not create_startup_scripts():
        print("❌ 시작 스크립트 생성 실패.")
        return False

    # 7. 배포 체크리스트 생성
    if not create_deployment_checklist():
        print("❌ 배포 체크리스트 생성 실패.")
        return False

    print("\n" + "=" * 60)
    print("🎉 배포 준비 완료!")
    print("\n📋 다음 단계:")
    print("1. DEPLOYMENT_CHECKLIST.md 파일을 확인하세요")
    print("2. .env.production 파일을 설정하세요")
    print("3. 서버에 파일을 업로드하세요")
    print(
        "4. start_production.bat (Windows) 또는 start_production.sh (Linux/Mac)를 실행하세요"
    )
    print("\n📞 문제가 발생하면 로그 파일을 확인하세요: logs/your_program_prod.log")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

