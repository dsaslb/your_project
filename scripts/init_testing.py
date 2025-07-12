#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플러그인 테스트/모니터링/문서화 시스템 초기화 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.backend.plugin_testing_system import PluginTestingSystem

def init_testing_system():
    """테스트 시스템 초기화"""
    print("🔧 플러그인 테스트/모니터링/문서화 시스템 초기화 중...")
    
    try:
        # 테스트 시스템 초기화
        testing_system = PluginTestingSystem()
        print("✅ 테스트 시스템이 초기화되었습니다")
        
        # 샘플 테스트 데이터 생성
        create_sample_test_data(testing_system)
        
        # 샘플 성능 데이터 생성
        create_sample_performance_data(testing_system)
        
        # 샘플 문서 데이터 생성
        create_sample_documentation_data(testing_system)
        
        print("✅ 모든 테스트 데이터가 생성되었습니다")
        
    except Exception as e:
        print(f"❌ 테스트 시스템 초기화 실패: {e}")
        return False
    
    return True

def create_sample_test_data(testing_system):
    """샘플 테스트 데이터 생성"""
    print("📊 샘플 테스트 데이터 생성 중...")
    
    sample_test_results = [
        {
            "plugin_id": "your_program_management",
            "test_type": "all",
            "started_at": "2024-01-15T10:00:00",
            "completed_at": "2024-01-15T10:05:00",
            "total_tests": 15,
            "passed_tests": 14,
            "failed_tests": 1,
            "status": "passed",
            "results": [
                {
                    "test_id": "your_program_management_unit_1705310400",
                    "plugin_id": "your_program_management",
                    "test_type": "unit",
                    "status": "passed",
                    "duration": 2.5,
                    "message": "단위 테스트 통과",
                    "details": {
                        "stdout": "test_your_program_management.py::test_basic_functionality PASSED",
                        "stderr": "",
                        "return_code": 0
                    },
                    "created_at": "2024-01-15T10:00:30"
                },
                {
                    "test_id": "your_program_management_integration_1705310400",
                    "plugin_id": "your_program_management",
                    "test_type": "integration",
                    "status": "passed",
                    "duration": 8.2,
                    "message": "통합 테스트 통과",
                    "details": {
                        "stdout": "test_integration.py::test_api_endpoints PASSED",
                        "stderr": "",
                        "return_code": 0
                    },
                    "created_at": "2024-01-15T10:01:00"
                },
                {
                    "test_id": "your_program_management_performance_1705310400",
                    "plugin_id": "your_program_management",
                    "test_type": "performance",
                    "status": "failed",
                    "duration": 15.0,
                    "message": "성능 테스트 실패 - 응답 시간 초과",
                    "details": {
                        "stdout": "test_performance.py::test_response_time FAILED",
                        "stderr": "AssertionError: Response time 1200ms exceeds limit of 1000ms",
                        "return_code": 1
                    },
                    "created_at": "2024-01-15T10:02:00"
                }
            ]
        },
        {
            "plugin_id": "inventory_management",
            "test_type": "unit",
            "started_at": "2024-01-15T09:30:00",
            "completed_at": "2024-01-15T09:32:00",
            "total_tests": 8,
            "passed_tests": 8,
            "failed_tests": 0,
            "status": "passed",
            "results": [
                {
                    "test_id": "inventory_management_unit_1705307400",
                    "plugin_id": "inventory_management",
                    "test_type": "unit",
                    "status": "passed",
                    "duration": 1.8,
                    "message": "단위 테스트 통과",
                    "details": {
                        "stdout": "test_inventory.py::test_stock_management PASSED",
                        "stderr": "",
                        "return_code": 0
                    },
                    "created_at": "2024-01-15T09:30:30"
                }
            ]
        }
    ]
    
    # 테스트 결과 저장
    for result in sample_test_results:
        testing_system._save_test_result(result)
    
    print(f"✅ {len(sample_test_results)}개의 샘플 테스트 결과가 생성되었습니다")

def create_sample_performance_data(testing_system):
    """샘플 성능 데이터 생성"""
    print("📈 샘플 성능 데이터 생성 중...")
    
    import random
    from datetime import datetime, timedelta
    
    sample_metrics = []
    base_time = datetime.now() - timedelta(hours=24)
    
    plugin_ids = ["your_program_management", "inventory_management", "order_management"]
    
    for i in range(24):  # 24시간 데이터
        timestamp = base_time + timedelta(hours=i)
        
        for plugin_id in plugin_ids:
            metric = {
                "plugin_id": plugin_id,
                "cpu_usage": random.uniform(5.0, 25.0),
                "memory_usage": random.uniform(10.0, 40.0),
                "response_time": random.uniform(50.0, 300.0),
                "throughput": random.uniform(80.0, 120.0),
                "error_rate": random.uniform(0.0, 2.0),
                "timestamp": timestamp.isoformat()
            }
            sample_metrics.append(metric)
    
    # 성능 메트릭 저장
    testing_system._save_performance_metrics(sample_metrics)
    
    print(f"✅ {len(sample_metrics)}개의 샘플 성능 메트릭이 생성되었습니다")

def create_sample_documentation_data(testing_system):
    """샘플 문서 데이터 생성"""
    print("📚 샘플 문서 데이터 생성 중...")
    
    sample_documentation = {
        "your_program_management": {
            "plugin_id": "your_program_management",
            "api_docs": {
                "endpoints": [
                    {
                        "file": "main.py",
                        "routes": [
                            {
                                "line": 15,
                                "route": "@bp.route('/dashboard')",
                                "method": "GET"
                            },
                            {
                                "line": 25,
                                "route": "@bp.route('/orders', methods=['GET', 'POST'])",
                                "method": "GET,POST"
                            }
                        ]
                    }
                ],
                "models": [],
                "examples": []
            },
            "user_guide": """# 레스토랑 관리 플러그인 사용자 가이드

## 개요
레스토랑 관리 플러그인은 음식점의 전반적인 운영을 관리할 수 있는 종합적인 솔루션입니다.

## 설치
1. 플러그인을 다운로드합니다.
2. 플러그인 디렉토리에 설치합니다.
3. 플러그인을 활성화합니다.

## 설정
플러그인 설정은 관리자 패널에서 할 수 있습니다.

## 사용법
자세한 사용법은 플러그인 문서를 참조하세요.
""",
            "developer_guide": """# 레스토랑 관리 플러그인 개발자 가이드

## 구조
```
your_program_management/
├── backend/          # 백엔드 코드
├── config/           # 설정 파일
├── templates/        # 템플릿 파일
└── static/          # 정적 파일
```

## 의존성
Flask, SQLAlchemy, Jinja2

## 권한
admin, manager, staff

## API
플러그인 API는 백엔드 디렉토리의 Python 파일에 정의되어 있습니다.
""",
            "changelog": [
                {
                    "version": "1.0.0",
                    "date": "2024-01-15T00:00:00",
                    "changes": ["초기 버전", "기본 레스토랑 관리 기능", "주문 관리 시스템"]
                },
                {
                    "version": "1.1.0",
                    "date": "2024-01-20T00:00:00",
                    "changes": ["성능 개선", "UI/UX 개선", "버그 수정"]
                }
            ],
            "examples": [
                {
                    "file": "example_usage.py",
                    "description": "기본 사용법 예제",
                    "code": """# 레스토랑 관리 플러그인 사용 예제
from your_program_management import RestaurantManager

# 매니저 초기화
manager = RestaurantManager()

# 주문 생성
order = manager.create_order({
    'table': 5,
    'items': ['파스타', '샐러드'],
    'total': 25000
})

print(f"주문이 생성되었습니다: {order.id}")
"""
                }
            ],
            "last_updated": "2024-01-15T12:00:00"
        },
        "inventory_management": {
            "plugin_id": "inventory_management",
            "api_docs": {
                "endpoints": [
                    {
                        "file": "inventory.py",
                        "routes": [
                            {
                                "line": 10,
                                "route": "@bp.route('/inventory')",
                                "method": "GET"
                            }
                        ]
                    }
                ],
                "models": [],
                "examples": []
            },
            "user_guide": """# 재고 관리 플러그인 사용자 가이드

## 개요
재고 관리 플러그인은 레스토랑의 재고를 효율적으로 관리할 수 있는 도구입니다.

## 설치 및 설정
관리자 패널에서 플러그인을 활성화하세요.

## 사용법
재고 현황을 실시간으로 확인하고 관리할 수 있습니다.
""",
            "developer_guide": """# 재고 관리 플러그인 개발자 가이드

## 구조
```
inventory_management/
├── backend/
├── config/
└── templates/
```

## 의존성
Flask, SQLAlchemy

## 권한
admin, manager
""",
            "changelog": [
                {
                    "version": "1.0.0",
                    "date": "2024-01-10T00:00:00",
                    "changes": ["초기 버전", "기본 재고 관리 기능"]
                }
            ],
            "examples": [],
            "last_updated": "2024-01-10T12:00:00"
        }
    }
    
    # 문서 저장
    for plugin_id, doc in sample_documentation.items():
        testing_system._save_documentation(plugin_id, doc)
    
    print(f"✅ {len(sample_documentation)}개의 샘플 문서가 생성되었습니다")

def main():
    """메인 함수"""
    print("🚀 플러그인 테스트/모니터링/문서화 시스템 초기화를 시작합니다...")
    
    success = init_testing_system()
    
    if success:
        print("\n🎉 플러그인 테스트/모니터링/문서화 시스템 초기화가 완료되었습니다!")
        print("\n📋 다음 기능들을 사용할 수 있습니다:")
        print("  • 플러그인 테스트 실행 및 결과 확인")
        print("  • 성능 모니터링 및 알림")
        print("  • 자동 문서 생성 및 관리")
        print("  • 테스트 커버리지 분석")
        print("\n🔗 API 엔드포인트:")
        print("  • POST /api/plugins/{plugin_id}/test - 테스트 실행")
        print("  • GET /api/plugins/test-results - 테스트 결과 조회")
        print("  • POST /api/plugins/monitoring/start - 모니터링 시작")
        print("  • POST /api/plugins/monitoring/stop - 모니터링 중지")
        print("  • GET /api/plugins/performance - 성능 메트릭 조회")
        print("  • POST /api/plugins/{plugin_id}/documentation - 문서 생성")
        print("  • GET /api/plugins/{plugin_id}/documentation - 문서 조회")
    else:
        print("\n❌ 플러그인 테스트/모니터링/문서화 시스템 초기화에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
