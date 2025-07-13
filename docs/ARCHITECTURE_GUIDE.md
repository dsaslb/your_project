# 🏗️ 시스템 아키텍처 가이드

## 📋 개요

이 문서는 **공통 데이터/모듈/스토어** 구조와 **계층별 승인/권한** 시스템, **업무간 데이터 연동/동기화**를 기반으로 한 확장 가능한 시스템 아키텍처를 설명합니다.

## 🎯 핵심 설계 원칙

### 1. **단일 진실 소스 (Single Source of Truth)**
- 모든 업무 데이터는 **공통 모델/서비스/API**에서만 관리
- 데이터 중복/불일치 방지를 위한 중앙 집중식 데이터 관리
- 프론트엔드 전역 스토어와 백엔드 공통 서비스 계층 연동

### 2. **계층별 권한 관리**
- **최고관리자 → 브랜드 관리자 → 매장 관리자 → 직원** 계층 구조
- JSON 기반 세밀한 권한 관리 (`User.permissions`)
- 권한 위임/회수 시스템으로 유연한 권한 관리

### 3. **실시간 데이터 동기화**
- 업무간 자동 연동 (발주→재고, 주문→재고 등)
- 실시간 알림 및 이벤트 스트리밍
- 오프라인 지원 및 데이터 동기화

## 🏛️ 시스템 구조

### 백엔드 구조

```
📁 api/
├── 📁 modules/           # 업무별 모듈
│   ├── automation.py     # 자동화 규칙
│   ├── notification_system.py  # 알림 시스템
│   └── reporting_system.py     # 리포트 시스템
├── staff.py              # 직원 관리 API
├── orders.py             # 주문 관리 API
├── inventory.py          # 재고 관리 API
├── schedule.py           # 스케줄 관리 API
└── realtime_monitoring.py # 실시간 모니터링

📁 models.py              # 공통 데이터 모델
├── User                  # 사용자/권한/승인
├── Branch                # 매장 정보
├── Brand                 # 브랜드 정보
├── Order                 # 주문 정보
├── InventoryItem         # 재고 정보
├── Attendance            # 근태 정보
├── Notification          # 알림 정보
└── AutomationRule        # 자동화 규칙

📁 utils/                 # 공통 유틸리티
├── assignee_manager.py   # 담당자 배정
├── dashboard.py          # 대시보드 통계
└── pay_transfer.py       # 결제/이체
```

### 프론트엔드 구조

```
📁 frontend/src/store/
├── index.ts              # 중앙 데이터 스토어
├── useUserStore.ts       # 사용자/권한 관리
├── useOrderStore.ts      # 주문 관리
├── useInventoryStore.ts  # 재고 관리
├── useStaffStore.ts      # 직원 관리
├── useScheduleStore.ts   # 스케줄 관리
└── useNotificationStore.ts # 알림 관리
```

## 🔐 권한 시스템

### 계층별 권한 구조

```typescript
interface User {
  role: 'admin' | 'brand_admin' | 'store_admin' | 'employee';
  permissions: {
    dashboard: { view: boolean, edit: boolean };
    brand_management: { view: boolean, create: boolean, edit: boolean, delete: boolean, approve: boolean };
    store_management: { view: boolean, create: boolean, edit: boolean, delete: boolean, approve: boolean };
    employee_management: { view: boolean, create: boolean, edit: boolean, delete: boolean, approve: boolean, assign_roles: boolean };
    schedule_management: { view: boolean, create: boolean, edit: boolean, delete: boolean, approve: boolean };
    order_management: { view: boolean, create: boolean, edit: boolean, delete: boolean, approve: boolean };
    inventory_management: { view: boolean, create: boolean, edit: boolean, delete: boolean };
    notification_management: { view: boolean, send: boolean, delete: boolean };
    system_management: { view: boolean, backup: boolean, restore: boolean, settings: boolean, monitoring: boolean };
    ai_management: { view: boolean, create: boolean, edit: boolean, delete: boolean, approve: boolean, monitor: boolean };
    reports: { view: boolean, export: boolean, admin_only: boolean };
  };
}
```

### 권한 검증 함수

```python
def has_permission(self, module, action):
    """특정 모듈의 특정 액션에 대한 권한 확인"""
    if not self.permissions:
        return False
    
    module_perms = self.permissions.get(module, {})
    
    # admin_only 체크
    if module_perms.get("admin_only", False) and self.role != "admin":
        return False
    
    # 특정 액션 권한 확인
    return module_perms.get(action, False)
```

## 🔄 데이터 연동 시스템

### 업무간 자동 연동

```python
# 발주 → 재고 자동 반영
def process_order(order_data):
    # 주문 처리
    order = create_order(order_data)
    
    # 재고 자동 차감
    for item in order.items:
        inventory_item = InventoryItem.query.get(item.inventory_id)
        inventory_item.current_stock -= item.quantity
        
        # 재고 부족 시 자동 알림
        if inventory_item.current_stock <= inventory_item.min_stock:
            send_low_stock_alert(inventory_item)
    
    # 실시간 업데이트 브로드캐스트
    broadcast_inventory_update()
```

### 자동화 규칙 시스템

```python
# 자동화 규칙 정의
automation_rule = {
    'name': '재고 부족 자동 알림',
    'trigger_type': 'threshold',
    'trigger_conditions': {
        'field': 'current_stock',
        'operator': 'less_than_or_equal',
        'value': 'min_stock'
    },
    'actions': [
        {
            'type': 'send_notification',
            'target': 'admin',
            'message': '재고 부족 알림'
        },
        {
            'type': 'update_inventory',
            'action': 'create_order_request'
        }
    ]
}
```

## 🚀 새로운 업무/권한/페이지 추가 가이드

### 1. 새로운 업무 모듈 추가

#### 백엔드 API 추가

```python
# api/new_module.py
from flask import Blueprint, request, jsonify
from models import NewModule, db
from api.gateway import token_required, role_required

new_module_bp = Blueprint('new_module', __name__)

@new_module_bp.route('/api/new-module', methods=['GET'])
@token_required
@role_required(['admin', 'manager'])
def get_new_module_data(current_user):
    """새로운 업무 데이터 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('new_module', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 데이터 조회
        data = NewModule.query.filter_by(branch_id=current_user.branch_id).all()
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in data]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### 데이터 모델 추가

```python
# models.py
class NewModule(db.Model):
    __tablename__ = "new_modules"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="active")
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    branch = db.relationship("Branch", backref="new_modules")
    creator = db.relationship("User", backref="created_new_modules")
```

#### 프론트엔드 스토어 추가

```typescript
// frontend/src/store/useNewModuleStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface NewModule {
  id: number;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  branchId: number;
  createdAt: string;
  updatedAt: string;
}

interface NewModuleStore {
  items: NewModule[];
  syncStatus: 'synced' | 'pending' | 'offline' | 'error';
  lastSync: string | null;
  
  fetchData: () => Promise<void>;
  addItem: (item: Omit<NewModule, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateItem: (id: number, updates: Partial<NewModule>) => void;
  removeItem: (id: number) => void;
  
  // 실시간 동기화
  subscribeToChanges: (callback: (items: NewModule[]) => void) => () => void;
  broadcastChange: (action: string, data?: any) => void;
}

export const useNewModuleStore = create<NewModuleStore>()(
  persist(
    (set, get) => ({
      items: [],
      syncStatus: 'synced',
      lastSync: null,
      
      fetchData: async () => {
        try {
          set({ syncStatus: 'pending' });
          const res = await fetch('/api/new-module');
          if (!res.ok) throw new Error('API 오류');
          const data: NewModule[] = await res.json();
          set({ items: data, syncStatus: 'synced', lastSync: new Date().toISOString() });
          
          // 실시간 동기화
          get().broadcastChange('data_loaded', { count: data.length });
        } catch (e) {
          set({ syncStatus: 'offline' });
        }
      },
      
      addItem: async (item) => {
        const newItem: NewModule = {
          ...item,
          id: Date.now(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        set((state) => ({
          items: [...state.items, newItem],
          syncStatus: 'pending',
        }));
        
        // 실시간 동기화
        get().broadcastChange('item_added', { item: newItem });
      },
      
      updateItem: async (id, updates) => {
        set((state) => ({
          items: state.items.map((item) =>
            item.id === id ? { ...item, ...updates, updatedAt: new Date().toISOString() } : item
          ),
          syncStatus: 'pending',
        }));
        
        // 실시간 동기화
        get().broadcastChange('item_updated', { id, updates });
      },
      
      removeItem: async (id) => {
        set((state) => ({
          items: state.items.filter((item) => item.id !== id),
          syncStatus: 'pending',
        }));
        
        // 실시간 동기화
        get().broadcastChange('item_removed', { id });
      },
      
      // 실시간 동기화 구현
      subscribeToChanges: (callback) => {
        const handleStorageChange = (e: StorageEvent) => {
          if (e.key === 'new-module-store') {
            try {
              const newState = JSON.parse(e.newValue || '{}');
              if (newState.items) {
                callback(newState.items);
              }
            } catch (error) {
              console.error('NewModule store state 파싱 오류:', error);
            }
          }
        };
        
        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
      },
      
      broadcastChange: (action, data) => {
        const broadcastData = {
          action,
          data,
          timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('new-module-store-broadcast', JSON.stringify(broadcastData));
        localStorage.removeItem('new-module-store-broadcast');
      },
    }),
    {
      name: 'new-module-store',
    }
  )
);
```

### 2. 새로운 권한 추가

#### 권한 정의 추가

```python
# models.py - User 클래스의 _get_default_permissions 메서드 수정
def _get_default_permissions(self):
    base_permissions = {
        # 기존 권한들...
        
        # 새로운 업무 권한 추가
        "new_module_management": {
            "view": False,
            "create": False,
            "edit": False,
            "delete": False,
            "approve": False,
        },
    }
    
    # 역할별 권한 설정
    if self.role == "admin":
        # 최고관리자: 모든 권한
        for module in base_permissions:
            for action in base_permissions[module]:
                base_permissions[module][action] = True
    elif self.role == "brand_admin":
        # 브랜드 관리자: 새로운 업무 권한 포함
        base_permissions["new_module_management"]["view"] = True
        base_permissions["new_module_management"]["create"] = True
        base_permissions["new_module_management"]["edit"] = True
        base_permissions["new_module_management"]["approve"] = True
    # ... 다른 역할들
    
    return base_permissions
```

#### 권한 검증 데코레이터 추가

```python
# api/gateway.py
def new_module_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_permission('new_module_management', 'view'):
            return jsonify({'error': '새로운 업무 접근 권한이 없습니다.'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 사용 예시
@new_module_bp.route('/api/new-module', methods=['POST'])
@token_required
@new_module_required
def create_new_module(current_user):
    # 새로운 업무 생성 로직
    pass
```

### 3. 새로운 페이지 추가

#### React 컴포넌트 추가

```typescript
// frontend/src/app/new-module/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useNewModuleStore } from '@/store/useNewModuleStore';
import { useUserStore } from '@/store/useUserStore';

export default function NewModulePage() {
  const { items, fetchData, addItem, updateItem, removeItem } = useNewModuleStore();
  const { user, hasRole } = useUserStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      await fetchData();
      setIsLoading(false);
    };
    loadData();
  }, [fetchData]);

  // 권한 확인
  const canCreate = hasRole(['admin', 'brand_admin', 'store_admin']);
  const canEdit = hasRole(['admin', 'brand_admin', 'store_admin']);
  const canDelete = hasRole(['admin', 'brand_admin']);

  if (isLoading) {
    return <div>로딩 중...</div>;
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">새로운 업무 관리</h1>
      
      {/* 권한에 따른 UI 표시 */}
      {canCreate && (
        <button 
          onClick={() => addItem({ name: '새 항목', description: '', status: 'active', branchId: user?.branchId || 0 })}
          className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
        >
          새 항목 추가
        </button>
      )}
      
      <div className="grid gap-4">
        {items.map((item) => (
          <div key={item.id} className="border p-4 rounded">
            <h3 className="font-semibold">{item.name}</h3>
            <p className="text-gray-600">{item.description}</p>
            <div className="flex gap-2 mt-2">
              {canEdit && (
                <button 
                  onClick={() => updateItem(item.id, { status: item.status === 'active' ? 'inactive' : 'active' })}
                  className="bg-yellow-500 text-white px-2 py-1 rounded text-sm"
                >
                  상태 변경
                </button>
              )}
              {canDelete && (
                <button 
                  onClick={() => removeItem(item.id)}
                  className="bg-red-500 text-white px-2 py-1 rounded text-sm"
                >
                  삭제
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 4. 자동화 규칙 추가

```python
# 새로운 업무 자동화 규칙 추가
def create_new_module_automation_rules():
    """새로운 업무 관련 자동화 규칙 생성"""
    
    # 규칙 1: 새로운 업무 생성 시 알림
    rule1 = AutomationRule(
        name='새로운 업무 생성 알림',
        trigger_type='event',
        trigger_config={
            'event_type': 'new_module_created',
            'conditions': {}
        },
        action_type='notification',
        action_config={
            'target': 'admin',
            'message': '새로운 업무가 생성되었습니다.',
            'priority': 'normal'
        },
        is_active=True
    )
    
    # 규칙 2: 새로운 업무 상태 변경 시 처리
    rule2 = AutomationRule(
        name='새로운 업무 상태 변경 처리',
        trigger_type='data_change',
        trigger_config={
            'table': 'new_modules',
            'field': 'status',
            'conditions': {
                'old_value': 'active',
                'new_value': 'inactive'
            }
        },
        action_type='workflow',
        action_config={
            'workflow_type': 'status_change_notification',
            'recipients': ['manager', 'admin']
        },
        is_active=True
    )
    
    db.session.add_all([rule1, rule2])
    db.session.commit()
```

## 📊 데이터 흐름

### 1. 데이터 생성 흐름

```
사용자 액션 → 프론트엔드 스토어 → API 호출 → 데이터베이스 저장 → 실시간 브로드캐스트 → 다른 페이지 자동 업데이트
```

### 2. 권한 검증 흐름

```
API 요청 → 토큰 검증 → 사용자 정보 조회 → 권한 확인 → 업무별 권한 검증 → 응답 반환
```

### 3. 실시간 동기화 흐름

```
데이터 변경 → 이벤트 발생 → 자동화 규칙 실행 → 알림 발송 → 실시간 브로드캐스트 → 모든 클라이언트 업데이트
```

## 🔧 확장성 보장

### 1. 모듈화된 구조
- 각 업무는 독립적인 모듈로 구성
- 공통 인터페이스를 통한 일관된 데이터 접근
- 플러그인 방식의 기능 확장

### 2. 설정 기반 권한 관리
- JSON 기반 권한 설정으로 유연한 권한 관리
- 새로운 권한 추가 시 코드 변경 최소화
- 역할별 권한 템플릿 시스템

### 3. 이벤트 기반 아키텍처
- 이벤트 드리븐 아키텍처로 느슨한 결합
- 새로운 기능 추가 시 기존 코드 영향 최소화
- 확장 가능한 알림 및 자동화 시스템

## 📝 모범 사례

### 1. 새로운 기능 추가 시 체크리스트
- [ ] 데이터 모델 정의 및 마이그레이션
- [ ] API 엔드포인트 구현
- [ ] 권한 설정 추가
- [ ] 프론트엔드 스토어 구현
- [ ] UI 컴포넌트 개발
- [ ] 자동화 규칙 정의
- [ ] 테스트 코드 작성
- [ ] 문서 업데이트

### 2. 권한 관리 모범 사례
- 최소 권한 원칙 적용
- 역할 기반 권한 관리
- 권한 위임/회수 기능 제공
- 권한 변경 이력 추적

### 3. 데이터 일관성 보장
- 트랜잭션 기반 데이터 처리
- 실시간 동기화 메커니즘
- 오프라인 지원 및 충돌 해결
- 데이터 무결성 검증

## 🚨 주의사항

1. **데이터 중복 금지**: 모든 데이터는 공통 모델에서만 관리
2. **권한 검증 필수**: 모든 API 엔드포인트에서 권한 검증 수행
3. **실시간 동기화**: 데이터 변경 시 반드시 실시간 브로드캐스트
4. **확장성 고려**: 새로운 기능 추가 시 기존 구조 활용
5. **문서화**: 모든 변경사항은 문서에 반영

---

이 가이드를 따라 새로운 업무/권한/페이지를 추가하면, 기존 시스템과 완벽하게 연동되고 일관성을 유지할 수 있습니다. 