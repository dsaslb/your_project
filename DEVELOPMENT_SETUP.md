# 개발 환경 설정 가이드 (Python 3.13)

## 환경 정보
- **Python 버전**: 3.13.5
- **가상환경**: venv (Python 3.13 기반)
- **주요 프레임워크**: Flask 2.3.3

## 초기 설정

### 1. 가상환경 활성화
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. VSCode 설정
- VSCode에서 `Ctrl+Shift+P` → "Python: Select Interpreter"
- `./venv/Scripts/python.exe` 선택

## 개발 서버 실행

### Flask 서버 (백엔드)
```bash
python app.py
```

### Next.js 서버 (프론트엔드)
```bash
cd restaurant_frontend
npm run dev
```

## 주요 패키지
- Flask 2.3.3 - 웹 프레임워크
- Flask-Login 0.6.3 - 사용자 인증
- SQLAlchemy 2.0.41 - 데이터베이스 ORM
- pandas 2.3.0 - 데이터 분석
- click 8.1.7 - CLI 도구

## 문제 해결

### Import 오류 발생 시
1. 가상환경이 활성화되어 있는지 확인
2. VSCode에서 올바른 Python 인터프리터 선택
3. `pip install -r requirements.txt` 재실행

### VSCode/Pylance 오류 시
1. VSCode 재시작
2. Python 확장 재로드 (`Ctrl+Shift+P` → "Python: Reload Window")
3. Python 인터프리터 재선택

## 배포 환경
- **Python**: 3.13.5
- **가상환경**: 필수
- **패키지**: requirements.txt 기준 