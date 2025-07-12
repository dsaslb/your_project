"""
플러그인 자동화 및 워크플로우 관리 시스템
고도화된 자동 배포, 테스트, 모니터링 워크플로우 제공
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
from dataclasses import dataclass, asdict
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import docker
from docker.errors import DockerException

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """워크플로우 상태 열거형"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class WorkflowStep(Enum):
    """워크플로우 단계 열거형"""
    VALIDATION = "validation"
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    DEPLOY = "deploy"
    MONITOR = "monitor"
    ROLLBACK = "rollback"

@dataclass
class WorkflowConfig:
    """워크플로우 설정 데이터 클래스"""
    name: str
    description: str
    steps: List[WorkflowStep]
    timeout_minutes: int = 30
    auto_rollback: bool = True
    parallel_execution: bool = False
    notification_channels: List[str] = None
    environment_variables: Dict[str, str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email", "webhook"]
        if self.environment_variables is None:
            self.environment_variables = {}

@dataclass
class WorkflowExecution:
    """워크플로우 실행 정보 데이터 클래스"""
    id: str
    plugin_id: str
    workflow_config: WorkflowConfig
    status: WorkflowStatus
    current_step: Optional[WorkflowStep]
    start_time: datetime
    end_time: Optional[datetime]
    logs: List[Dict[str, Any]]
    artifacts: Dict[str, Any]
    error_message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "plugin_id": self.plugin_id,
            "workflow_name": self.workflow_config.name,
            "status": self.status.value,
            "current_step": self.current_step.value if self.current_step else None,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.get_duration_minutes(),
            "logs_count": len(self.logs),
            "error_message": self.error_message
        }
    
    def get_duration_minutes(self) -> float:
        """실행 시간을 분 단위로 반환"""
        end_time = self.end_time or datetime.now()
        duration = end_time - self.start_time
        return duration.total_seconds() / 60

class PluginAutomationWorkflow:
    """플러그인 자동화 및 워크플로우 관리 시스템"""
    
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.workflows: Dict[str, WorkflowConfig] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.docker_client = None
        self._init_docker_client()
        self._load_default_workflows()
    
    def _init_docker_client(self):
        """Docker 클라이언트 초기화"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker 클라이언트 초기화 성공")
        except DockerException as e:
            logger.warning(f"Docker 클라이언트 초기화 실패: {e}")
            self.docker_client = None
    
    def _load_default_workflows(self):
        """기본 워크플로우 로드"""
        default_workflows = {
            "full_deployment": WorkflowConfig(
                name="전체 배포 워크플로우",
                description="검증부터 배포까지 전체 과정을 자동화",
                steps=[
                    WorkflowStep.VALIDATION,
                    WorkflowStep.BUILD,
                    WorkflowStep.TEST,
                    WorkflowStep.SECURITY_SCAN,
                    WorkflowStep.DEPLOY,
                    WorkflowStep.MONITOR
                ],
                timeout_minutes=45,
                auto_rollback=True
            ),
            "quick_deploy": WorkflowConfig(
                name="빠른 배포 워크플로우",
                description="기본 검증 후 빠른 배포",
                steps=[
                    WorkflowStep.VALIDATION,
                    WorkflowStep.BUILD,
                    WorkflowStep.DEPLOY
                ],
                timeout_minutes=15,
                auto_rollback=False
            ),
            "security_focus": WorkflowConfig(
                name="보안 중심 워크플로우",
                description="보안 검사에 중점을 둔 배포",
                steps=[
                    WorkflowStep.VALIDATION,
                    WorkflowStep.SECURITY_SCAN,
                    WorkflowStep.BUILD,
                    WorkflowStep.TEST,
                    WorkflowStep.DEPLOY
                ],
                timeout_minutes=30,
                auto_rollback=True
            ),
            "testing_only": WorkflowConfig(
                name="테스트 전용 워크플로우",
                description="배포 없이 테스트만 실행",
                steps=[
                    WorkflowStep.VALIDATION,
                    WorkflowStep.BUILD,
                    WorkflowStep.TEST
                ],
                timeout_minutes=20,
                auto_rollback=False
            )
        }
        
        for workflow_id, config in default_workflows.items():
            self.workflows[workflow_id] = config
    
    async def create_workflow(self, workflow_id: str, config: WorkflowConfig) -> bool:
        """새 워크플로우 생성"""
        try:
            self.workflows[workflow_id] = config
            await self._save_workflows()
            logger.info(f"워크플로우 생성 완료: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"워크플로우 생성 실패: {e}")
            return False
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowConfig]:
        """워크플로우 조회"""
        return self.workflows.get(workflow_id)
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """워크플로우 목록 조회"""
        return [
            {
                "id": workflow_id,
                "name": config.name,
                "description": config.description,
                "steps": [step.value for step in config.steps],
                "timeout_minutes": config.timeout_minutes,
                "auto_rollback": config.auto_rollback
            }
            for workflow_id, config in self.workflows.items()
        ]
    
    async def execute_workflow(self, workflow_id: str, plugin_id: str, 
                             parameters: Dict[str, Any] = None) -> str:
        """워크플로우 실행"""
        if workflow_id not in self.workflows:
            raise ValueError(f"워크플로우를 찾을 수 없습니다: {workflow_id}")
        
        execution_id = f"{workflow_id}_{plugin_id}_{int(time.time())}"
        workflow_config = self.workflows[workflow_id]
        
        execution = WorkflowExecution(
            id=execution_id,
            plugin_id=plugin_id,
            workflow_config=workflow_config,
            status=WorkflowStatus.PENDING,
            current_step=None,
            start_time=datetime.now(),
            end_time=None,
            logs=[],
            artifacts={},
            error_message=None
        )
        
        self.executions[execution_id] = execution
        
        # 비동기로 워크플로우 실행
        asyncio.create_task(self._run_workflow(execution, parameters))
        
        return execution_id
    
    async def _run_workflow(self, execution: WorkflowExecution, parameters: Dict[str, Any]):
        """워크플로우 실행 로직"""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.now()
            
            plugin_path = self.base_path / execution.plugin_id
            if not plugin_path.exists():
                raise FileNotFoundError(f"플러그인 경로를 찾을 수 없습니다: {plugin_path}")
            
            # 각 단계 순차 실행
            for step in execution.workflow_config.steps:
                execution.current_step = step
                await self._log_step(execution, f"단계 시작: {step.value}")
                
                try:
                    if step == WorkflowStep.VALIDATION:
                        await self._execute_validation(execution, plugin_path, parameters)
                    elif step == WorkflowStep.BUILD:
                        await self._execute_build(execution, plugin_path, parameters)
                    elif step == WorkflowStep.TEST:
                        await self._execute_test(execution, plugin_path, parameters)
                    elif step == WorkflowStep.SECURITY_SCAN:
                        await self._execute_security_scan(execution, plugin_path, parameters)
                    elif step == WorkflowStep.DEPLOY:
                        await self._execute_deploy(execution, plugin_path, parameters)
                    elif step == WorkflowStep.MONITOR:
                        await self._execute_monitor(execution, plugin_path, parameters)
                    
                    await self._log_step(execution, f"단계 완료: {step.value}")
                    
                except Exception as e:
                    await self._log_step(execution, f"단계 실패: {step.value} - {str(e)}")
                    execution.error_message = str(e)
                    
                    if execution.workflow_config.auto_rollback:
                        await self._execute_rollback(execution, plugin_path)
                    
                    execution.status = WorkflowStatus.FAILED
                    execution.end_time = datetime.now()
                    return
            
            execution.status = WorkflowStatus.SUCCESS
            execution.end_time = datetime.now()
            await self._log_step(execution, "워크플로우 완료")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            await self._log_step(execution, f"워크플로우 실패: {str(e)}")
    
    async def _execute_validation(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
        """플러그인 검증 단계"""
        await self._log_step(execution, "플러그인 구조 검증 시작")
        
        # 필수 파일 검증
        required_files = ["config/plugin.json", "backend/plugin.py"]
        for file_path in required_files:
            if not (plugin_path / file_path).exists():
                raise ValueError(f"필수 파일이 없습니다: {file_path}")
        
        # 설정 파일 검증
        config_file = plugin_path / "config/plugin.json"
        async with aiofiles.open(config_file, 'r', encoding='utf-8') as f:
            config_content = await f.read()
            config = json.loads(config_content)
            
            required_fields = ["name", "version", "description", "author"]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"필수 설정 필드가 없습니다: {field}")
        
        # 코드 문법 검증
        await self._validate_python_syntax(execution, plugin_path)
        
        await self._log_step(execution, "플러그인 검증 완료")
    
    async def _execute_build(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
        """플러그인 빌드 단계"""
        await self._log_step(execution, "플러그인 빌드 시작")
        
        # 빌드 디렉토리 생성
        build_dir = plugin_path / "build"
        build_dir.mkdir(exist_ok=True)
        
        # 플러그인 패키징
        plugin_name = execution.plugin_id
        package_path = build_dir / f"{plugin_name}.zip"
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in plugin_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    arcname = file_path.relative_to(plugin_path)
                    zipf.write(file_path, arcname)
        
        execution.artifacts["package_path"] = str(package_path)
        execution.artifacts["package_size"] = package_path.stat().st_size
        
        await self._log_step(execution, f"플러그인 빌드 완료: {package_path}")
    
    async def _execute_test(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
        """플러그인 테스트 단계"""
        await self._log_step(execution, "플러그인 테스트 시작")
        
        # 테스트 파일 검색
        test_files = list(plugin_path.rglob("test_*.py"))
        if not test_files:
            await self._log_step(execution, "테스트 파일이 없어 기본 검증만 수행")
            return
        
        # 테스트 실행
        test_results = []
        for test_file in test_files:
            try:
                result = await self._run_python_test(execution, test_file)
                test_results.append(result)
            except Exception as e:
                await self._log_step(execution, f"테스트 실패: {test_file.name} - {str(e)}")
                raise
        
        execution.artifacts["test_results"] = test_results
        await self._log_step(execution, f"테스트 완료: {len(test_results)}개 테스트 실행")
    
    async def _execute_security_scan(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
        """보안 스캔 단계"""
        await self._log_step(execution, "보안 스캔 시작")
        
        # Python 파일 보안 검사
        python_files = list(plugin_path.rglob("*.py"))
        security_issues = []
        
        for py_file in python_files:
            issues = await self._scan_python_security(execution, py_file)
            security_issues.extend(issues)
        
        if security_issues:
            execution.artifacts["security_issues"] = security_issues
            await self._log_step(execution, f"보안 이슈 발견: {len(security_issues)}개")
            
            # 심각한 보안 이슈가 있으면 실패
            critical_issues = [issue for issue in security_issues if issue.get("severity") == "critical"]
            if critical_issues:
                raise ValueError(f"심각한 보안 이슈가 발견되었습니다: {len(critical_issues)}개")
        else:
            await self._log_step(execution, "보안 스캔 완료 - 이슈 없음")
    
    async def _execute_deploy(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
        """플러그인 배포 단계"""
        await self._log_step(execution, "플러그인 배포 시작")
        
        # 배포 디렉토리로 복사
        deploy_dir = self.base_path / "deployed" / execution.plugin_id
        deploy_dir.mkdir(parents=True, exist_ok=True)
        
        # 기존 배포 백업
        if deploy_dir.exists():
            backup_dir = deploy_dir.parent / f"{execution.plugin_id}_backup_{int(time.time())}"
            shutil.move(str(deploy_dir), str(backup_dir))
            execution.artifacts["backup_path"] = str(backup_dir)
        
        # 새 버전 배포
        shutil.copytree(plugin_path, deploy_dir, dirs_exist_ok=True)
        
        # 배포 로그 생성
        deployment_log = {
            "timestamp": datetime.now().isoformat(),
            "plugin_id": execution.plugin_id,
            "execution_id": execution.id,
            "status": "deployed"
        }
        
        log_file = deploy_dir / "deployment_log.json"
        async with aiofiles.open(log_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(deployment_log, indent=2, ensure_ascii=False))
        
        execution.artifacts["deploy_path"] = str(deploy_dir)
        await self._log_step(execution, f"플러그인 배포 완료: {deploy_dir}")
    
    async def _execute_monitor(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
        """모니터링 단계"""
        await self._log_step(execution, "모니터링 시작")
        
        # 플러그인 상태 확인
        deploy_path = Path(execution.artifacts.get("deploy_path", ""))
        if not deploy_path.exists():
            raise ValueError("배포된 플러그인을 찾을 수 없습니다")
        
        # 기본 상태 정보 수집
        status_info = {
            "deployed_at": datetime.now().isoformat(),
            "plugin_size": sum(f.stat().st_size for f in deploy_path.rglob('*') if f.is_file()),
            "file_count": len(list(deploy_path.rglob('*'))),
            "status": "active"
        }
        
        execution.artifacts["monitoring_info"] = status_info
        await self._log_step(execution, "모니터링 완료")
    
    async def _execute_rollback(self, execution: WorkflowExecution, plugin_path: Path):
        """롤백 단계"""
        await self._log_step(execution, "롤백 시작")
        
        backup_path = execution.artifacts.get("backup_path")
        if backup_path and Path(backup_path).exists():
            deploy_dir = self.base_path / "deployed" / execution.plugin_id
            if deploy_dir.exists():
                shutil.rmtree(deploy_dir)
            shutil.move(backup_path, str(deploy_dir))
            await self._log_step(execution, "롤백 완료")
        else:
            await self._log_step(execution, "백업이 없어 롤백을 건너뜀")
    
    async def _validate_python_syntax(self, execution: WorkflowExecution, plugin_path: Path):
        """Python 문법 검증"""
        python_files = list(plugin_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    raise ValueError(f"Python 문법 오류: {py_file.name} - {result.stderr}")
            except subprocess.TimeoutExpired:
                raise ValueError(f"Python 문법 검증 시간 초과: {py_file.name}")
    
    async def _run_python_test(self, execution: WorkflowExecution, test_file: Path) -> Dict[str, Any]:
        """Python 테스트 실행"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "test_file": test_file.name,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "test_file": test_file.name,
                "return_code": -1,
                "stdout": "",
                "stderr": "테스트 시간 초과",
                "success": False
            }
    
    async def _scan_python_security(self, execution: WorkflowExecution, py_file: Path) -> List[Dict[str, Any]]:
        """Python 파일 보안 검사"""
        issues = []
        
        try:
            async with aiofiles.open(py_file, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # 위험한 패턴 검사
            dangerous_patterns = [
                (r"eval\s*\(", "eval 함수 사용", "high"),
                (r"exec\s*\(", "exec 함수 사용", "high"),
                (r"__import__\s*\(", "__import__ 함수 사용", "medium"),
                (r"subprocess\.Popen", "subprocess.Popen 사용", "medium"),
                (r"os\.system", "os.system 사용", "medium"),
                (r"input\s*\(", "input 함수 사용", "low")
            ]
            
            import re
            for pattern, description, severity in dangerous_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "file": py_file.name,
                        "line": line_num,
                        "pattern": pattern,
                        "description": description,
                        "severity": severity
                    })
        
        except Exception as e:
            issues.append({
                "file": py_file.name,
                "line": 0,
                "pattern": "file_read_error",
                "description": f"파일 읽기 오류: {str(e)}",
                "severity": "medium"
            })
        
        return issues
    
    async def _log_step(self, execution: WorkflowExecution, message: str, level: str = "info"):
        """워크플로우 단계 로그 기록"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "step": execution.current_step.value if execution.current_step else None
        }
        
        execution.logs.append(log_entry)
        logger.info(f"[{execution.id}] {message}")
    
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """워크플로우 실행 정보 조회"""
        return self.executions.get(execution_id)
    
    async def list_executions(self, plugin_id: Optional[str] = None, 
                            status: Optional[WorkflowStatus] = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """워크플로우 실행 목록 조회"""
        executions = []
        
        for exec_id, execution in self.executions.items():
            if plugin_id and execution.plugin_id != plugin_id:
                continue
            if status and execution.status != status:
                continue
            
            executions.append(execution.to_dict())
        
        # 최신 순으로 정렬
        executions.sort(key=lambda x: x["start_time"], reverse=True)
        return executions[:limit]
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """워크플로우 실행 취소"""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now()
            await self._log_step(execution, "워크플로우 취소됨")
            return True
        
        return False
    
    async def get_execution_logs(self, execution_id: str) -> List[Dict[str, Any]]:
        """워크플로우 실행 로그 조회"""
        execution = self.executions.get(execution_id)
        if not execution:
            return []
        
        return execution.logs
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """워크플로우 통계 정보"""
        total_executions = len(self.executions)
        if total_executions == 0:
            return {
                "total_executions": 0,
                "success_rate": 0,
                "average_duration": 0,
                "status_distribution": {}
            }
        
        status_counts = {}
        successful_executions = 0
        total_duration = 0
        
        for execution in self.executions.values():
            status = execution.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if execution.status == WorkflowStatus.SUCCESS:
                successful_executions += 1
            
            if execution.end_time:
                duration = (execution.end_time - execution.start_time).total_seconds() / 60
                total_duration += duration
        
        return {
            "total_executions": total_executions,
            "success_rate": (successful_executions / total_executions) * 100,
            "average_duration": total_duration / total_executions,
            "status_distribution": status_counts
        }
    
    async def _save_workflows(self):
        """워크플로우 설정 저장"""
        workflows_file = self.base_path / "workflows.json"
        workflows_data = {}
        
        for workflow_id, config in self.workflows.items():
            workflows_data[workflow_id] = {
                "name": config.name,
                "description": config.description,
                "steps": [step.value for step in config.steps],
                "timeout_minutes": config.timeout_minutes,
                "auto_rollback": config.auto_rollback,
                "parallel_execution": config.parallel_execution,
                "notification_channels": config.notification_channels,
                "environment_variables": config.environment_variables
            }
        
        async with aiofiles.open(workflows_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(workflows_data, indent=2, ensure_ascii=False))
    
    async def cleanup_old_executions(self, days: int = 30):
        """오래된 실행 기록 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)
        executions_to_remove = []
        
        for execution_id, execution in self.executions.items():
            if execution.start_time < cutoff_date:
                executions_to_remove.append(execution_id)
        
        for execution_id in executions_to_remove:
            del self.executions[execution_id]
        
        logger.info(f"오래된 실행 기록 {len(executions_to_remove)}개 정리 완료")
        return len(executions_to_remove)

# 전역 인스턴스
workflow_manager = PluginAutomationWorkflow() 