# 중복 라우트 문제 해결 가이드

## 문제 상황
`app.py`에서 `notice_hide` 라우트가 중복으로 정의되어 서버 실행 시 오류가 발생합니다.

## 해결 방법

### 1. 중복 라우트 찾기
`app.py` 파일에서 다음 패턴을 검색하세요:
```python
@app.route('/notice/hide/<int:notice_id>', methods=['POST'])
@owner_or_admin(lambda notice_id: Notice.query.get_or_404(notice_id))
def notice_hide(notice_id):
```

### 2. 중복 제거
- 첫 번째 `notice_hide` 함수는 유지
- 두 번째 이후의 중복된 `notice_hide` 함수들을 모두 삭제

### 3. 확인할 중복 라우트들
다음 라우트들이 중복될 수 있습니다:
- `/notice/hide/<int:notice_id>`
- `/notice/restore/<int:notice_id>`
- `/notice/report/<int:notice_id>`

### 4. 수정 후 확인
```bash
python app.py
```

## CSRF 보호 추가

### 1. Flask-WTF 설치
```bash
pip install Flask-WTF
```

### 2. app.py에 추가
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

### 3. 템플릿에 CSRF 토큰 추가
모든 POST 폼에 다음을 추가:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

## 완료 후 테스트
1. 서버 실행: `python app.py`
2. 브라우저에서 접속 확인
3. 공지사항 기능 테스트 