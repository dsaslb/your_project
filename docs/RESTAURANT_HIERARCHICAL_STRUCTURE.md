# 🏗️ 레스토랑 업종 계층적 구조

## 📋 구조 개요

레스토랑 업종은 다음과 같은 계층적 구조로 구성됩니다:

```
레스토랑 업종 (Industry)
├── 브랜드별 페이지 (Brand)
│   ├── 스타벅스
│   ├── 맥도날드
│   ├── KFC
│   └── 기타 브랜드
├── 매장별 페이지 (Branch)
│   ├── 강남점
│   ├── 홍대점
│   └── 기타 매장
└── 직원별 페이지 (Staff)
    ├── 매장 관리자
    ├── 주방장
    ├── 서버
    └── 캐셔
```

## 🎯 각 계층별 특징

### 1. 업종 레벨 (Industry Level)
- **접근 권한**: 전체 관리자, 업종 관리자
- **주요 기능**: 
  - 전체 업종 현황 파악
  - 브랜드별 성과 비교
  - 업종 트렌드 분석
  - 전체 매출/주문 통계

### 2. 브랜드 레벨 (Brand Level)
- **접근 권한**: 브랜드 관리자, 업종 관리자
- **주요 기능**:
  - 브랜드별 현황 관리
  - 소속 매장 목록 및 성과
  - 브랜드 트렌드 분석
  - 브랜드별 매출/주문 통계

### 3. 매장 레벨 (Branch Level)
- **접근 권한**: 매장 관리자, 해당 매장 직원
- **주요 기능**:
  - 매장별 실시간 현황
  - 직원 관리 및 스케줄
  - 재고 관리
  - 주문 처리 현황

### 4. 직원 레벨 (Staff Level)
- **접근 권한**: 본인, 매장 관리자
- **주요 기능**:
  - 개인 성과 현황
  - 스케줄 확인
  - 처리 주문 내역
  - 개인 통계

## 🔗 라우트 구조

### 업종 레벨
```
/restaurant/industry/dashboard
```

### 브랜드 레벨
```
/restaurant/brand/{brand_id}/dashboard
```

### 매장 레벨
```
/restaurant/branch/{branch_id}/dashboard
```

### 직원 레벨
```
/restaurant/staff/{staff_id}/dashboard
```

## 📊 데이터 필터링

### 권한 기반 데이터 접근
- **업종 관리자**: 모든 브랜드, 매장, 직원 데이터 접근
- **브랜드 관리자**: 해당 브랜드 소속 매장/직원 데이터만 접근
- **매장 관리자**: 해당 매장 데이터만 접근
- **일반 직원**: 본인 데이터만 접근

### 데이터 보안
```python
# 예시: 매장별 데이터 접근 제어
def get_branch_stats(branch_id):
    # 사용자 권한 확인
    user_branch = current_user.staff.branch_id if current_user.staff else None
    
    # 관리자가 아닌 경우 자신의 매장만 접근 가능
    if current_user.role not in ['admin', 'super_admin'] and user_branch != branch_id:
        return {'error': '권한 없음'}
    
    # 권한이 있는 경우에만 데이터 반환
    return fetch_branch_data(branch_id)
```

## 🎨 UI/UX 특징

### 네비게이션 구조
- **브레드크럼**: 현재 위치 표시
- **상위 레벨 링크**: 상위 계층으로 이동
- **하위 레벨 링크**: 하위 계층으로 이동

### 반응형 디자인
- **데스크톱**: 전체 계층 구조 표시
- **모바일**: 탭 기반 네비게이션

## 🔧 구현 세부사항

### 모델 관계
```python
class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branches = db.relationship('Branch', backref='brand', lazy=True)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    staff = db.relationship('Staff', backref='branch', lazy=True)

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    position = db.Column(db.String(50), nullable=False)
```

### 권한 체크 함수
```python
def check_hierarchical_access(user, target_level, target_id):
    """계층적 접근 권한 확인"""
    if user.role in ['admin', 'super_admin']:
        return True
    
    if target_level == 'brand':
        # 브랜드 관리자 권한 확인
        return user.brand_id == target_id if hasattr(user, 'brand_id') else False
    
    elif target_level == 'branch':
        # 매장 관리자 권한 확인
        return user.staff.branch_id == target_id if user.staff else False
    
    elif target_level == 'staff':
        # 직원 본인 또는 매장 관리자 권한 확인
        return user.staff.id == target_id if user.staff else False
    
    return False
```

## 📈 성능 최적화

### 데이터베이스 쿼리 최적화
- **인덱스**: brand_id, branch_id, staff_id에 인덱스 설정
- **조인 최적화**: 필요한 테이블만 조인
- **캐싱**: 자주 조회되는 통계 데이터 캐싱

### 프론트엔드 최적화
- **지연 로딩**: 하위 계층 데이터는 필요시 로딩
- **페이지네이션**: 대량 데이터 처리
- **실시간 업데이트**: WebSocket을 통한 실시간 데이터

## 🔒 보안 고려사항

### 데이터 격리
- 각 계층별 데이터 완전 격리
- 상위 계층에서 하위 계층 데이터 접근 제한
- API 엔드포인트별 권한 검증

### 감사 로그
- 모든 데이터 접근 로그 기록
- 권한 변경 이력 추적
- 데이터 수정 이력 관리

## 🚀 확장 가능성

### 새로운 계층 추가
- **지역별**: 시/도/구 단위 그룹핑
- **업태별**: 패스트푸드/카페/레스토랑 분류
- **규모별**: 대형/중형/소형 매장 분류

### 기능 확장
- **크로스 브랜드 분석**: 브랜드 간 비교 분석
- **체인 관리**: 프랜차이즈 체인 관리
- **공급망 관리**: 원재료 공급업체 관리

## 📝 사용 예시

### 업종 관리자
1. 업종 대시보드에서 전체 현황 확인
2. 브랜드별 성과 비교 분석
3. 문제가 있는 브랜드/매장 식별
4. 업종 전체 전략 수립

### 브랜드 관리자
1. 브랜드 대시보드에서 소속 매장 현황 확인
2. 매장별 성과 비교 및 개선점 도출
3. 브랜드 전략 실행 및 모니터링

### 매장 관리자
1. 매장 대시보드에서 실시간 현황 확인
2. 직원 스케줄 및 성과 관리
3. 재고 및 주문 처리 현황 모니터링

### 일반 직원
1. 개인 대시보드에서 본인 성과 확인
2. 스케줄 및 업무 현황 파악
3. 개인 목표 달성도 추적

---

**🏗️ 레스토랑 업종 계층적 구조** - 체계적이고 효율적인 레스토랑 관리 시스템 