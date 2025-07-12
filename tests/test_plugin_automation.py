"""
플러그인 자동화 및 워크플로우 시스템 테스트
고도화된 자동 배포, 테스트, 모니터링 워크플로우 테스트
"""

import unittest
import json
import tempfile
import shutil
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# 테스트 대상 모듈들
from core.backend.plugin_automation_workflow import (
    PluginAutomationWorkflow, WorkflowConfig, WorkflowStatus, WorkflowStep, WorkflowExecution
)
from api.plugin_automation_api import plugin_automation_bp

class TestWorkflowConfig(unittest.TestCase):
    """워크플로우 설정 테스트"""
    
    def test_workflow_config_creation(self):
        """워크플로우 설정 생성 테스트"""
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION, WorkflowStep.BUILD, WorkflowStep.DEPLOY],
            timeout_minutes=30,
            auto_rollback=True
        )
        
        self.assertEqual(config.name, "테스트 워크플로우")
        self.assertEqual(config.description, "테스트용 워크플로우")
        self.assertEqual(len(config.steps), 3)
        self.assertEqual(config.timeout_minutes, 30)
        self.assertTrue(config.auto_rollback)
        self.assertIsInstance(config.notification_channels, list)
        self.assertIsInstance(config.environment_variables, dict)

class TestWorkflowExecution(unittest.TestCase):
    """워크플로우 실행 테스트"""
    
    def test_workflow_execution_creation(self):
        """워크플로우 실행 생성 테스트"""
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        execution = WorkflowExecution(
            id="test_execution_123",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.PENDING,
            current_step=None,
            start_time=datetime.now(),
            end_time=None,
            logs=[],
            artifacts={},
            error_message=None
        )
        
        self.assertEqual(execution.id, "test_execution_123")
        self.assertEqual(execution.plugin_id, "test_plugin")
        self.assertEqual(execution.status, WorkflowStatus.PENDING)
        self.assertIsNone(execution.current_step)
        self.assertIsInstance(execution.logs, list)
        self.assertIsInstance(execution.artifacts, dict)
    
    def test_workflow_execution_to_dict(self):
        """워크플로우 실행 딕셔너리 변환 테스트"""
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        start_time = datetime.now()
        execution = WorkflowExecution(
            id="test_execution_123",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.SUCCESS,
            current_step=WorkflowStep.VALIDATION,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=5),
            logs=[{"timestamp": "2024-01-01T00:00:00", "message": "테스트"}],
            artifacts={"test": "data"},
            error_message=None
        )
        
        execution_dict = execution.to_dict()
        
        self.assertEqual(execution_dict["id"], "test_execution_123")
        self.assertEqual(execution_dict["plugin_id"], "test_plugin")
        self.assertEqual(execution_dict["workflow_name"], "테스트 워크플로우")
        self.assertEqual(execution_dict["status"], "success")
        self.assertEqual(execution_dict["current_step"], "validation")
        self.assertEqual(execution_dict["logs_count"], 1)
        self.assertIsNone(execution_dict["error_message"])
    
    def test_workflow_execution_duration(self):
        """워크플로우 실행 시간 계산 테스트"""
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=10, seconds=30)
        
        execution = WorkflowExecution(
            id="test_execution_123",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.SUCCESS,
            current_step=None,
            start_time=start_time,
            end_time=end_time,
            logs=[],
            artifacts={},
            error_message=None
        )
        
        duration = execution.get_duration_minutes()
        self.assertAlmostEqual(duration, 10.5, places=1)

class TestPluginAutomationWorkflow(unittest.TestCase):
    """플러그인 자동화 워크플로우 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.workflow_manager = PluginAutomationWorkflow(self.temp_dir)
    
    def tearDown(self):
        """테스트 정리"""
        shutil.rmtree(self.temp_dir)
    
    def test_workflow_manager_initialization(self):
        """워크플로우 매니저 초기화 테스트"""
        self.assertIsInstance(self.workflow_manager.workflows, dict)
        self.assertIsInstance(self.workflow_manager.executions, dict)
        self.assertIsInstance(self.workflow_manager.executor, type(self.workflow_manager.executor))
        
        # 기본 워크플로우 확인
        expected_workflows = ['full_deployment', 'quick_deploy', 'security_focus', 'testing_only']
        for workflow_id in expected_workflows:
            self.assertIn(workflow_id, self.workflow_manager.workflows)
    
    def test_default_workflows_loaded(self):
        """기본 워크플로우 로드 테스트"""
        # 전체 배포 워크플로우
        full_deployment = self.workflow_manager.workflows['full_deployment']
        self.assertEqual(full_deployment.name, "전체 배포 워크플로우")
        self.assertTrue(full_deployment.auto_rollback)
        self.assertEqual(full_deployment.timeout_minutes, 45)
        
        # 빠른 배포 워크플로우
        quick_deploy = self.workflow_manager.workflows['quick_deploy']
        self.assertEqual(quick_deploy.name, "빠른 배포 워크플로우")
        self.assertFalse(quick_deploy.auto_rollback)
        self.assertEqual(quick_deploy.timeout_minutes, 15)
    
    @patch('core.backend.plugin_automation_workflow.docker.from_env')
    def test_docker_client_initialization(self, mock_docker):
        """Docker 클라이언트 초기화 테스트"""
        # Docker 사용 가능한 경우
        mock_docker.return_value = Mock()
        workflow_manager = PluginAutomationWorkflow()
        self.assertIsNotNone(workflow_manager.docker_client)
        
        # Docker 사용 불가능한 경우
        mock_docker.side_effect = Exception("Docker not available")
        workflow_manager = PluginAutomationWorkflow()
        self.assertIsNone(workflow_manager.docker_client)
    
    async def test_create_workflow(self):
        """워크플로우 생성 테스트"""
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION, WorkflowStep.BUILD],
            timeout_minutes=20,
            auto_rollback=False
        )
        
        success = await self.workflow_manager.create_workflow("test_workflow", config)
        self.assertTrue(success)
        self.assertIn("test_workflow", self.workflow_manager.workflows)
        
        created_workflow = self.workflow_manager.workflows["test_workflow"]
        self.assertEqual(created_workflow.name, "테스트 워크플로우")
        self.assertEqual(len(created_workflow.steps), 2)
        self.assertFalse(created_workflow.auto_rollback)
    
    async def test_get_workflow(self):
        """워크플로우 조회 테스트"""
        # 존재하는 워크플로우
        workflow = await self.workflow_manager.get_workflow("full_deployment")
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.name, "전체 배포 워크플로우")
        
        # 존재하지 않는 워크플로우
        workflow = await self.workflow_manager.get_workflow("non_existent")
        self.assertIsNone(workflow)
    
    async def test_list_workflows(self):
        """워크플로우 목록 조회 테스트"""
        workflows = await self.workflow_manager.list_workflows()
        
        self.assertIsInstance(workflows, list)
        self.assertGreater(len(workflows), 0)
        
        # 각 워크플로우의 구조 확인
        for workflow in workflows:
            self.assertIn("id", workflow)
            self.assertIn("name", workflow)
            self.assertIn("description", workflow)
            self.assertIn("steps", workflow)
            self.assertIn("timeout_minutes", workflow)
            self.assertIn("auto_rollback", workflow)
    
    async def test_execute_workflow(self):
        """워크플로우 실행 테스트"""
        # 테스트 플러그인 디렉토리 생성
        plugin_dir = Path(self.temp_dir) / "test_plugin"
        plugin_dir.mkdir()
        
        # 기본 플러그인 파일 생성
        config_dir = plugin_dir / "config"
        config_dir.mkdir()
        
        plugin_config = {
            "name": "테스트 플러그인",
            "version": "1.0.0",
            "description": "테스트용 플러그인",
            "author": "테스트 작성자"
        }
        
        with open(config_dir / "plugin.json", "w") as f:
            json.dump(plugin_config, f)
        
        backend_dir = plugin_dir / "backend"
        backend_dir.mkdir()
        
        with open(backend_dir / "plugin.py", "w") as f:
            f.write("# 테스트 플러그인\nprint('Hello, World!')\n")
        
        # 워크플로우 실행
        execution_id = await self.workflow_manager.execute_workflow(
            "quick_deploy", "test_plugin", {"test_param": "value"}
        )
        
        self.assertIsInstance(execution_id, str)
        self.assertIn(execution_id, self.workflow_manager.executions)
        
        # 실행 정보 확인
        execution = self.workflow_manager.executions[execution_id]
        self.assertEqual(execution.plugin_id, "test_plugin")
        self.assertEqual(execution.workflow_config.name, "빠른 배포 워크플로우")
        self.assertIn(execution.status, [WorkflowStatus.PENDING, WorkflowStatus.RUNNING])
    
    async def test_execution_validation_step(self):
        """검증 단계 테스트"""
        # 유효한 플러그인 구조
        plugin_dir = Path(self.temp_dir) / "valid_plugin"
        plugin_dir.mkdir()
        
        config_dir = plugin_dir / "config"
        config_dir.mkdir()
        
        plugin_config = {
            "name": "유효한 플러그인",
            "version": "1.0.0",
            "description": "유효한 플러그인",
            "author": "작성자"
        }
        
        with open(config_dir / "plugin.json", "w") as f:
            json.dump(plugin_config, f)
        
        backend_dir = plugin_dir / "backend"
        backend_dir.mkdir()
        
        with open(backend_dir / "plugin.py", "w") as f:
            f.write("# 유효한 플러그인\nprint('Valid plugin')\n")
        
        # 검증 단계 실행
        await self.workflow_manager._execute_validation(
            Mock(), plugin_dir, {}
        )
        # 예외가 발생하지 않으면 성공
    
    async def test_execution_validation_step_invalid(self):
        """잘못된 플러그인 검증 테스트"""
        # 잘못된 플러그인 구조
        plugin_dir = Path(self.temp_dir) / "invalid_plugin"
        plugin_dir.mkdir()
        
        # 필수 파일이 없는 경우
        with self.assertRaises(FileNotFoundError):
            await self.workflow_manager._execute_validation(
                Mock(), plugin_dir, {}
            )
    
    async def test_execution_build_step(self):
        """빌드 단계 테스트"""
        plugin_dir = Path(self.temp_dir) / "build_test_plugin"
        plugin_dir.mkdir()
        
        # 테스트 파일 생성
        test_file = plugin_dir / "test.txt"
        test_file.write_text("테스트 파일")
        
        execution = Mock()
        execution.artifacts = {}
        
        await self.workflow_manager._execute_build(execution, plugin_dir, {})
        
        # 빌드 결과 확인
        self.assertIn("package_path", execution.artifacts)
        self.assertIn("package_size", execution.artifacts)
        
        package_path = Path(execution.artifacts["package_path"])
        self.assertTrue(package_path.exists())
        self.assertGreater(execution.artifacts["package_size"], 0)
    
    async def test_execution_security_scan(self):
        """보안 스캔 단계 테스트"""
        plugin_dir = Path(self.temp_dir) / "security_test_plugin"
        plugin_dir.mkdir()
        
        # 안전한 Python 파일
        safe_file = plugin_dir / "safe.py"
        safe_file.write_text("# 안전한 코드\nprint('Hello')\n")
        
        execution = Mock()
        execution.artifacts = {}
        
        await self.workflow_manager._execute_security_scan(execution, plugin_dir, {})
        
        # 보안 이슈가 없어야 함
        if "security_issues" in execution.artifacts:
            self.assertEqual(len(execution.artifacts["security_issues"]), 0)
    
    async def test_execution_security_scan_dangerous(self):
        """위험한 코드 보안 스캔 테스트"""
        plugin_dir = Path(self.temp_dir) / "dangerous_plugin"
        plugin_dir.mkdir()
        
        # 위험한 Python 파일
        dangerous_file = plugin_dir / "dangerous.py"
        dangerous_file.write_text("import os\nos.system('rm -rf /')\n")
        
        execution = Mock()
        execution.artifacts = {}
        
        await self.workflow_manager._execute_security_scan(execution, plugin_dir, {})
        
        # 보안 이슈가 발견되어야 함
        self.assertIn("security_issues", execution.artifacts)
        self.assertGreater(len(execution.artifacts["security_issues"]), 0)
    
    async def test_execution_deploy_step(self):
        """배포 단계 테스트"""
        plugin_dir = Path(self.temp_dir) / "deploy_test_plugin"
        plugin_dir.mkdir()
        
        test_file = plugin_dir / "test.txt"
        test_file.write_text("배포 테스트")
        
        execution = Mock()
        execution.artifacts = {}
        execution.plugin_id = "deploy_test_plugin"
        
        await self.workflow_manager._execute_deploy(execution, plugin_dir, {})
        
        # 배포 결과 확인
        self.assertIn("deploy_path", execution.artifacts)
        
        deploy_path = Path(execution.artifacts["deploy_path"])
        self.assertTrue(deploy_path.exists())
        
        # 배포된 파일 확인
        deployed_file = deploy_path / "test.txt"
        self.assertTrue(deployed_file.exists())
        self.assertEqual(deployed_file.read_text(), "배포 테스트")
    
    async def test_execution_monitor_step(self):
        """모니터링 단계 테스트"""
        plugin_dir = Path(self.temp_dir) / "monitor_test_plugin"
        plugin_dir.mkdir()
        
        test_file = plugin_dir / "test.txt"
        test_file.write_text("모니터링 테스트")
        
        execution = Mock()
        execution.artifacts = {"deploy_path": str(plugin_dir)}
        
        await self.workflow_manager._execute_monitor(execution, plugin_dir, {})
        
        # 모니터링 결과 확인
        self.assertIn("monitoring_info", execution.artifacts)
        
        monitoring_info = execution.artifacts["monitoring_info"]
        self.assertIn("deployed_at", monitoring_info)
        self.assertIn("plugin_size", monitoring_info)
        self.assertIn("file_count", monitoring_info)
        self.assertEqual(monitoring_info["status"], "active")
    
    async def test_cancel_execution(self):
        """워크플로우 실행 취소 테스트"""
        # 실행 중인 워크플로우 생성
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        execution = WorkflowExecution(
            id="cancel_test_123",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.RUNNING,
            current_step=WorkflowStep.VALIDATION,
            start_time=datetime.now(),
            end_time=None,
            logs=[],
            artifacts={},
            error_message=None
        )
        
        self.workflow_manager.executions["cancel_test_123"] = execution
        
        # 실행 취소
        success = await self.workflow_manager.cancel_execution("cancel_test_123")
        self.assertTrue(success)
        self.assertEqual(execution.status, WorkflowStatus.CANCELLED)
        self.assertIsNotNone(execution.end_time)
        
        # 이미 완료된 실행 취소 시도
        execution.status = WorkflowStatus.SUCCESS
        success = await self.workflow_manager.cancel_execution("cancel_test_123")
        self.assertFalse(success)
    
    async def test_get_execution_logs(self):
        """실행 로그 조회 테스트"""
        # 테스트 실행 생성
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        execution = WorkflowExecution(
            id="logs_test_123",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.SUCCESS,
            current_step=None,
            start_time=datetime.now(),
            end_time=datetime.now(),
            logs=[
                {
                    "timestamp": "2024-01-01T00:00:00",
                    "level": "info",
                    "message": "테스트 로그",
                    "step": "validation"
                }
            ],
            artifacts={},
            error_message=None
        )
        
        self.workflow_manager.executions["logs_test_123"] = execution
        
        # 로그 조회
        logs = await self.workflow_manager.get_execution_logs("logs_test_123")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["message"], "테스트 로그")
        self.assertEqual(logs[0]["level"], "info")
        
        # 존재하지 않는 실행 로그 조회
        logs = await self.workflow_manager.get_execution_logs("non_existent")
        self.assertEqual(logs, [])
    
    async def test_list_executions(self):
        """실행 목록 조회 테스트"""
        # 테스트 실행들 생성
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        for i in range(3):
            execution = WorkflowExecution(
                id=f"list_test_{i}",
                plugin_id=f"plugin_{i}",
                workflow_config=config,
                status=WorkflowStatus.SUCCESS,
                current_step=None,
                start_time=datetime.now(),
                end_time=datetime.now(),
                logs=[],
                artifacts={},
                error_message=None
            )
            self.workflow_manager.executions[f"list_test_{i}"] = execution
        
        # 전체 실행 목록
        executions = await self.workflow_manager.list_executions()
        self.assertGreaterEqual(len(executions), 3)
        
        # 특정 플러그인 필터링
        executions = await self.workflow_manager.list_executions(plugin_id="plugin_0")
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["plugin_id"], "plugin_0")
        
        # 상태별 필터링
        executions = await self.workflow_manager.list_executions(status=WorkflowStatus.SUCCESS)
        self.assertGreaterEqual(len(executions), 3)
    
    async def test_get_workflow_statistics(self):
        """워크플로우 통계 테스트"""
        # 테스트 실행들 생성
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        # 성공한 실행
        success_execution = WorkflowExecution(
            id="stats_success",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.SUCCESS,
            current_step=None,
            start_time=datetime.now() - timedelta(minutes=10),
            end_time=datetime.now(),
            logs=[],
            artifacts={},
            error_message=None
        )
        
        # 실패한 실행
        failed_execution = WorkflowExecution(
            id="stats_failed",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.FAILED,
            current_step=None,
            start_time=datetime.now() - timedelta(minutes=5),
            end_time=datetime.now(),
            logs=[],
            artifacts={},
            error_message="테스트 오류"
        )
        
        self.workflow_manager.executions["stats_success"] = success_execution
        self.workflow_manager.executions["stats_failed"] = failed_execution
        
        # 통계 조회
        stats = await self.workflow_manager.get_workflow_statistics()
        
        self.assertEqual(stats["total_executions"], 2)
        self.assertEqual(stats["success_rate"], 50.0)
        self.assertIn("success", stats["status_distribution"])
        self.assertIn("failed", stats["status_distribution"])
        self.assertEqual(stats["status_distribution"]["success"], 1)
        self.assertEqual(stats["status_distribution"]["failed"], 1)
    
    async def test_cleanup_old_executions(self):
        """오래된 실행 기록 정리 테스트"""
        # 오래된 실행 생성
        config = WorkflowConfig(
            name="테스트 워크플로우",
            description="테스트용 워크플로우",
            steps=[WorkflowStep.VALIDATION]
        )
        
        old_execution = WorkflowExecution(
            id="old_execution",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.SUCCESS,
            current_step=None,
            start_time=datetime.now() - timedelta(days=31),
            end_time=datetime.now() - timedelta(days=31),
            logs=[],
            artifacts={},
            error_message=None
        )
        
        # 최근 실행 생성
        recent_execution = WorkflowExecution(
            id="recent_execution",
            plugin_id="test_plugin",
            workflow_config=config,
            status=WorkflowStatus.SUCCESS,
            current_step=None,
            start_time=datetime.now() - timedelta(days=5),
            end_time=datetime.now() - timedelta(days=5),
            logs=[],
            artifacts={},
            error_message=None
        )
        
        self.workflow_manager.executions["old_execution"] = old_execution
        self.workflow_manager.executions["recent_execution"] = recent_execution
        
        # 30일 이전 실행 정리
        cleaned_count = await self.workflow_manager.cleanup_old_executions(days=30)
        self.assertEqual(cleaned_count, 1)
        
        # 오래된 실행은 삭제되고 최근 실행은 유지
        self.assertNotIn("old_execution", self.workflow_manager.executions)
        self.assertIn("recent_execution", self.workflow_manager.executions)

class TestPluginAutomationAPI(unittest.TestCase):
    """플러그인 자동화 API 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(plugin_automation_bp)
        self.client = self.app.test_client()
    
    def test_list_workflows_endpoint(self):
        """워크플로우 목록 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_run_async.return_value = [
                {
                    "id": "test_workflow",
                    "name": "테스트 워크플로우",
                    "description": "테스트용",
                    "steps": ["validation", "build"],
                    "timeout_minutes": 30,
                    "auto_rollback": True
                }
            ]
            
            response = self.client.get('/api/plugin-automation/workflows')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 1)
            self.assertEqual(data['data'][0]['id'], 'test_workflow')
    
    def test_get_workflow_endpoint(self):
        """특정 워크플로우 조회 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_workflow = Mock()
            mock_workflow.name = "테스트 워크플로우"
            mock_workflow.description = "테스트용"
            mock_workflow.steps = [WorkflowStep.VALIDATION, WorkflowStep.BUILD]
            mock_workflow.timeout_minutes = 30
            mock_workflow.auto_rollback = True
            mock_workflow.parallel_execution = False
            mock_workflow.notification_channels = ['email']
            mock_workflow.environment_variables = {}
            
            mock_run_async.return_value = mock_workflow
            
            response = self.client.get('/api/plugin-automation/workflows/test_workflow')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['name'], '테스트 워크플로우')
    
    def test_create_workflow_endpoint(self):
        """워크플로우 생성 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_run_async.return_value = True
            
            workflow_data = {
                "id": "new_workflow",
                "name": "새 워크플로우",
                "description": "새로 생성된 워크플로우",
                "steps": ["validation", "build", "deploy"],
                "timeout_minutes": 45,
                "auto_rollback": True,
                "parallel_execution": False,
                "notification_channels": ["email", "webhook"],
                "environment_variables": {}
            }
            
            response = self.client.post(
                '/api/plugin-automation/workflows',
                data=json.dumps(workflow_data),
                content_type='application/json'
            )
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 201)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['workflow_id'], 'new_workflow')
    
    def test_execute_workflow_endpoint(self):
        """워크플로우 실행 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_run_async.side_effect = [Mock(), "execution_123"]
            
            execution_data = {
                "workflow_id": "quick_deploy",
                "plugin_id": "test_plugin",
                "parameters": {"test_param": "value"}
            }
            
            response = self.client.post(
                '/api/plugin-automation/execute',
                data=json.dumps(execution_data),
                content_type='application/json'
            )
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 202)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['execution_id'], 'execution_123')
    
    def test_list_executions_endpoint(self):
        """실행 목록 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_run_async.return_value = [
                {
                    "id": "execution_123",
                    "plugin_id": "test_plugin",
                    "workflow_name": "테스트 워크플로우",
                    "status": "success",
                    "current_step": None,
                    "start_time": "2024-01-01T00:00:00",
                    "end_time": "2024-01-01T00:05:00",
                    "duration_minutes": 5.0,
                    "logs_count": 10,
                    "error_message": None
                }
            ]
            
            response = self.client.get('/api/plugin-automation/executions')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 1)
            self.assertEqual(data['data'][0]['id'], 'execution_123')
    
    def test_get_execution_logs_endpoint(self):
        """실행 로그 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_run_async.return_value = [
                {
                    "timestamp": "2024-01-01T00:00:00",
                    "level": "info",
                    "message": "테스트 로그",
                    "step": "validation"
                }
            ]
            
            response = self.client.get('/api/plugin-automation/executions/execution_123/logs')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 1)
            self.assertEqual(data['data'][0]['message'], '테스트 로그')
    
    def test_cancel_execution_endpoint(self):
        """실행 취소 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_run_async.return_value = True
            
            response = self.client.post('/api/plugin-automation/executions/execution_123/cancel')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['execution_id'], 'execution_123')
    
    def test_get_statistics_endpoint(self):
        """통계 API 테스트"""
        with patch('api.plugin_automation_api.run_async') as mock_run_async:
            mock_run_async.return_value = {
                "total_executions": 10,
                "success_rate": 80.0,
                "average_duration": 15.5,
                "status_distribution": {
                    "success": 8,
                    "failed": 2
                }
            }
            
            response = self.client.get('/api/plugin-automation/statistics')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['total_executions'], 10)
            self.assertEqual(data['data']['success_rate'], 80.0)
    
    def test_health_check_endpoint(self):
        """헬스 체크 API 테스트"""
        response = self.client.get('/api/plugin-automation/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'healthy')

if __name__ == '__main__':
    unittest.main() 