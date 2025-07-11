#!/usr/bin/env python3
"""
플러그인 테스트 환경 구축
플러그인 개발을 위한 테스트 환경을 자동으로 설정하는 도구
"""

import json
import subprocess
import sys
from pathlib import Path
# from typing import Any  # 미사용


class PluginTestEnvironment:
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.test_config = {
            "pytest": {
                "testpaths": ["tests"],
                "python_files": ["test_*.py", "*_test.py"],
                "python_classes": ["Test*"],
                "python_functions": ["test_*"],
                "addopts": [
                    "-v",
                    "--tb=short",
                    "--strict-markers",
                    "--disable-warnings"
                ]
            }
        }

    def setup_test_environment(self, plugin_id: str) -> bool:
        """플러그인 테스트 환경 설정"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                print(f"❌ 플러그인 {plugin_id}이 존재하지 않습니다.")
                return False

            # 테스트 디렉토리 생성
            test_path = plugin_path / "tests"
            test_path.mkdir(exist_ok=True)

            # 테스트 설정 파일 생성
            self._create_pytest_config(plugin_path)
            self._create_test_structure(test_path, plugin_id)
            self._create_test_requirements(plugin_path)
            self._create_test_data(plugin_path, plugin_id)

            print(f"✅ {plugin_id} 플러그인 테스트 환경이 설정되었습니다.")
            return True

        except Exception as e:
            print(f"❌ 테스트 환경 설정 중 오류: {e}")
            return False

    def run_tests(self, plugin_id: str, test_type: str = "all") -> bool:
        """테스트 실행"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                print(f"❌ 플러그인 {plugin_id}이 존재하지 않습니다.")
                return False

            # 테스트 의존성 설치
            print("📦 테스트 의존성 설치 중...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r",
                str(plugin_path / "test_requirements.txt")
            ], check=True)

            # 테스트 실행
            print(f"🧪 {plugin_id} 플러그인 테스트 실행 중...")
            test_args = ["pytest", str(plugin_path / "tests")]
            if test_type == "unit":
                test_args.extend(["-m", "unit"])
            elif test_type == "integration":
                test_args.extend(["-m", "integration"])
            result = subprocess.run(test_args, cwd=plugin_path)
            if result.returncode == 0:
                print(f"✅ {plugin_id} 플러그인 테스트가 성공적으로 완료되었습니다.")
                return True
            else:
                print(f"❌ {plugin_id} 플러그인 테스트가 실패했습니다.")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return False

    def generate_test_report(self, plugin_id: str) -> bool:
        """테스트 리포트 생성"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                print(f"❌ 플러그인 {plugin_id}이 존재하지 않습니다.")
                return False
            # HTML 리포트 생성
            subprocess.run([
                "pytest", str(plugin_path / "tests"),
                "--cov=backend",
                "--cov-report=html",
                "--cov-report=term-missing"
            ], cwd=plugin_path, check=True)
            report_path = plugin_path / "htmlcov"
            if report_path.exists():
                print(f"📊 테스트 리포트가 생성되었습니다: {report_path}")
                return True
            else:
                print("❌ 테스트 리포트 생성에 실패했습니다.")
                return False
        except Exception as e:
            print(f"❌ 리포트 생성 중 오류: {e}")
            return False

    def _create_pytest_config(self, plugin_path: Path):
        """pytest 설정 파일 생성"""
        config_path = plugin_path / "pytest.ini"
        
        config_content = f"""[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
"""
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)

    def _create_test_structure(self, test_path: Path, plugin_id: str):
        """테스트 구조 생성"""
        # __init__.py 생성
        init_content = f'''"""
{plugin_id} 플러그인 테스트
"""

import pytest
import sys
from pathlib import Path

# 플러그인 경로를 sys.path에 추가
plugin_path = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_path))
'''
        
        with open(test_path / "__init__.py", "w", encoding="utf-8") as f:
            f.write(init_content)

        # 단위 테스트 파일 생성
        unit_test_content = self._generate_unit_tests(plugin_id)
        with open(test_path / "test_unit.py", "w", encoding="utf-8") as f:
            f.write(unit_test_content)

        # 통합 테스트 파일 생성
        integration_test_content = self._generate_integration_tests(plugin_id)
        with open(test_path / "test_integration.py", "w", encoding="utf-8") as f:
            f.write(integration_test_content)

        # 테스트 유틸리티 파일 생성
        utils_content = self._generate_test_utils(plugin_id)
        with open(test_path / "test_utils.py", "w", encoding="utf-8") as f:
            f.write(utils_content)

    def _create_test_requirements(self, plugin_path: Path):
        """테스트 의존성 파일 생성"""
        test_requirements = [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-asyncio>=0.21.0",
            "flask-testing>=0.8.1",
            "factory-boy>=3.2.0",
            "faker>=18.0.0"
        ]
        
        with open(plugin_path / "test_requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(test_requirements))

    def _create_test_data(self, plugin_path: Path, plugin_id: str):
        """테스트 데이터 생성"""
        test_data_path = plugin_path / "tests" / "data"
        test_data_path.mkdir(exist_ok=True)

        # 테스트 설정 데이터
        test_config = {
            "plugin_id": plugin_id,
            "test_mode": True,
            "mock_data": True,
            "database": {
                "url": "sqlite:///:memory:",
                "echo": False
            }
        }
        
        with open(test_data_path / "test_config.json", "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)

        # 샘플 테스트 데이터
        sample_data = {
            "users": [
                {"id": 1, "name": "Test User 1", "email": "test1@example.com"},
                {"id": 2, "name": "Test User 2", "email": "test2@example.com"}
            ],
            "settings": {
                "debug": True,
                "timeout": 30,
                "retry_count": 3
            }
        }
        
        with open(test_data_path / "sample_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)

    def _generate_unit_tests(self, plugin_id: str) -> str:
        """단위 테스트 파일 내용 생성"""
        class_name = plugin_id.replace('-', '_').title()
        
        return f'''"""
{plugin_id} 플러그인 단위 테스트
"""

import pytest
from unittest.mock import Mock, patch
from backend.main import {class_name}Plugin


class Test{class_name}Plugin:
    """{class_name}Plugin 단위 테스트"""
    
    @pytest.fixture
    def plugin(self):
        """플러그인 인스턴스 생성"""
        return {class_name}Plugin()
    
    def test_plugin_initialization(self, plugin):
        """플러그인 초기화 테스트"""
        assert plugin.plugin_id == "{plugin_id}"
        assert plugin.blueprint is not None
    
    def test_get_metadata(self, plugin):
        """메타데이터 반환 테스트"""
        metadata = plugin.get_metadata()
        assert metadata.id == "{plugin_id}"
        assert metadata.name is not None
        assert metadata.version is not None
        assert metadata.description is not None
        assert metadata.author is not None
    
    def test_get_routes(self, plugin):
        """라우트 반환 테스트"""
        routes = plugin.get_routes()
        assert isinstance(routes, list)
        for route in routes:
            assert hasattr(route, 'path')
            assert hasattr(route, 'methods')
            assert hasattr(route, 'handler')
    
    def test_get_menus(self, plugin):
        """메뉴 반환 테스트"""
        menus = plugin.get_menus()
        assert isinstance(menus, list)
        for menu in menus:
            assert hasattr(menu, 'id')
            assert hasattr(menu, 'title')
            assert hasattr(menu, 'path')
    
    def test_plugin_config(self, plugin):
        """플러그인 설정 테스트"""
        config = plugin.get_config()
        assert isinstance(config, dict)
        assert 'enabled' in config
    
    @pytest.mark.asyncio
    async def test_async_operations(self, plugin):
        """비동기 작업 테스트"""
        if hasattr(plugin, 'async_operation'):
            result = await plugin.async_operation()
            assert result is not None
    
    def test_error_handling(self, plugin):
        """오류 처리 테스트"""
        with pytest.raises(Exception):
            plugin.invalid_operation()
    
    def test_data_validation(self, plugin):
        """데이터 검증 테스트"""
        test_data = {"test": "data"}
        if hasattr(plugin, 'validate_data'):
            result = plugin.validate_data(test_data)
            assert isinstance(result, bool)
    
    def test_performance(self, plugin):
        """성능 테스트"""
        import time
        start_time = time.time()
        plugin.performance_test()
        execution_time = time.time() - start_time
        assert execution_time < 1.0  # 1초 이내 실행
    
    def test_memory_usage(self, plugin):
        """메모리 사용량 테스트"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        plugin.memory_intensive_operation()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가량이 100MB 이내여야 함
        assert memory_increase < 100 * 1024 * 1024
'''

    def _generate_integration_tests(self, plugin_id: str) -> str:
        """통합 테스트 파일 내용 생성"""
        class_name = plugin_id.replace('-', '_').title()
        
        return f'''"""
{plugin_id} 플러그인 통합 테스트
"""

import pytest
from flask import Flask
from flask.testing import FlaskClient
from unittest.mock import Mock, patch
from backend.main import {class_name}Plugin


class Test{class_name}PluginIntegration:
    """{class_name}Plugin 통합 테스트"""
    
    @pytest.fixture
    def app(self):
        """Flask 앱 생성"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        return app
    
    @pytest.fixture
    def client(self, app):
        """테스트 클라이언트 생성"""
        return app.test_client()
    
    @pytest.fixture
    def plugin(self):
        """플러그인 인스턴스 생성"""
        return {class_name}Plugin()
    
    def test_plugin_registration(self, app, plugin):
        """플러그인 등록 테스트"""
        plugin.register(app)
        assert plugin.blueprint in app.blueprints.values()
    
    def test_route_integration(self, app, plugin, client):
        """라우트 통합 테스트"""
        plugin.register(app)
        
        routes = plugin.get_routes()
        for route in routes:
            if 'GET' in route.methods:
                response = client.get(route.path)
                assert response.status_code in [200, 404, 405]
    
    def test_database_integration(self, plugin):
        """데이터베이스 통합 테스트"""
        if hasattr(plugin, 'database_operation'):
            result = plugin.database_operation()
            assert result is not None
    
    def test_external_api_integration(self, plugin):
        """외부 API 통합 테스트"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"status": "success"}
            
            if hasattr(plugin, 'api_call'):
                result = plugin.api_call()
                assert result is not None
    
    def test_plugin_interaction(self, plugin):
        """플러그인 간 상호작용 테스트"""
        other_plugin = Mock()
        other_plugin.plugin_id = "other_plugin"
        
        if hasattr(plugin, 'interact_with_plugin'):
            result = plugin.interact_with_plugin(other_plugin)
            assert result is not None
    
    def test_configuration_integration(self, plugin):
        """설정 통합 테스트"""
        test_config = {
            "enabled": True,
            "debug_mode": False,
            "timeout": 30
        }
        
        if hasattr(plugin, 'apply_config'):
            plugin.apply_config(test_config)
            current_config = plugin.get_config()
            assert current_config.get('enabled') == True
    
    def test_error_recovery(self, app, plugin):
        """오류 복구 테스트"""
        plugin.register(app)
        
        # 의도적으로 오류 발생
        with patch.object(plugin, 'error_prone_operation', side_effect=Exception("Test error")):
            try:
                plugin.error_prone_operation()
            except Exception:
                pass
            
            # 플러그인이 정상적으로 복구되었는지 확인
            assert plugin.is_healthy()
    
    def test_performance_under_load(self, app, plugin, client):
        """부하 하에서의 성능 테스트"""
        plugin.register(app)
        
        import time
        import threading
        
        def make_request():
            for _ in range(10):
                client.get(f'/plugin/{plugin_id}/status')
        
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        execution_time = time.time() - start_time
        assert execution_time < 10.0  # 10초 이내 완료
    
    def test_data_consistency(self, plugin):
        """데이터 일관성 테스트"""
        test_data = {"key": "value"}
        
        if hasattr(plugin, 'save_data'):
            plugin.save_data(test_data)
        
        if hasattr(plugin, 'load_data'):
            loaded_data = plugin.load_data()
            assert loaded_data == test_data
    
    def test_plugin_lifecycle(self, app, plugin):
        """플러그인 생명주기 테스트"""
        # 초기화
        assert not plugin.is_initialized()
        plugin.initialize()
        assert plugin.is_initialized()
        
        # 등록
        plugin.register(app)
        assert plugin.is_registered()
        
        # 활성화
        plugin.activate()
        assert plugin.is_active()
        
        # 비활성화
        plugin.deactivate()
        assert not plugin.is_active()
        
        # 해제
        plugin.cleanup()
        assert not plugin.is_initialized()
    
    def test_concurrent_access(self, app, plugin):
        """동시 접근 테스트"""
        import threading
        import time
        
        plugin.register(app)
        results = []
        
        def worker():
            for _ in range(5):
                if hasattr(plugin, 'thread_safe_operation'):
                    result = plugin.thread_safe_operation()
                    results.append(result)
                time.sleep(0.1)
        
        threads = [threading.Thread(target=worker) for _ in range(3)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 모든 작업이 성공적으로 완료되었는지 확인
        assert len(results) == 15  # 3 threads * 5 operations
'''

    def _generate_test_utils(self, plugin_id: str) -> str:
        """테스트 유틸리티 파일 내용 생성"""
        return f'''"""
{plugin_id} 플러그인 테스트 유틸리티
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch


class PluginTestUtils:
    """플러그인 테스트 유틸리티 클래스"""
    
    @staticmethod
    def create_temp_config(config_data: Any) -> str:
        """임시 설정 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            return f.name
    
    @staticmethod
    def load_test_data(data_file: str) -> Any:
        """테스트 데이터 로드"""
        data_path = Path(__file__).parent / "data" / data_file
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def create_mock_plugin_registry():
        """모의 플러그인 레지스트리 생성"""
        registry = Mock()
        registry.get_plugin.return_value = Mock()
        registry.get_all_plugins.return_value = {{}}
        registry.register_plugin.return_value = True
        registry.unregister_plugin.return_value = True
        return registry
    
    @staticmethod
    def create_mock_plugin_loader():
        """모의 플러그인 로더 생성"""
        loader = Mock()
        loader.get_plugin_config.return_value = {{}}
        loader.save_plugin_config.return_value = True
        loader.load_plugin.return_value = True
        loader.unload_plugin.return_value = True
        return loader
    
    @staticmethod
    def assert_plugin_metadata(metadata):
        """플러그인 메타데이터 검증"""
        assert hasattr(metadata, 'id')
        assert hasattr(metadata, 'name')
        assert hasattr(metadata, 'version')
        assert hasattr(metadata, 'description')
        assert hasattr(metadata, 'author')
        assert hasattr(metadata, 'category')
    
    @staticmethod
    def assert_plugin_route(route):
        """플러그인 라우트 검증"""
        assert hasattr(route, 'path')
        assert hasattr(route, 'methods')
        assert hasattr(route, 'handler')
        assert isinstance(route.methods, list)
        assert len(route.methods) > 0
    
    @staticmethod
    def assert_plugin_menu(menu):
        """플러그인 메뉴 검증"""
        assert hasattr(menu, 'id')
        assert hasattr(menu, 'title')
        assert hasattr(menu, 'path')
        assert hasattr(menu, 'icon')
    
    @staticmethod
    def create_test_environment():
        """테스트 환경 생성"""
        test_env = {{
            'TESTING': True,
            'DEBUG': False,
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///:memory:'
        }}
        return test_env
    
    @staticmethod
    def cleanup_temp_files(temp_files: list):
        """임시 파일 정리"""
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink()
            except FileNotFoundError:
                pass
'''


# 테스트 데이터 팩토리
class TestDataFactory:
    """테스트 데이터 팩토리"""
    
    @staticmethod
    def create_user_data(user_id: int = 1):
        """사용자 테스트 데이터 생성"""
        return {
            'id': user_id,
            'name': f'Test User {user_id}',
            'email': f'test{user_id}@example.com',
            'role': 'user'
        }
    
    @staticmethod
    def create_plugin_config_data(plugin_id: str):
        """플러그인 설정 테스트 데이터 생성"""
        return {
            'plugin_id': plugin_id,
            'enabled': True,
            'debug_mode': False,
            'version': '1.0.0',
            'settings': {
                'timeout': 30,
                'retry_count': 3
            }
        }
    
    @staticmethod
    def create_health_status_data():
        """상태 확인 테스트 데이터 생성"""
        return {
            'status': 'healthy',
            'uptime': '2023-01-01T00:00:00',
            'version': '1.0.0',
            'features': ['feature1', 'feature2']
        }


# 테스트 마커 정의
pytest_plugins = ['pytest_mock']


def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )


def main():
    """메인 함수"""
    test_env = PluginTestEnvironment()
    
    print("🧪 플러그인 테스트 환경 구축")
    print("=" * 50)
    
    # 플러그인 ID 입력
    plugin_id = input("테스트 환경을 설정할 플러그인 ID를 입력하세요: ").strip()
    
    if not plugin_id:
        print("❌ 플러그인 ID를 입력해주세요.")
        return
    
    # 테스트 환경 설정
    print(f"\n🔧 {plugin_id} 플러그인 테스트 환경 설정 중...")
    if test_env.setup_test_environment(plugin_id):
        print(f"\n✅ {plugin_id} 플러그인 테스트 환경이 설정되었습니다!")
        
        # 테스트 실행 여부 확인
        run_tests = input("\n테스트를 실행하시겠습니까? (y/N): ").strip().lower()
        if run_tests == 'y':
            test_type = input("테스트 유형을 선택하세요 (all/unit/integration): ").strip() or "all"
            test_env.run_tests(plugin_id, test_type)
        
        # 리포트 생성 여부 확인
        generate_report = input("\n테스트 리포트를 생성하시겠습니까? (y/N): ").strip().lower()
        if generate_report == 'y':
            test_env.generate_test_report(plugin_id)
        
        print(f"\n📁 테스트 파일 위치:")
        print(f"  - 테스트 디렉토리: plugins/{plugin_id}/tests/")
        print(f"  - 설정 파일: plugins/{plugin_id}/pytest.ini")
        print(f"  - 의존성: plugins/{plugin_id}/test_requirements.txt")
        print(f"  - 리포트: plugins/{plugin_id}/htmlcov/ (테스트 실행 후)")
        
        print(f"\n🚀 다음 명령어로 테스트를 실행할 수 있습니다:")
        print(f"  cd plugins/{plugin_id}")
        print(f"  pytest tests/")
        print(f"  pytest tests/ -m unit")
        print(f"  pytest tests/ -m integration")


if __name__ == "__main__":
    main() 