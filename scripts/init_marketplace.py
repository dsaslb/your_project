#!/usr/bin/env python3
"""
플러그인 마켓플레이스 시스템 초기화 스크립트
"""

import sys
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.backend.plugin_marketplace_system import marketplace, deployment_system

def create_sample_plugin(plugin_id: str, name: str, description: str, author: str, category: str):
    """샘플 플러그인 생성"""
    plugin_dir = Path(f"plugins/samples/{plugin_id}")
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    # plugin.json 생성
    plugin_config = {
        "plugin_id": plugin_id,
        "name": name,
        "version": "1.0.0",
        "description": description,
        "author": author,
        "category": category,
        "dependencies": [],
        "permissions": ["read", "write"],
        "entry_point": "main.py",
        "config_schema": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": True},
                "debug_mode": {"type": "boolean", "default": False}
            }
        }
    }
    
    with open(plugin_dir / "plugin.json", 'w', encoding='utf-8') as f:
        json.dump(plugin_config, f, indent=2, ensure_ascii=False)
    
    # README.md 생성
    readme_content = f"""# {name}

{description}

## 설치 방법

1. 플러그인 파일을 다운로드합니다.
2. 플러그인 디렉토리에 압축을 해제합니다.
3. 시스템에서 플러그인을 활성화합니다.

## 사용 방법

이 플러그인은 자동으로 활성화되며, 별도의 설정이 필요하지 않습니다.

## 라이선스

MIT License

## 작성자

{author}
"""
    
    with open(plugin_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # main.py 생성
    main_content = f'''#!/usr/bin/env python3
"""
{name} 플러그인 메인 모듈
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class {name.replace(" ", "")}Plugin:
    """{name} 플러그인 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.debug_mode = config.get("debug_mode", False)
        
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"{name} 플러그인이 초기화되었습니다.")
    
    def start(self):
        """플러그인 시작"""
        if not self.enabled:
            logger.info(f"{name} 플러그인이 비활성화되어 있습니다.")
            return
        
        logger.info(f"{name} 플러그인이 시작되었습니다.")
        
        # 여기에 플러그인 로직을 구현하세요
        self._initialize_plugin()
    
    def stop(self):
        """플러그인 중지"""
        logger.info(f"{name} 플러그인이 중지되었습니다.")
    
    def _initialize_plugin(self):
        """플러그인 초기화"""
        logger.debug(f"{name} 플러그인 초기화 중...")
        
        # 샘플 기능 구현
        self._sample_function()
    
    def _sample_function(self):
        """샘플 기능"""
        logger.info(f"{name} 플러그인의 샘플 기능이 실행되었습니다.")
        
        # 여기에 실제 기능을 구현하세요
        pass

def create_plugin(config: Dict[str, Any]):
    """플러그인 인스턴스 생성"""
    return {name.replace(" ", "")}Plugin(config)
'''
    
    with open(plugin_dir / "main.py", 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    # requirements.txt 생성
    requirements_content = """# 플러그인 의존성
# 필요한 패키지들을 여기에 추가하세요
# requests>=2.25.1
# pandas>=1.3.0
"""
    
    with open(plugin_dir / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    return plugin_dir

def init_plugin_marketplace():
    """플러그인 마켓플레이스 초기화"""
    print("🛒 플러그인 마켓플레이스 초기화 시작...")
    
    # 샘플 플러그인 생성
    print("📦 샘플 플러그인 생성 중...")
    sample_plugins = [
        {
            'plugin_id': 'restaurant_management',
            'name': '레스토랑 관리 플러그인',
            'description': '레스토랑 운영을 위한 종합 관리 플러그인으로 주문, 재고, 직원 관리 기능을 제공합니다.',
            'author': 'Restaurant Team',
            'category': 'business'
        },
        {
            'plugin_id': 'analytics_dashboard',
            'name': '분석 대시보드 플러그인',
            'description': '데이터 분석 및 시각화를 위한 대시보드 플러그인입니다.',
            'author': 'Analytics Team',
            'category': 'analytics'
        },
        {
            'plugin_id': 'notification_system',
            'name': '알림 시스템 플러그인',
            'description': '이메일, SMS, 푸시 알림을 통합 관리하는 알림 시스템 플러그인입니다.',
            'author': 'Communication Team',
            'category': 'communication'
        },
        {
            'plugin_id': 'security_monitor',
            'name': '보안 모니터링 플러그인',
            'description': '시스템 보안 상태를 실시간으로 모니터링하고 경고를 제공하는 플러그인입니다.',
            'author': 'Security Team',
            'category': 'security'
        },
        {
            'plugin_id': 'data_sync',
            'name': '데이터 동기화 플러그인',
            'description': '외부 시스템과의 데이터 동기화를 관리하는 플러그인입니다.',
            'author': 'Integration Team',
            'category': 'integration'
        },
        {
            'plugin_id': 'backup_manager',
            'name': '백업 관리 플러그인',
            'description': '자동 백업 및 복원 기능을 제공하는 유틸리티 플러그인입니다.',
            'author': 'Utility Team',
            'category': 'utility'
        }
    ]
    
    created_plugins = []
    for plugin_data in sample_plugins:
        plugin_dir = create_sample_plugin(
            plugin_data['plugin_id'],
            plugin_data['name'],
            plugin_data['description'],
            plugin_data['author'],
            plugin_data['category']
        )
        created_plugins.append((plugin_dir, plugin_data))
        print(f"  ✅ {plugin_data['name']} 생성 완료")
    
    # 플러그인 등록
    print("📋 플러그인 마켓플레이스 등록 중...")
    for plugin_dir, plugin_data in created_plugins:
        metadata = {
            'plugin_id': plugin_data['plugin_id'],
            'name': plugin_data['name'],
            'description': plugin_data['description'],
            'author': plugin_data['author'],
            'version': '1.0.0',
            'category': plugin_data['category'],
            'tags': ['sample', 'demo'],
            'license': 'MIT',
            'homepage': 'https://example.com',
            'repository': 'https://github.com/example/plugin',
            'support_email': 'support@example.com'
        }
        
        success = marketplace.register_plugin(str(plugin_dir), metadata)
        if success:
            print(f"  ✅ {plugin_data['name']} 마켓플레이스 등록 완료")
        else:
            print(f"  ⚠️  {plugin_data['name']} 마켓플레이스 등록 실패 (이미 존재)")
    
    # 일부 플러그인 승인
    print("✅ 플러그인 승인 중...")
    approved_plugins = ['restaurant_management', 'analytics_dashboard', 'notification_system']
    for plugin_id in approved_plugins:
        success = marketplace.approve_plugin(plugin_id)
        if success:
            print(f"  ✅ {plugin_id} 승인 완료")
        else:
            print(f"  ⚠️  {plugin_id} 승인 실패")
    
    # 샘플 평점 추가
    print("⭐ 샘플 평점 추가 중...")
    sample_ratings = [
        ('restaurant_management', 4.5, 'admin'),
        ('restaurant_management', 4.0, 'user1'),
        ('restaurant_management', 5.0, 'user2'),
        ('analytics_dashboard', 4.2, 'analyst1'),
        ('analytics_dashboard', 4.8, 'analyst2'),
        ('notification_system', 4.0, 'admin'),
        ('notification_system', 3.5, 'user3')
    ]
    
    for plugin_id, rating, user_id in sample_ratings:
        success = marketplace.rate_plugin(plugin_id, rating, user_id)
        if success:
            print(f"  ✅ {plugin_id} 평점 {rating} 추가 완료")
        else:
            print(f"  ❌ {plugin_id} 평점 추가 실패")
    
    # 샘플 다운로드 기록 추가
    print("📥 샘플 다운로드 기록 추가 중...")
    sample_downloads = [
        ('restaurant_management', 150),
        ('analytics_dashboard', 89),
        ('notification_system', 67),
        ('security_monitor', 45),
        ('data_sync', 34),
        ('backup_manager', 23)
    ]
    
    for plugin_id, downloads in sample_downloads:
        if plugin_id in marketplace.marketplace_data['plugins']:
            marketplace.marketplace_data['plugins'][plugin_id]['downloads'] = downloads
            print(f"  ✅ {plugin_id} 다운로드 수 {downloads} 설정 완료")
    
    marketplace.save_marketplace_data()
    
    # 샘플 배포 상태 생성
    print("🚀 샘플 배포 상태 생성 중...")
    sample_deployments = [
        {
            'plugin_id': 'restaurant_management',
            'environment': 'production',
            'deployed_at': '2024-01-15T10:30:00',
            'version': '1.0.0',
            'status': 'deployed'
        },
        {
            'plugin_id': 'analytics_dashboard',
            'environment': 'staging',
            'deployed_at': '2024-01-14T15:45:00',
            'version': '1.0.0',
            'status': 'deployed'
        }
    ]
    
    for deployment in sample_deployments:
        deployment_system.deployment_data['deployments'][deployment['plugin_id']] = deployment
        deployment_system.deployment_data['history'].append({
            **deployment,
            'action': 'deploy',
            'timestamp': deployment['deployed_at']
        })
        print(f"  ✅ {deployment['plugin_id']} 배포 상태 생성 완료")
    
    deployment_system.save_deployment_log()
    
    # 마켓플레이스 통계 출력
    print("\n📊 마켓플레이스 통계:")
    stats = marketplace.get_plugin_statistics()
    print(f"  총 플러그인: {stats.get('total_plugins', 0)}")
    print(f"  총 다운로드: {stats.get('total_downloads', 0)}")
    print(f"  총 평점: {stats.get('total_ratings', 0)}")
    
    if 'category_statistics' in stats:
        print("  카테고리별 통계:")
        for category, cat_stats in stats['category_statistics'].items():
            print(f"    {category}: {cat_stats['count']}개, {cat_stats['downloads']}다운로드, 평점 {cat_stats['avg_rating']}")
    
    print("\n✅ 플러그인 마켓플레이스 초기화 완료!")
    print("\n📝 다음 단계:")
    print("1. 서버를 재시작하여 마켓플레이스 API를 활성화하세요")
    print("2. 프론트엔드에서 /plugin-marketplace 페이지에 접속하세요")
    print("3. 플러그인을 검색하고 다운로드해보세요")
    print("4. 관리자는 플러그인 승인/거부 기능을 사용할 수 있습니다")

if __name__ == "__main__":
    init_plugin_marketplace() 