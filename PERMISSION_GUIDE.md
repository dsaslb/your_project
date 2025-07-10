# Your Program 권한 관리 가이드

## 개요
Your Program은 **User.permissions (JSON 기반)** 권한 시스템을 사용하여 세밀한 권한 관리를 제공합니다.

## 권한 시스템 구조

### 1. 사용자 역할 (User.role)
- `super_admin`: 최고관리자 (모든 권한)
- `admin`: 관리자 (브랜드/매장 관리 권한)
- `brand_manager`: 브랜드 매니저 (해당 브랜드만 관리)
- `store_manager`: 매장 관리자 (해당 매장만 관리)
- `manager`: 팀장 (제한된 관리 권한)
- `employee`: 직원 (기본 업무 권한)

### 2. 권한 모듈 (User.permissions)
각 사용자는 JSON 형태의 permissions 필드를 가지며, 다음과 같은 모듈별 권한을 가집니다:

```json
{
  "dashboard": {"view": true, "edit": false, "admin_only": false},
  "brand_management": {"view": false, "create": false, "edit": false, "delete": false, "approve": false, "monitor": false},
  "store_management": {"view": false, "create": false, "edit": false, "delete": false, "approve": false, "monitor": false},
  "employee_management": {"view": false, "create": false, "edit": false, "delete": false, "approve": false, "assign_roles": false},
  "schedule_management": {"view": false, "create": false, "edit": false, "delete": false, "approve": false},
  "order_management": {"view": false, "create": false, "edit": false, "delete": false, "approve": false},
  "inventory_management": {"view": false, "create": false, "edit": false, "delete": false},
  "notification_management": {"view": false, "send": false, "delete": false},
  "system_management": {"view": false, "backup": false, "restore": false, "settings": false, "monitoring": false},
  "ai_management": {"view": false, "create": false, "edit": false, "delete": false, "approve": false, "monitor": false},
  "reports": {"view": false, "export": false, "admin_only": false}
}
```

### 3. 권한 액션
- `view`: 조회 권한
- `create`: 생성 권한
- `edit`: 편집 권한
- `delete`: 삭제 권한
- `approve`: 승인 권한
- `assign_roles`: 권한 부여 권한
- `monitor`: 모니터링 권한
- `admin_only`: 관리자 전용 권한

## 권한 확인 방법

### 1. Python 코드에서 권한 확인
```python
# 특정 모듈의 특정 액션 권한 확인
if current_user.has_permission("employee_management", "create"):
    # 직원 생성 로직
    pass

# 모듈 접근 권한 확인
if current_user.can_access_module("dashboard"):
    # 대시보드 접근 로직
    pass

# 편집 권한 확인
if current_user.can_edit_module("schedule_management"):
    # 스케줄 편집 로직
    pass
```

### 2. 템플릿에서 권한 확인
```html
{% if current_user.has_permission("employee_management", "create") %}
    <button class="btn btn-primary">직원 추가</button>
{% endif %}

{% if current_user.can_access_module("reports") %}
    <li><a href="{{ url_for('admin_reports.reports_stats') }}">보고서</a></li>
{% endif %}
```

### 3. 데코레이터를 사용한 권한 제어
```python
from utils.decorators import require_permission

@admin_reports_bp.route("/admin/employees")
@login_required
@require_permission("employee_management", "view")
def manage_employees():
    # 직원 관리 페이지
    pass

@admin_reports_bp.route("/admin/employees/create", methods=["POST"])
@login_required
@require_permission("employee_management", "create")
def create_employee():
    # 직원 생성 로직
    pass
```

## 권한 관리

### 1. 권한 설정
```python
# 사용자 권한 설정
user = User.query.get(user_id)
user.permissions = {
    "dashboard": {"view": True, "edit": False},
    "employee_management": {"view": True, "create": True, "edit": True},
    "schedule_management": {"view": True, "create": True, "edit": True}
}
db.session.commit()
```

### 2. 권한 위임
```python
# 권한 위임 (최고관리자가 매장관리자에게)
admin_user.delegate_permissions(
    target_user=store_manager,
    permissions={"schedule_management": {"view": True, "create": True}},
    expires_in_days=30
)
```

### 3. 권한 회수
```python
# 위임된 권한 회수
admin_user.revoke_delegated_permissions(store_manager)
```

## 권한별 메뉴 접근

### 1. 최고관리자 (super_admin)
- 모든 메뉴 접근 가능
- 시스템 전체 설정
- 브랜드/매장 관리
- 권한 관리

### 2. 관리자 (admin)
- 브랜드/매장 관리
- 직원 관리
- 스케줄/발주/재고 관리
- 보고서 및 모니터링

### 3. 브랜드 매니저 (brand_manager)
- 해당 브랜드의 매장들만 관리
- 직원 관리
- 스케줄/발주/재고 관리

### 4. 매장 관리자 (store_manager)
- 해당 매장만 관리
- 직원 관리
- 스케줄/발주/재고 관리

### 5. 팀장 (manager)
- 제한된 관리 권한
- 스케줄/발주/재고 관리

### 6. 직원 (employee)
- 기본 업무 권한
- 스케줄 조회
- 발주 생성

## 보안 고려사항

### 1. 권한 검증
- 모든 API 엔드포인트에서 권한 검증 필수
- 프론트엔드와 백엔드 모두에서 권한 확인
- 세션 기반 권한 캐싱 활용

### 2. 권한 로깅
- 권한 변경 시 로그 기록
- 권한 위임/회수 시 알림 발송
- 정기적인 권한 감사

### 3. 기본 권한
- 새 사용자 생성 시 역할별 기본 권한 자동 설정
- 최소 권한 원칙 적용
- 필요시에만 권한 추가

## 문제 해결

### 1. 권한 확인 실패
```python
# 권한 요약 정보 확인
summary = current_user.get_permission_summary()
print(f"사용자 권한: {summary}")

# 실제 적용되는 권한 확인
effective_perms = current_user.get_effective_permissions()
print(f"실제 권한: {effective_perms}")
```

### 2. 권한 위임 만료 확인
```python
if current_user.is_delegation_expired():
    # 기본 권한으로 복원
    current_user.permissions = current_user._get_default_permissions()
    db.session.commit()
```

### 3. 권한 디버깅
```python
# 권한 체크 로그 활성화
import logging
logging.getLogger('permissions').setLevel(logging.DEBUG)
```

## 최적화된 권한 시스템의 장점

1. **성능 향상**: 불필요한 테이블 조인 제거
2. **유연성**: JSON 기반으로 동적 권한 관리
3. **확장성**: 새로운 권한 모듈 쉽게 추가
4. **보안성**: 세밀한 권한 제어
5. **유지보수성**: 단순한 구조로 관리 용이

---

**최종 업데이트**: 2025-07-10
**버전**: 2.0 (User.permissions 기반) 