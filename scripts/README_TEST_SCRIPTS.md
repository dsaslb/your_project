# 테스트 실행 스크립트 사용법

이 폴더에는 가상환경 활성화부터 pytest 실행까지 한 번에 처리하는 Windows 배치 스크립트들이 포함되어 있습니다.

## 📁 스크립트 파일들

### 1. `run_tests.bat` - 기본 버전
- **용도**: 가장 안전하고 완전한 테스트 실행
- **특징**: 
  - 가상환경 자동 생성 옵션
  - pytest 자동 설치
  - 상세한 오류 처리
  - 사용자 친화적인 메시지

### 2. `run_tests_simple.bat` - 간단 버전
- **용도**: 빠른 테스트 실행
- **특징**:
  - 최소한의 기능
  - 빠른 실행
  - 가상환경이 이미 존재한다고 가정

### 3. `run_tests_advanced.bat` - 고급 버전
- **용도**: 다양한 테스트 옵션 제공
- **특징**:
  - 커버리지 리포트 생성
  - 병렬 테스트 실행
  - 특정 테스트 파일 실행
  - 상세한 출력 옵션

## 🚀 사용법

### 기본 사용법
```bash
# 기본 테스트 실행
run_tests.bat

# 간단한 테스트 실행
run_tests_simple.bat

# 고급 옵션 사용
run_tests_advanced.bat [옵션]
```

### 고급 옵션 사용법
```bash
# 도움말 보기
run_tests_advanced.bat help

# 커버리지 리포트 생성
run_tests_advanced.bat coverage

# 실패한 테스트만 실행
run_tests_advanced.bat fast

# 특정 테스트 파일 실행
run_tests_advanced.bat specific

# 상세한 출력
run_tests_advanced.bat verbose

# 병렬 테스트 실행
run_tests_advanced.bat parallel
```

## ⚙️ 사전 요구사항

1. **Python 설치**: Python 3.7 이상이 시스템에 설치되어 있어야 합니다.
2. **가상환경**: `venv` 폴더가 프로젝트 루트에 있어야 합니다.
3. **테스트 폴더**: `tests/` 폴더가 프로젝트 루트에 있어야 합니다.

## 🔧 설정

### 가상환경 경로 변경
스크립트에서 가상환경 경로를 변경하려면:
```batch
set VENV_PATH=your_venv_path
```

### 테스트 폴더 변경
테스트 폴더를 변경하려면:
```batch
set TEST_DIR=your_test_directory
```

## 📊 결과 확인

### 성공 시
```
========================================
[성공] 모든 테스트가 통과했습니다!
========================================
```

### 실패 시
```
========================================
[경고] 일부 테스트가 실패했습니다.
========================================
```

## 🐛 문제 해결

### 가상환경을 찾을 수 없는 경우
1. `venv` 폴더가 프로젝트 루트에 있는지 확인
2. 가상환경을 새로 생성할지 묻는 메시지에서 'y' 선택

### pytest가 설치되지 않은 경우
- 스크립트가 자동으로 pytest를 설치합니다
- 설치에 실패하면 수동으로 설치: `pip install pytest`

### 권한 오류가 발생하는 경우
- 관리자 권한으로 명령 프롬프트를 실행
- 또는 PowerShell을 사용하여 스크립트 실행

## 📝 로그 파일

고급 스크립트는 `test_log.txt` 파일에 테스트 실행 결과를 기록합니다:
```
2024-01-15 14:30:25 - Test Result: PASSED
2024-01-15 15:45:12 - Test Result: FAILED
```

## 🔄 자동화

### Windows 작업 스케줄러에 등록
1. 작업 스케줄러 열기
2. "기본 작업 만들기" 선택
3. 트리거 설정 (매일, 매주 등)
4. 동작에서 스크립트 경로 지정: `C:\path\to\your_program\scripts\run_tests.bat`

### CI/CD 파이프라인에서 사용
```yaml
# GitHub Actions 예시
- name: Run Tests
  run: |
    cd scripts
    ./run_tests.bat
```

## 💡 팁

1. **빠른 테스트**: 개발 중에는 `run_tests_simple.bat` 사용
2. **커버리지 확인**: 배포 전에 `run_tests_advanced.bat coverage` 실행
3. **문제 디버깅**: `run_tests_advanced.bat verbose`로 상세한 출력 확인
4. **대용량 테스트**: `run_tests_advanced.bat parallel`로 병렬 실행

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Python 버전: `python --version`
2. 가상환경 상태: `venv\Scripts\activate.bat`
3. pytest 설치: `pip list | findstr pytest`
4. 테스트 폴더 존재: `dir tests\` 