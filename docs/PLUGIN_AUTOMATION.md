# 플러그인 자동화 및 워크플로우 시스템

## 개요

플러그인 자동화 및 워크플로우 시스템은 플러그인의 자동 배포, 테스트, 모니터링을 위한 완전 자동화된 워크플로우 관리 시스템입니다. 이 시스템을 통해 플러그인 개발부터 배포까지의 전체 과정을 자동화하고 표준화할 수 있습니다.

## 주요 기능

### 1. 워크플로우 관리
- **워크플로우 정의**: 검증, 빌드, 테스트, 보안 스캔, 배포, 모니터링 단계를 조합하여 워크플로우 정의
- **워크플로우 템플릿**: 미리 정의된 워크플로우 템플릿 제공
- **커스텀 워크플로우**: 사용자 정의 워크플로우 생성 및 관리

### 2. 자동화된 실행 단계
- **검증 (Validation)**: 플러그인 구조 및 설정 파일 검증
- **빌드 (Build)**: 플러그인 패키징 및 빌드
- **테스트 (Test)**: 자동화된 테스트 실행
- **보안 스캔 (Security Scan)**: 보안 취약점 검사
- **배포 (Deploy)**: 자동 배포 및 버전 관리
- **모니터링 (Monitor)**: 배포 후 상태 모니터링
- **롤백 (Rollback)**: 실패 시 자동 롤백

### 3. 실시간 모니터링
- **실행 상태 추적**: 워크플로우 실행 상태 실시간 모니터링
- **로그 관리**: 상세한 실행 로그 수집 및 관리
- **알림 시스템**: 실행 완료/실패 시 알림

### 4. 통계 및 분석
- **성공률 분석**: 워크플로우 실행 성공률 통계
- **실행 시간 분석**: 평균 실행 시간 및 성능 분석
- **상태 분포**: 실행 상태별 분포 분석

## 시스템 아키텍처

### 백엔드 구성요소

#### 1. PluginAutomationWorkflow (core/backend/plugin_automation_workflow.py)
```python
class PluginAutomationWorkflow:
    """플러그인 자동화 및 워크플로우 관리 시스템"""
    
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.workflows: Dict[str, WorkflowConfig] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.docker_client = None
```

**주요 기능:**
- 워크플로우 정의 및 관리
- 워크플로우 실행 및 모니터링
- 실행 로그 수집
- 통계 정보 생성

#### 2. WorkflowConfig 데이터 클래스
```python
@dataclass
class WorkflowConfig:
    name: str
    description: str
    steps: List[WorkflowStep]
    timeout_minutes: int = 30
    auto_rollback: bool = True
    parallel_execution: bool = False
    notification_channels: List[str] = None
    environment_variables: Dict[str, str] = None
```

#### 3. WorkflowExecution 데이터 클래스
```python
@dataclass
class WorkflowExecution:
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
```

### 프론트엔드 구성요소

#### 1. PluginAutomationDashboard (frontend/src/components/PluginAutomationDashboard.tsx)
- 워크플로우 목록 및 관리
- 실행 상태 모니터링
- 실시간 로그 확인
- 통계 대시보드

#### 2. 플러그인 자동화 페이지 (frontend/src/app/plugin-automation/page.tsx)
- 전체 자동화 시스템 접근점

## API 엔드포인트

### 워크플로우 관리 API

#### 1. 워크플로우 목록 조회
```http
GET /api/plugin-automation/workflows
```

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": "full_deployment",
      "name": "전체 배포 워크플로우",
      "description": "검증부터 배포까지 전체 과정을 자동화",
      "steps": ["validation", "build", "test", "security_scan", "deploy", "monitor"],
      "timeout_minutes": 45,
      "auto_rollback": true
    }
  ],
  "message": "1개의 워크플로우를 찾았습니다."
}
```

#### 2. 워크플로우 생성
```http
POST /api/plugin-automation/workflows
Content-Type: application/json

{
  "id": "custom_workflow",
  "name": "커스텀 워크플로우",
  "description": "사용자 정의 워크플로우",
  "steps": ["validation", "build", "deploy"],
  "timeout_minutes": 30,
  "auto_rollback": true,
  "parallel_execution": false,
  "notification_channels": ["email", "webhook"],
  "environment_variables": {}
}
```

#### 3. 워크플로우 조회
```http
GET /api/plugin-automation/workflows/{workflow_id}
```

### 워크플로우 실행 API

#### 1. 워크플로우 실행
```http
POST /api/plugin-automation/execute
Content-Type: application/json

{
  "workflow_id": "full_deployment",
  "plugin_id": "my_plugin",
  "parameters": {
    "environment": "production",
    "version": "1.0.0"
  }
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "execution_id": "full_deployment_my_plugin_1704067200",
    "workflow_id": "full_deployment",
    "plugin_id": "my_plugin",
    "status": "pending"
  },
  "message": "워크플로우 실행이 시작되었습니다."
}
```

#### 2. 실행 목록 조회
```http
GET /api/plugin-automation/executions?plugin_id=my_plugin&status=running&limit=50
```

#### 3. 실행 상세 조회
```http
GET /api/plugin-automation/executions/{execution_id}
```

#### 4. 실행 로그 조회
```http
GET /api/plugin-automation/executions/{execution_id}/logs
```

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00",
      "level": "info",
      "message": "플러그인 검증 시작",
      "step": "validation"
    },
    {
      "timestamp": "2024-01-01T00:00:05",
      "level": "info",
      "message": "플러그인 검증 완료",
      "step": "validation"
    }
  ],
  "message": "2개의 로그 항목을 찾았습니다."
}
```

#### 5. 실행 취소
```http
POST /api/plugin-automation/executions/{execution_id}/cancel
```

### 통계 및 관리 API

#### 1. 워크플로우 통계
```http
GET /api/plugin-automation/statistics
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "total_executions": 100,
    "success_rate": 85.5,
    "average_duration": 12.3,
    "status_distribution": {
      "success": 85,
      "failed": 10,
      "running": 3,
      "cancelled": 2
    }
  },
  "message": "워크플로우 통계 정보를 성공적으로 조회했습니다."
}
```

#### 2. 오래된 실행 기록 정리
```http
POST /api/plugin-automation/cleanup
Content-Type: application/json

{
  "days": 30
}
```

#### 3. 헬스 체크
```http
GET /api/plugin-automation/health
```

## 기본 워크플로우 템플릿

### 1. 전체 배포 워크플로우 (full_deployment)
- **설명**: 검증부터 배포까지 전체 과정을 자동화
- **단계**: validation → build → test → security_scan → deploy → monitor
- **타임아웃**: 45분
- **자동 롤백**: 활성화

### 2. 빠른 배포 워크플로우 (quick_deploy)
- **설명**: 기본 검증 후 빠른 배포
- **단계**: validation → build → deploy
- **타임아웃**: 15분
- **자동 롤백**: 비활성화

### 3. 보안 중심 워크플로우 (security_focus)
- **설명**: 보안 검사에 중점을 둔 배포
- **단계**: validation → security_scan → build → test → deploy
- **타임아웃**: 30분
- **자동 롤백**: 활성화

### 4. 테스트 전용 워크플로우 (testing_only)
- **설명**: 배포 없이 테스트만 실행
- **단계**: validation → build → test
- **타임아웃**: 20분
- **자동 롤백**: 비활성화

## 워크플로우 단계 상세

### 1. 검증 (Validation)
```python
async def _execute_validation(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
    """플러그인 검증 단계"""
    # 필수 파일 검증
    required_files = ["config/plugin.json", "backend/plugin.py"]
    
    # 설정 파일 검증
    config_file = plugin_path / "config/plugin.json"
    config = json.loads(config_content)
    
    # 코드 문법 검증
    await self._validate_python_syntax(execution, plugin_path)
```

**검증 항목:**
- 필수 파일 존재 여부
- 설정 파일 형식 및 필수 필드
- Python 코드 문법 검사
- 플러그인 구조 검증

### 2. 빌드 (Build)
```python
async def _execute_build(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
    """플러그인 빌드 단계"""
    # 빌드 디렉토리 생성
    build_dir = plugin_path / "build"
    
    # 플러그인 패키징
    package_path = build_dir / f"{plugin_name}.zip"
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in plugin_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                arcname = file_path.relative_to(plugin_path)
                zipf.write(file_path, arcname)
```

**빌드 과정:**
- 빌드 디렉토리 생성
- 플러그인 파일 패키징
- ZIP 파일 생성
- 빌드 아티팩트 저장

### 3. 테스트 (Test)
```python
async def _execute_test(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
    """플러그인 테스트 단계"""
    # 테스트 파일 검색
    test_files = list(plugin_path.rglob("test_*.py"))
    
    # 테스트 실행
    for test_file in test_files:
        result = await self._run_python_test(execution, test_file)
        test_results.append(result)
```

**테스트 과정:**
- 테스트 파일 자동 검색
- pytest를 사용한 테스트 실행
- 테스트 결과 수집
- 실패 시 워크플로우 중단

### 4. 보안 스캔 (Security Scan)
```python
async def _execute_security_scan(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
    """보안 스캔 단계"""
    # Python 파일 보안 검사
    python_files = list(plugin_path.rglob("*.py"))
    
    for py_file in python_files:
        issues = await self._scan_python_security(execution, py_file)
        security_issues.extend(issues)
```

**보안 검사 항목:**
- eval, exec 함수 사용 검사
- __import__ 함수 사용 검사
- subprocess.Popen 사용 검사
- os.system 사용 검사
- input 함수 사용 검사

### 5. 배포 (Deploy)
```python
async def _execute_deploy(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
    """플러그인 배포 단계"""
    # 배포 디렉토리로 복사
    deploy_dir = self.base_path / "deployed" / execution.plugin_id
    
    # 기존 배포 백업
    if deploy_dir.exists():
        backup_dir = deploy_dir.parent / f"{execution.plugin_id}_backup_{int(time.time())}"
        shutil.move(str(deploy_dir), str(backup_dir))
    
    # 새 버전 배포
    shutil.copytree(plugin_path, deploy_dir, dirs_exist_ok=True)
```

**배포 과정:**
- 기존 배포 백업
- 새 버전 배포
- 배포 로그 생성
- 배포 상태 업데이트

### 6. 모니터링 (Monitor)
```python
async def _execute_monitor(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
    """모니터링 단계"""
    # 플러그인 상태 확인
    deploy_path = Path(execution.artifacts.get("deploy_path", ""))
    
    # 기본 상태 정보 수집
    status_info = {
        "deployed_at": datetime.now().isoformat(),
        "plugin_size": sum(f.stat().st_size for f in deploy_path.rglob('*') if f.is_file()),
        "file_count": len(list(deploy_path.rglob('*'))),
        "status": "active"
    }
```

**모니터링 항목:**
- 배포 상태 확인
- 플러그인 크기 및 파일 수
- 실행 상태 정보
- 성능 메트릭 수집

### 7. 롤백 (Rollback)
```python
async def _execute_rollback(self, execution: WorkflowExecution, plugin_path: Path):
    """롤백 단계"""
    backup_path = execution.artifacts.get("backup_path")
    if backup_path and Path(backup_path).exists():
        deploy_dir = self.base_path / "deployed" / execution.plugin_id
        if deploy_dir.exists():
            shutil.rmtree(deploy_dir)
        shutil.move(backup_path, str(deploy_dir))
```

**롤백 과정:**
- 백업 파일 확인
- 현재 배포 제거
- 이전 버전 복원
- 롤백 로그 생성

## 사용 예시

### 1. 워크플로우 생성
```python
from core.backend.plugin_automation_workflow import WorkflowConfig, WorkflowStep

# 커스텀 워크플로우 생성
config = WorkflowConfig(
    name="프로덕션 배포 워크플로우",
    description="프로덕션 환경 배포용 워크플로우",
    steps=[
        WorkflowStep.VALIDATION,
        WorkflowStep.SECURITY_SCAN,
        WorkflowStep.BUILD,
        WorkflowStep.TEST,
        WorkflowStep.DEPLOY,
        WorkflowStep.MONITOR
    ],
    timeout_minutes=60,
    auto_rollback=True,
    notification_channels=["email", "slack"]
)

# 워크플로우 등록
await workflow_manager.create_workflow("production_deploy", config)
```

### 2. 워크플로우 실행
```python
# 워크플로우 실행
execution_id = await workflow_manager.execute_workflow(
    "production_deploy",
    "my_plugin",
    {
        "environment": "production",
        "version": "2.0.0",
        "notify_on_complete": True
    }
)

# 실행 상태 확인
execution = await workflow_manager.get_execution(execution_id)
print(f"상태: {execution.status}")
print(f"현재 단계: {execution.current_step}")
```

### 3. 실행 로그 확인
```python
# 실행 로그 조회
logs = await workflow_manager.get_execution_logs(execution_id)
for log in logs:
    print(f"[{log['timestamp']}] {log['level']}: {log['message']}")
```

### 4. 통계 정보 조회
```python
# 워크플로우 통계
stats = await workflow_manager.get_workflow_statistics()
print(f"총 실행 수: {stats['total_executions']}")
print(f"성공률: {stats['success_rate']:.1f}%")
print(f"평균 실행 시간: {stats['average_duration']:.1f}분")
```

## 프론트엔드 사용법

### 1. 대시보드 접근
```
http://localhost:3000/plugin-automation
```

### 2. 워크플로우 관리
- **워크플로우 목록**: 등록된 모든 워크플로우 확인
- **워크플로우 생성**: 새 워크플로우 정의 및 등록
- **워크플로우 편집**: 기존 워크플로우 수정
- **워크플로우 삭제**: 불필요한 워크플로우 제거

### 3. 실행 관리
- **빠른 실행**: 워크플로우와 플러그인 선택 후 즉시 실행
- **실행 모니터링**: 실시간 실행 상태 확인
- **로그 확인**: 상세한 실행 로그 조회
- **실행 취소**: 진행 중인 워크플로우 중단

### 4. 통계 및 분석
- **성공률 분석**: 워크플로우별 성공률 확인
- **실행 시간 분석**: 평균 실행 시간 및 성능 분석
- **상태 분포**: 실행 상태별 분포 확인

## 설정 및 환경 변수

### 1. 워크플로우 설정
```json
{
  "timeout_minutes": 30,
  "auto_rollback": true,
  "parallel_execution": false,
  "notification_channels": ["email", "webhook"],
  "environment_variables": {
    "PYTHONPATH": "/app/plugins",
    "LOG_LEVEL": "INFO"
  }
}
```

### 2. 알림 설정
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-password"
  },
  "webhook": {
    "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

## 모니터링 및 로깅

### 1. 로그 레벨
- **INFO**: 일반적인 실행 정보
- **WARNING**: 주의가 필요한 상황
- **ERROR**: 오류 발생
- **DEBUG**: 디버깅 정보

### 2. 로그 형식
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "level": "info",
  "message": "플러그인 검증 시작",
  "step": "validation",
  "execution_id": "workflow_123",
  "plugin_id": "my_plugin"
}
```

### 3. 모니터링 메트릭
- 워크플로우 실행 수
- 성공률
- 평균 실행 시간
- 실패 원인 분석
- 리소스 사용량

## 보안 고려사항

### 1. 코드 실행 보안
- 샌드박스 환경에서 테스트 실행
- 위험한 함수 사용 제한
- 실행 권한 제한

### 2. 데이터 보안
- 민감한 정보 암호화
- 로그 데이터 보호
- 접근 권한 관리

### 3. 네트워크 보안
- API 인증 및 권한 확인
- HTTPS 통신 강제
- 요청 제한 및 속도 제한

## 성능 최적화

### 1. 병렬 실행
- 독립적인 단계 병렬 처리
- 리소스 사용량 최적화
- 실행 시간 단축

### 2. 캐싱
- 빌드 결과 캐싱
- 의존성 캐싱
- 중복 작업 방지

### 3. 리소스 관리
- 메모리 사용량 제한
- CPU 사용량 제한
- 디스크 공간 관리

## 문제 해결

### 1. 일반적인 문제

#### 워크플로우 실행 실패
```bash
# 로그 확인
curl -X GET "http://localhost:5000/api/plugin-automation/executions/{execution_id}/logs"

# 실행 상태 확인
curl -X GET "http://localhost:5000/api/plugin-automation/executions/{execution_id}"
```

#### 플러그인 검증 실패
- 필수 파일 존재 여부 확인
- 설정 파일 형식 검사
- Python 문법 오류 확인

#### 보안 스캔 실패
- 위험한 함수 사용 여부 확인
- 보안 정책 준수 여부 검사
- 권한 설정 확인

### 2. 디버깅 방법

#### 로그 분석
```python
# 상세 로그 확인
logs = await workflow_manager.get_execution_logs(execution_id)
for log in logs:
    if log['level'] == 'error':
        print(f"오류: {log['message']}")
```

#### 단계별 실행
```python
# 특정 단계만 실행
await workflow_manager._execute_validation(execution, plugin_path, {})
```

### 3. 성능 문제 해결

#### 실행 시간 최적화
- 불필요한 단계 제거
- 병렬 실행 활성화
- 캐싱 활용

#### 리소스 사용량 최적화
- 동시 실행 수 제한
- 메모리 사용량 모니터링
- 디스크 공간 정리

## 확장 및 커스터마이징

### 1. 새로운 단계 추가
```python
class CustomWorkflowStep(WorkflowStep):
    CUSTOM_STEP = "custom_step"

async def _execute_custom_step(self, execution: WorkflowExecution, plugin_path: Path, parameters: Dict[str, Any]):
    """커스텀 단계 실행"""
    await self._log_step(execution, "커스텀 단계 시작")
    # 커스텀 로직 구현
    await self._log_step(execution, "커스텀 단계 완료")
```

### 2. 알림 채널 확장
```python
async def send_slack_notification(self, message: str, channel: str):
    """Slack 알림 전송"""
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK"
    payload = {
        "text": message,
        "channel": channel
    }
    # HTTP 요청 구현
```

### 3. 외부 시스템 연동
```python
async def integrate_with_ci_cd(self, execution: WorkflowExecution):
    """CI/CD 시스템 연동"""
    # Jenkins, GitLab CI, GitHub Actions 등과 연동
    pass
```

## 결론

플러그인 자동화 및 워크플로우 시스템은 플러그인 개발과 배포 과정을 완전히 자동화하여 개발 효율성을 크게 향상시킵니다. 표준화된 워크플로우를 통해 일관성 있는 배포 프로세스를 구축하고, 실시간 모니터링을 통해 안정적인 운영을 보장합니다.

이 시스템을 통해 플러그인 개발자는 복잡한 배포 과정에 신경 쓰지 않고 핵심 기능 개발에 집중할 수 있으며, 운영자는 안정적이고 예측 가능한 배포 프로세스를 통해 시스템 안정성을 확보할 수 있습니다. 