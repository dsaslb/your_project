# 🔧 신규 권한 추가 가이드

## 📋 1단계: 권한 상수에 추가

### `app_core.py` 파일에서 권한 상수 수정

```python
ALL_PERMISSIONS = [
    'order', 'schedule', 'clean', 'inventory', 'customer', 'reports', 'reservation', 'accounting',
    'marketing'  # 🆕 신규 권한 추가
]

PERMISSION_LABELS = {
    'order':'발주', 'schedule':'스케줄', 'clean':'청소', 'inventory':'재고', 'customer':'고객',
    'reports':'보고서', 'reservation':'예약', 'accounting':'정산', 'marketing':'마케팅'  # 🆕 라벨 추가
}
```

## 📋 2단계: 권한 관리 템플릿 자동 반영

### `templates/user_permissions.html`에서 반복문으로 표시

```html
{% for perm in ALL_PERMISSIONS %}
  <label>
    <input type="checkbox" name="perm_{{ perm }}" {% if perms[perm] %}checked{% endif %}>
    {{ PERMISSION_LABELS[perm] }}
  </label>
{% endfor %}
```

## 📋 3단계: 대시보드 메뉴 자동 추가

### `templates/dashboard.html`에서 권한별 메뉴 표시

```html
{% if perms.get('marketing', False) or user.role == 'admin' %}
    <a href="/marketing">📢 마케팅 관리</a>
{% endif %}
```

## 📋 4단계: 신규 기능 라우트 생성

### `app_core.py`에 라우트 추가

```python
@app.route('/marketing', methods=['GET', 'POST'])
@require_perm('marketing')
def marketing():
    """마케팅 관리"""
    if request.method == 'POST':
        # 마케팅 데이터 등록 로직
        campaign_name = request.form['campaign_name']
        budget = float(request.form['budget'])
        # Marketing 모델이 있다면 여기에 추가
        return redirect(url_for('marketing'))
    
    # 마케팅 조회 로직
    return render_template('marketing.html', message="마케팅 관리 기능이 구현되었습니다!")
```

## 📋 5단계: 템플릿 생성

### `templates/marketing.html` 생성

```html
<!DOCTYPE html>
<html>
<head>
    <title>마케팅 관리 - Core System</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #333; color: white; padding: 15px; margin-bottom: 20px; }
        .nav { background-color: #4CAF50; padding: 10px; margin-bottom: 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; padding: 8px 16px; border-radius: 5px; }
        .content { max-width: 800px; margin: 0 auto; }
        .feature-box { background-color: #e8f5e8; padding: 30px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .back-btn { background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📢 마케팅 관리</h1>
    </div>
    
    <div class="nav">
        <a href="/dashboard">🏠 대시보드</a>
        <a href="/marketing">📢 마케팅 관리</a>
    </div>
    
    <div class="content">
        <div class="feature-box">
            <h2>🎯 마케팅 관리 시스템</h2>
            <p>{{ message }}</p>
            <p>이 기능은 마케팅 관리 권한이 있는 사용자만 접근할 수 있습니다.</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/dashboard" class="back-btn">← 대시보드로 돌아가기</a>
        </div>
    </div>
</body>
</html>
```

## ✅ 완료!

이제 **마케팅** 권한이 완전히 추가되었습니다:

1. ✅ 권한 상수에 추가
2. ✅ 권한 관리 UI에 자동 반영
3. ✅ 대시보드 메뉴에 자동 추가
4. ✅ 라우트 권한 보호 적용
5. ✅ 템플릿 생성

## 🔄 다른 권한 추가하기

위 과정을 반복하여 새로운 권한을 추가할 수 있습니다:

- `'sales'` (영업)
- `'hr'` (인사)
- `'finance'` (재무)
- `'quality'` (품질관리)
- 등등...

## 📝 주의사항

- 권한 이름은 **소문자**로 작성
- 라벨은 **한글**로 작성
- 권한 변경 후 **재시작** 필요
- 기존 사용자의 권한은 **기본값 False**로 설정됨 