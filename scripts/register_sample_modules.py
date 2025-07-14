#!/usr/bin/env python3
"""
샘플 모듈 마켓플레이스 등록 스크립트
"""

import sys
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_module_package(module_dir: Path, module_id: str) -> Optional[Path]:
    """모듈 패키지 생성"""
    try:
        # ZIP 파일 생성
        zip_path = Path(f"sample_modules/{module_id}_v1.0.0.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in module_dir.rglob('*'):
                if file_path.is_file():
                    # 상대 경로로 압축
                    arcname = file_path.relative_to(module_dir)
                    zipf.write(file_path, arcname)
        
        print(f"  ✅ {module_id} 패키지 생성 완료: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"  ❌ {module_id} 패키지 생성 실패: {e}")
        return None

def register_sample_modules():
    """샘플 모듈 등록"""
    print("📦 샘플 모듈 마켓플레이스 등록 시작...")
    
    # 샘플 모듈 정보
    sample_modules = [
        {
            'module_id': 'attendance_management',
            'name': '출근 관리 모듈',
            'description': '직원 출근/퇴근 관리, 근무 시간 추적, 출근 통계를 제공하는 모듈입니다.',
            'author': 'Your Program Team',
            'category': 'attendance',
            'version': '1.0.0',
            'tags': ['attendance', 'employee', 'time-tracking'],
            'compatibility': ['restaurant', 'retail', 'service'],
            'features': [
                '출근/퇴근 기록',
                '근무 시간 계산',
                '출근 통계 대시보드',
                '지각/조퇴 관리',
                '근무 일정 관리'
            ]
        },
        {
            'module_id': 'schedule_module',
            'name': '일정 관리 모듈',
            'description': '직원 근무 일정 관리, 교대 근무, 휴가 관리 기능을 제공하는 모듈입니다.',
            'author': 'Your Program Team',
            'category': 'schedule',
            'version': '1.0.0',
            'tags': ['schedule', 'shift', 'vacation'],
            'compatibility': ['restaurant', 'retail', 'service'],
            'features': [
                '근무 일정 생성',
                '교대 근무 관리',
                '휴가 신청/승인',
                '일정 충돌 검사',
                '일정 알림 기능'
            ]
        },
        {
            'module_id': 'inventory_module',
            'name': '재고 관리 모듈',
            'description': '상품 재고 관리, 입출고 추적, 재고 알림 기능을 제공하는 모듈입니다.',
            'author': 'Your Program Team',
            'category': 'inventory',
            'version': '1.0.0',
            'tags': ['inventory', 'stock', 'warehouse'],
            'compatibility': ['restaurant', 'retail', 'manufacturing'],
            'features': [
                '재고 현황 관리',
                '입출고 기록',
                '재고 알림',
                '재고 분석',
                '자동 발주 기능'
            ]
        },
        {
            'module_id': 'purchase_module',
            'name': '구매 관리 모듈',
            'description': '구매 요청, 승인, 발주, 입고 관리 기능을 제공하는 모듈입니다.',
            'author': 'Your Program Team',
            'category': 'purchase',
            'version': '1.0.0',
            'tags': ['purchase', 'procurement', 'order'],
            'compatibility': ['restaurant', 'retail', 'manufacturing'],
            'features': [
                '구매 요청 관리',
                '구매 승인 워크플로우',
                '발주서 생성',
                '입고 관리',
                '구매 분석'
            ]
        },
        {
            'module_id': 'ai_analysis_module',
            'name': 'AI 분석 모듈',
            'description': '머신러닝을 활용한 데이터 분석, 예측, 인사이트 제공 모듈입니다.',
            'author': 'Your Program Team',
            'category': 'analytics',
            'version': '1.0.0',
            'tags': ['ai', 'analytics', 'prediction', 'ml'],
            'compatibility': ['restaurant', 'retail', 'service', 'manufacturing'],
            'features': [
                '매출 예측',
                '고객 행동 분석',
                '재고 최적화',
                '인력 계획',
                '실시간 대시보드'
            ]
        }
    ]
    
    # 모듈 등록
    registered_modules = []
    for module_info in sample_modules:
        module_id = module_info['module_id']
        module_dir = Path(f"sample_modules/{module_id}")
        
        if not module_dir.exists():
            print(f"  ⚠️  {module_id} 디렉토리가 존재하지 않습니다. 건너뜁니다.")
            continue
        
        # 모듈 패키지 생성
        package_path = create_module_package(module_dir, module_id)
        if not package_path:
            continue
        
        # 마켓플레이스에 등록
        try:
            # 마켓플레이스 시스템 import
            from core.backend.plugin_marketplace_system import marketplace
            
            # 메타데이터 준비
            metadata = {
                'plugin_id': module_id,
                'name': module_info['name'],
                'description': module_info['description'],
                'author': module_info['author'],
                'version': module_info['version'],
                'category': module_info['category'],
                'tags': module_info['tags'],
                'compatibility': module_info['compatibility'],
                'features': module_info['features'],
                'license': 'MIT',
                'homepage': 'https://your-program-system.com',
                'repository': 'https://github.com/your-program/modules',
                'support_email': 'support@your-program-system.com'
            }
            
            # 플러그인 등록
            success = marketplace.register_plugin(str(module_dir), metadata)
            if success:
                print(f"  ✅ {module_info['name']} 마켓플레이스 등록 완료")
                registered_modules.append(module_id)
                
                # 자동 승인
                approval_success = marketplace.approve_plugin(module_id)
                if approval_success:
                    print(f"  ✅ {module_info['name']} 승인 완료")
                else:
                    print(f"  ⚠️  {module_info['name']} 승인 실패")
            else:
                print(f"  ❌ {module_info['name']} 마켓플레이스 등록 실패")
                
        except Exception as e:
            print(f"  ❌ {module_info['name']} 등록 중 오류: {e}")
    
    # 샘플 평점 및 다운로드 수 추가
    print("⭐ 샘플 평점 및 다운로드 수 추가 중...")
    try:
        from core.backend.plugin_marketplace_system import marketplace
        
        for module_id in registered_modules:
            # 평점 추가
            ratings = [4.5, 4.0, 4.8, 4.2, 4.6]
            for rating in ratings:
                marketplace.rate_plugin(module_id, rating, f"user_{rating}")
            
            # 다운로드 수 설정
            if module_id in marketplace.marketplace_data['plugins']:
                downloads = {
                    'attendance_management': 120,
                    'schedule_module': 95,
                    'inventory_module': 78,
                    'purchase_module': 65,
                    'ai_analysis_module': 45
                }.get(module_id, 50)
                
                marketplace.marketplace_data['plugins'][module_id]['downloads'] = downloads
                print(f"  ✅ {module_id} 다운로드 수 {downloads} 설정 완료")
        
        marketplace.save_marketplace_data()
        
    except Exception as e:
        print(f"  ⚠️  평점 및 다운로드 수 추가 실패: {e}")
    
    # 통계 출력
    print("\n📊 모듈 마켓플레이스 통계:")
    try:
        from core.backend.plugin_marketplace_system import marketplace
        stats = marketplace.get_plugin_statistics()
        print(f"  총 모듈: {stats.get('total_plugins', 0)}")
        print(f"  총 다운로드: {stats.get('total_downloads', 0)}")
        print(f"  총 평점: {stats.get('total_ratings', 0)}")
        
        if 'category_statistics' in stats:
            print("  카테고리별 통계:")
            for category, cat_stats in stats['category_statistics'].items():
                print(f"    {category}: {cat_stats['count']}개, {cat_stats['downloads']}다운로드, 평점 {cat_stats['avg_rating']}")
                
    except Exception as e:
        print(f"  ⚠️  통계 조회 실패: {e}")
    
    print(f"\n✅ 샘플 모듈 등록 완료! ({len(registered_modules)}개)")
    print("\n📝 다음 단계:")
    print("1. 서버를 재시작하여 모듈 마켓플레이스 API를 활성화하세요")
    print("2. 프론트엔드에서 /module-marketplace 페이지에 접속하세요")
    print("3. 모듈을 검색하고 다운로드해보세요")
    print("4. 브랜드별로 모듈을 활성화하고 커스터마이징할 수 있습니다")

if __name__ == "__main__":
    register_sample_modules() 