#!/usr/bin/env python3
"""
플러그인 시스템 전체 초기화 스크립트
모든 플러그인 시스템 컴포넌트를 초기화하고 테스트합니다.
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/plugin_system_init.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def init_plugin_system():
    """플러그인 시스템 전체 초기화"""
    logger.info("=== 플러그인 시스템 전체 초기화 시작 ===")
    
    try:
        # 1. 플러그인 시스템 매니저 초기화
        logger.info("1. 플러그인 시스템 매니저 초기화")
        from core.backend.plugin_system_manager import plugin_system_manager
        
        init_result = plugin_system_manager.initialize_system()
        logger.info(f"초기화 결과: {init_result}")
        
        # 2. 플러그인 시스템 시작
        logger.info("2. 플러그인 시스템 시작")
        start_result = plugin_system_manager.start_system()
        logger.info(f"시작 결과: {start_result}")
        
        # 3. 시스템 상태 확인
        logger.info("3. 시스템 상태 확인")
        status = plugin_system_manager.get_system_status()
        logger.info(f"시스템 상태: {status}")
        
        # 4. 헬스 체크 실행
        logger.info("4. 헬스 체크 실행")
        health_result = plugin_system_manager.run_health_check()
        logger.info(f"헬스 체크 결과: {health_result}")
        
        # 5. 시스템 정보 조회
        logger.info("5. 시스템 정보 조회")
        info = plugin_system_manager.get_system_info()
        logger.info(f"시스템 정보: {info}")
        
        # 6. 각 컴포넌트별 상태 확인
        logger.info("6. 컴포넌트별 상태 확인")
        for name, component in plugin_system_manager.components.items():
            if component:
                try:
                    if hasattr(component, 'get_status'):
                        component_status = component.get_status()
                        logger.info(f"  {name}: {component_status}")
                    else:
                        logger.info(f"  {name}: available")
                except Exception as e:
                    logger.error(f"  {name}: error - {e}")
            else:
                logger.warning(f"  {name}: unavailable")
        
        # 7. 플러그인 레지스트리 확인
        logger.info("7. 플러그인 레지스트리 확인")
        try:
            # 동적 import로 안전하게 처리
            import importlib
            plugin_registry_module = importlib.import_module('core.backend.plugin_registry')
            all_plugins = plugin_registry_module.plugin_registry.get_all_plugins()
            active_plugins = plugin_registry_module.plugin_registry.get_active_plugins()
            
            logger.info(f"  전체 플러그인 수: {len(all_plugins)}")
            logger.info(f"  활성 플러그인 수: {len(active_plugins)}")
            
            for plugin_id, plugin in all_plugins.items():
                status = "활성" if plugin_id in active_plugins else "비활성"
                logger.info(f"    {plugin_id}: {status}")
                
        except Exception as e:
            logger.error(f"플러그인 레지스트리 확인 실패: {e}")
        
        # 8. 플러그인 마켓플레이스 확인
        logger.info("8. 플러그인 마켓플레이스 확인")
        try:
            # 동적 import로 안전하게 처리
            import importlib
            plugin_marketplace_module = importlib.import_module('core.backend.plugin_marketplace')
            available_plugins = plugin_marketplace_module.plugin_marketplace.get_available_plugins()
            logger.info(f"  마켓플레이스 플러그인 수: {len(available_plugins)}")
            
            for plugin in available_plugins[:5]:  # 처음 5개만 표시
                logger.info(f"    {plugin.get('name', 'Unknown')}: {plugin.get('version', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"플러그인 마켓플레이스 확인 실패: {e}")
        
        # 9. 플러그인 보안 시스템 확인
        logger.info("9. 플러그인 보안 시스템 확인")
        try:
            # 동적 import로 안전하게 처리
            import importlib
            plugin_security_module = importlib.import_module('core.backend.plugin_security')
            security_status = plugin_security_module.plugin_security.get_security_status()
            logger.info(f"  보안 상태: {security_status}")
            
        except Exception as e:
            logger.error(f"플러그인 보안 시스템 확인 실패: {e}")
        
        # 10. 플러그인 최적화 시스템 확인
        logger.info("10. 플러그인 최적화 시스템 확인")
        try:
            from core.backend.plugin_optimizer import system_optimizer
            optimizer_status = system_optimizer.get_system_status()
            logger.info(f"  최적화 시스템 상태: {optimizer_status}")
            
        except Exception as e:
            logger.error(f"플러그인 최적화 시스템 확인 실패: {e}")
        
        logger.info("=== 플러그인 시스템 전체 초기화 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"플러그인 시스템 초기화 실패: {e}")
        return False

def test_plugin_system_apis():
    """플러그인 시스템 API 테스트"""
    logger.info("=== 플러그인 시스템 API 테스트 시작 ===")
    
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # API 엔드포인트 테스트
        test_endpoints = [
            "/api/plugin-system/status",
            "/api/plugin-system/info",
            "/api/plugin-system/metrics",
            "/api/plugin-system/config",
            "/api/plugin-management/plugins",
            "/api/plugin-security/status",
            "/api/plugin-marketplace/plugins",
        ]
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    logger.info(f"  [OK] {endpoint}: 성공")
                else:
                    logger.warning(f"  [WARN] {endpoint}: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"  [ERROR] {endpoint}: 실패 - {e}")
        
        # POST 엔드포인트 테스트
        post_endpoints = [
            ("/api/plugin-system/health-check", {}),
        ]
        
        for endpoint, data in post_endpoints:
            try:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=5)
                if response.status_code == 200:
                    logger.info(f"  [OK] {endpoint}: 성공")
                else:
                    logger.warning(f"  [WARN] {endpoint}: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"  [ERROR] {endpoint}: 실패 - {e}")
        
        logger.info("=== 플러그인 시스템 API 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"API 테스트 실패: {e}")
        return False

def create_sample_plugins():
    """샘플 플러그인 생성"""
    logger.info("=== 샘플 플러그인 생성 ===")
    
    try:
        # 플러그인 디렉토리 생성
        plugin_dir = Path("plugins")
        plugin_dir.mkdir(exist_ok=True)
        
        # 샘플 플러그인들
        sample_plugins = [
            {
                "name": "sample_analytics",
                "description": "샘플 분석 플러그인",
                "version": "1.0.0",
                "author": "System",
                "main_file": "main.py"
            },
            {
                "name": "sample_notification",
                "description": "샘플 알림 플러그인", 
                "version": "1.0.0",
                "author": "System",
                "main_file": "main.py"
            },
            {
                "name": "sample_reporting",
                "description": "샘플 리포트 플러그인",
                "version": "1.0.0", 
                "author": "System",
                "main_file": "main.py"
            }
        ]
        
        for plugin_info in sample_plugins:
            plugin_name = plugin_info["name"]
            plugin_path = plugin_dir / plugin_name
            plugin_path.mkdir(exist_ok=True)
            
            # 플러그인 메인 파일 생성
            main_file = plugin_path / "main.py"
            if not main_file.exists():
                with open(main_file, 'w', encoding='utf-8') as f:
                    f.write(f'''"""
{plugin_info["description"]}
"""

class {plugin_name.replace('_', '').title()}Plugin:
    def __init__(self):
        self.name = "{plugin_name}"
        self.version = "{plugin_info["version"]}"
        self.author = "{plugin_info["author"]}"
        self.description = "{plugin_info["description"]}"
    
    def initialize(self):
        """플러그인 초기화"""
        print(f"{{self.name}} 플러그인 초기화")
    
    def get_routes(self):
        """라우트 정보 반환"""
        return []
    
    def get_menu_items(self):
        """메뉴 아이템 반환"""
        return []

# 플러그인 인스턴스
plugin = {plugin_name.replace('_', '').title()}Plugin()
''')
            
            # 플러그인 설정 파일 생성 (JSON 문자열로 직접 작성)
            config_file = plugin_path / "config.json"
            if not config_file.exists():
                config_content = f'''{{
  "name": "{plugin_info["name"]}",
  "description": "{plugin_info["description"]}",
  "version": "{plugin_info["version"]}",
  "author": "{plugin_info["author"]}",
  "main_file": "{plugin_info["main_file"]}"
}}'''
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(config_content)
            
            logger.info(f"  [OK] {plugin_name} 플러그인 생성 완료")
        
        logger.info("=== 샘플 플러그인 생성 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"샘플 플러그인 생성 실패: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("플러그인 시스템 초기화 스크립트 시작")
    
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 1. 샘플 플러그인 생성
    if not create_sample_plugins():
        logger.error("샘플 플러그인 생성 실패")
        return False
    
    # 2. 플러그인 시스템 초기화
    if not init_plugin_system():
        logger.error("플러그인 시스템 초기화 실패")
        return False
    
    # 3. API 테스트 (서버가 실행 중인 경우)
    try:
        test_plugin_system_apis()
    except Exception as e:
        logger.warning(f"API 테스트 건너뜀 (서버가 실행되지 않음): {e}")
    
    logger.info("플러그인 시스템 초기화 스크립트 완료")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 