"""
고급 워크플로우 엔진
복잡한 비즈니스 프로세스를 자동화하고 관리하는 시스템
"""

import json
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
import queue
import concurrent.futures

# 로깅 설정
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """워크플로우 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskStatus(Enum):
    """태스크 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class TaskType(Enum):
    """태스크 타입"""
    FUNCTION = "function"
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    FILE_OPERATION = "file_operation"
    EMAIL = "email"
    NOTIFICATION = "notification"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    DELAY = "delay"

@dataclass
class WorkflowDefinition:
    """워크플로우 정의"""
    id: str
    name: str
    description: str
    version: str
    created_at: datetime
    updated_at: datetime
    tasks: List[Dict[str, Any]]
    variables: Dict[str, Any]
    triggers: List[Dict[str, Any]]
    timeout: int = 3600  # 초 단위
    retry_count: int = 3
    retry_delay: int = 60

@dataclass
class WorkflowInstance:
    """워크플로우 인스턴스"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime]
    variables: Dict[str, Any]
    current_task: Optional[str]
    error_message: Optional[str]
    created_by: str
    metadata: Dict[str, Any]

@dataclass
class TaskInstance:
    """태스크 인스턴스"""
    id: str
    workflow_instance_id: str
    task_id: str
    name: str
    task_type: TaskType
    status: TaskStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Any]
    error_message: Optional[str]
    retry_count: int = 0
    max_retries: int = 3

class WorkflowEngine:
    """고급 워크플로우 엔진"""
    
    def __init__(self, db_path: str = "data/integration/workflows.db"):
        self.db_path = db_path
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.task_queue = queue.Queue()
        self.running_workflows: Dict[str, WorkflowInstance] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.task_handlers: Dict[TaskType, Callable] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 초기화
        self.initialize_database()
        
        # 기본 태스크 핸들러 등록
        self.register_default_handlers()
        
        # 워크플로우 실행 스레드 시작
        self.start_worker_thread()
    
    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 워크플로우 정의 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_definitions (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        version TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        tasks TEXT NOT NULL,
                        variables TEXT NOT NULL,
                        triggers TEXT NOT NULL,
                        timeout INTEGER DEFAULT 3600,
                        retry_count INTEGER DEFAULT 3,
                        retry_delay INTEGER DEFAULT 60
                    )
                """)
                
                # 워크플로우 인스턴스 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_instances (
                        id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        completed_at TEXT,
                        variables TEXT NOT NULL,
                        current_task TEXT,
                        error_message TEXT,
                        created_by TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        FOREIGN KEY (workflow_id) REFERENCES workflow_definitions (id)
                    )
                """)
                
                # 태스크 인스턴스 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS task_instances (
                        id TEXT PRIMARY KEY,
                        workflow_instance_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        task_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        started_at TEXT,
                        completed_at TEXT,
                        result TEXT,
                        error_message TEXT,
                        retry_count INTEGER DEFAULT 0,
                        max_retries INTEGER DEFAULT 3,
                        FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances (id)
                    )
                """)
                
                # 워크플로우 실행 로그 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workflow_instance_id TEXT NOT NULL,
                        task_instance_id TEXT,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances (id),
                        FOREIGN KEY (task_instance_id) REFERENCES task_instances (id)
                    )
                """)
                
                conn.commit()
                logger.info("워크플로우 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
            raise
    
    def register_default_handlers(self):
        """기본 태스크 핸들러 등록"""
        self.register_task_handler(TaskType.FUNCTION, self._execute_function_task)
        self.register_task_handler(TaskType.HTTP_REQUEST, self._execute_http_task)
        self.register_task_handler(TaskType.DATABASE_QUERY, self._execute_database_task)
        self.register_task_handler(TaskType.FILE_OPERATION, self._execute_file_task)
        self.register_task_handler(TaskType.EMAIL, self._execute_email_task)
        self.register_task_handler(TaskType.NOTIFICATION, self._execute_notification_task)
        self.register_task_handler(TaskType.CONDITION, self._execute_condition_task)
        self.register_task_handler(TaskType.LOOP, self._execute_loop_task)
        self.register_task_handler(TaskType.PARALLEL, self._execute_parallel_task)
        self.register_task_handler(TaskType.DELAY, self._execute_delay_task)
    
    def register_task_handler(self, task_type: TaskType, handler: Callable):
        """태스크 핸들러 등록"""
        self.task_handlers[task_type] = handler
        logger.info(f"태스크 핸들러 등록: {task_type.value}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """이벤트 핸들러 등록"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"이벤트 핸들러 등록: {event_type}")
    
    def create_workflow_definition(self, name: str, description: str, tasks: List[Dict], 
                                 variables: Dict = None, triggers: List[Dict] = None,
                                 timeout: int = 3600, retry_count: int = 3, retry_delay: int = 60) -> str:
        """워크플로우 정의 생성"""
        try:
            workflow_id = str(uuid.uuid4())
            now = datetime.now()
            
            definition = WorkflowDefinition(
                id=workflow_id,
                name=name,
                description=description,
                version="1.0.0",
                created_at=now,
                updated_at=now,
                tasks=tasks,
                variables=variables or {},
                triggers=triggers or [],
                timeout=timeout,
                retry_count=retry_count,
                retry_delay=retry_delay
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO workflow_definitions 
                    (id, name, description, version, created_at, updated_at, tasks, variables, triggers, timeout, retry_count, retry_delay)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    definition.id, definition.name, definition.description, definition.version,
                    definition.created_at.isoformat(), definition.updated_at.isoformat(),
                    json.dumps(definition.tasks), json.dumps(definition.variables),
                    json.dumps(definition.triggers), definition.timeout, definition.retry_count, definition.retry_delay
                ))
                conn.commit()
            
            self.workflow_definitions[workflow_id] = definition
            logger.info(f"워크플로우 정의 생성: {workflow_id}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"워크플로우 정의 생성 오류: {str(e)}")
            raise
    
    def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """워크플로우 정의 조회"""
        try:
            if workflow_id in self.workflow_definitions:
                return self.workflow_definitions[workflow_id]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM workflow_definitions WHERE id = ?", (workflow_id,))
                row = cursor.fetchone()
                
                if row:
                    definition = WorkflowDefinition(
                        id=row[0], name=row[1], description=row[2], version=row[3],
                        created_at=datetime.fromisoformat(row[4]),
                        updated_at=datetime.fromisoformat(row[5]),
                        tasks=json.loads(row[6]), variables=json.loads(row[7]),
                        triggers=json.loads(row[8]), timeout=row[9], retry_count=row[10], retry_delay=row[11]
                    )
                    self.workflow_definitions[workflow_id] = definition
                    return definition
                
                return None
                
        except Exception as e:
            logger.error(f"워크플로우 정의 조회 오류: {str(e)}")
            return None
    
    def start_workflow(self, workflow_id: str, variables: Dict = None, created_by: str = "system") -> str:
        """워크플로우 실행 시작"""
        try:
            definition = self.get_workflow_definition(workflow_id)
            if not definition:
                raise ValueError(f"워크플로우 정의를 찾을 수 없습니다: {workflow_id}")
            
            instance_id = str(uuid.uuid4())
            now = datetime.now()
            
            instance = WorkflowInstance(
                id=instance_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                started_at=now,
                completed_at=None,
                variables=variables or {},
                current_task=None,
                error_message=None,
                created_by=created_by,
                metadata={}
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO workflow_instances 
                    (id, workflow_id, status, started_at, completed_at, variables, current_task, error_message, created_by, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    instance.id, instance.workflow_id, instance.status.value,
                    instance.started_at.isoformat(), instance.completed_at.isoformat() if instance.completed_at else None,
                    json.dumps(instance.variables), instance.current_task, instance.error_message,
                    instance.created_by, json.dumps(instance.metadata)
                ))
                conn.commit()
            
            self.running_workflows[instance_id] = instance
            self.task_queue.put(instance_id)
            
            logger.info(f"워크플로우 실행 시작: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"워크플로우 실행 시작 오류: {str(e)}")
            raise
    
    def start_worker_thread(self):
        """워크플로우 실행 워커 스레드 시작"""
        def worker():
            while True:
                try:
                    instance_id = self.task_queue.get(timeout=1)
                    if instance_id:
                        self._execute_workflow(instance_id)
                    self.task_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"워커 스레드 오류: {str(e)}")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        logger.info("워크플로우 워커 스레드 시작")
    
    def _execute_workflow(self, instance_id: str):
        """워크플로우 실행"""
        try:
            instance = self.running_workflows.get(instance_id)
            if not instance:
                return
            
            definition = self.get_workflow_definition(instance.workflow_id)
            if not definition:
                self._update_workflow_status(instance_id, WorkflowStatus.FAILED, "워크플로우 정의를 찾을 수 없습니다")
                return
            
            # 워크플로우 상태를 실행 중으로 변경
            self._update_workflow_status(instance_id, WorkflowStatus.RUNNING)
            
            # 태스크 실행
            for task in definition.tasks:
                if instance.status == WorkflowStatus.CANCELLED:
                    break
                
                task_instance_id = self._execute_task(instance_id, task, instance.variables)
                if task_instance_id:
                    # 태스크 결과를 변수에 저장
                    task_result = self._get_task_result(task_instance_id)
                    if task_result and task.get('output_variable'):
                        instance.variables[task['output_variable']] = task_result
            
            # 워크플로우 완료
            if instance.status != WorkflowStatus.CANCELLED:
                self._update_workflow_status(instance_id, WorkflowStatus.COMPLETED)
            
        except Exception as e:
            logger.error(f"워크플로우 실행 오류: {str(e)}")
            self._update_workflow_status(instance_id, WorkflowStatus.FAILED, str(e))
    
    def _execute_task(self, workflow_instance_id: str, task: Dict, variables: Dict) -> Optional[str]:
        """태스크 실행"""
        try:
            task_id = task.get('id', str(uuid.uuid4()))
            task_type = TaskType(task.get('type', 'function'))
            
            # 태스크 인스턴스 생성
            task_instance = TaskInstance(
                id=str(uuid.uuid4()),
                workflow_instance_id=workflow_instance_id,
                task_id=task_id,
                name=task.get('name', 'Unknown Task'),
                task_type=task_type,
                status=TaskStatus.PENDING,
                started_at=None,
                completed_at=None,
                result=None,
                error_message=None,
                max_retries=task.get('max_retries', 3)
            )
            
            # 태스크 인스턴스 저장
            self._save_task_instance(task_instance)
            
            # 태스크 실행
            handler = self.task_handlers.get(task_type)
            if handler:
                task_instance.started_at = datetime.now()
                task_instance.status = TaskStatus.RUNNING
                self._update_task_instance(task_instance)
                
                try:
                    result = handler(task, variables, task_instance)
                    task_instance.result = result
                    task_instance.status = TaskStatus.COMPLETED
                    task_instance.completed_at = datetime.now()
                    
                except Exception as e:
                    task_instance.error_message = str(e)
                    task_instance.status = TaskStatus.FAILED
                    task_instance.completed_at = datetime.now()
                    
                    # 재시도 로직
                    if task_instance.retry_count < task_instance.max_retries:
                        task_instance.retry_count += 1
                        task_instance.status = TaskStatus.PENDING
                        task_instance.started_at = None
                        task_instance.completed_at = None
                        task_instance.error_message = None
                        # 재시도 큐에 추가
                        time.sleep(task.get('retry_delay', 60))
                        self.task_queue.put(workflow_instance_id)
                
                self._update_task_instance(task_instance)
                return task_instance.id
            
            else:
                logger.error(f"태스크 핸들러를 찾을 수 없습니다: {task_type}")
                return None
                
        except Exception as e:
            logger.error(f"태스크 실행 오류: {str(e)}")
            return None
    
    def _execute_function_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """함수 태스크 실행"""
        function_name = task.get('function')
        if not function_name:
            raise ValueError("함수 이름이 지정되지 않았습니다")
        
        # 전역 함수에서 찾기
        if function_name in globals():
            func = globals()[function_name]
        else:
            raise ValueError(f"함수를 찾을 수 없습니다: {function_name}")
        
        # 매개변수 준비
        params = task.get('parameters', {})
        # 변수 치환
        for key, value in params.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                var_name = value[2:-1]
                params[key] = variables.get(var_name, value)
        
        # 함수 실행
        return func(**params)
    
    def _execute_http_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """HTTP 요청 태스크 실행"""
        import requests
        
        method = task.get('method', 'GET')
        url = task.get('url')
        headers = task.get('headers', {})
        data = task.get('data')
        
        if not url:
            raise ValueError("URL이 지정되지 않았습니다")
        
        # 변수 치환
        url = self._replace_variables(url, variables)
        if data:
            data = self._replace_variables(data, variables)
        
        response = requests.request(method, url, headers=headers, json=data if method in ['POST', 'PUT', 'PATCH'] else None)
        
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': response.text
        }
    
    def _execute_database_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """데이터베이스 쿼리 태스크 실행"""
        query = task.get('query')
        if not query:
            raise ValueError("쿼리가 지정되지 않았습니다")
        
        # 변수 치환
        query = self._replace_variables(query, variables)
        
        # 데이터베이스 연결 및 쿼리 실행
        # 실제 구현에서는 적절한 데이터베이스 연결을 사용
        return {"result": "database_query_executed", "query": query}
    
    def _execute_file_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """파일 작업 태스크 실행"""
        operation = task.get('operation')
        file_path = task.get('file_path')
        
        if not operation or not file_path:
            raise ValueError("작업 또는 파일 경로가 지정되지 않았습니다")
        
        # 변수 치환
        file_path = self._replace_variables(file_path, variables)
        
        if operation == 'read':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif operation == 'write':
            content = task.get('content', '')
            content = self._replace_variables(content, variables)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "written", "file_path": file_path}
        elif operation == 'delete':
            import os
            os.remove(file_path)
            return {"status": "deleted", "file_path": file_path}
        else:
            raise ValueError(f"지원하지 않는 파일 작업: {operation}")
    
    def _execute_email_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """이메일 태스크 실행"""
        # 이메일 발송 로직 구현
        to_email = task.get('to')
        subject = task.get('subject')
        body = task.get('body')
        
        # 변수 치환
        to_email = self._replace_variables(to_email, variables)
        subject = self._replace_variables(subject, variables)
        body = self._replace_variables(body, variables)
        
        # 실제 이메일 발송 구현
        return {"status": "sent", "to": to_email, "subject": subject}
    
    def _execute_notification_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """알림 태스크 실행"""
        message = task.get('message')
        channel = task.get('channel', 'system')
        
        # 변수 치환
        message = self._replace_variables(message, variables)
        
        # 알림 발송
        self._emit_event('notification', {
            'channel': channel,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        return {"status": "sent", "channel": channel, "message": message}
    
    def _execute_condition_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """조건 태스크 실행"""
        condition = task.get('condition')
        if_true = task.get('if_true')
        if_false = task.get('if_false')
        
        # 조건 평가
        result = eval(condition, {"__builtins__": {}}, variables)
        
        if result:
            return if_true
        else:
            return if_false
    
    def _execute_loop_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """루프 태스크 실행"""
        items = task.get('items', [])
        loop_task = task.get('task')
        
        results = []
        for item in items:
            # 각 아이템에 대해 태스크 실행
            if loop_task:
                loop_variables = variables.copy()
                loop_variables['item'] = item
                loop_variables['index'] = items.index(item)
                
                # 재귀적으로 태스크 실행
                result = self._execute_task(task_instance.workflow_instance_id, loop_task, loop_variables)
                if result:
                    results.append(result)
        
        return results
    
    def _execute_parallel_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """병렬 태스크 실행"""
        tasks = task.get('tasks', [])
        
        # 병렬 실행
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for task_def in tasks:
                future = executor.submit(self._execute_task, task_instance.workflow_instance_id, task_def, variables)
                futures.append(future)
            
            # 결과 수집
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"병렬 태스크 실행 오류: {str(e)}")
                    results.append(None)
        
        return results
    
    def _execute_delay_task(self, task: Dict, variables: Dict, task_instance: TaskInstance):
        """지연 태스크 실행"""
        delay_seconds = task.get('seconds', 1)
        
        # 변수 치환
        if isinstance(delay_seconds, str):
            delay_seconds = int(self._replace_variables(delay_seconds, variables))
        
        time.sleep(delay_seconds)
        return {"delayed_seconds": delay_seconds}
    
    def _replace_variables(self, text: str, variables: Dict) -> str:
        """변수 치환"""
        if not isinstance(text, str):
            return text
        
        for key, value in variables.items():
            placeholder = f"${{{key}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(value))
        
        return text
    
    def _save_task_instance(self, task_instance: TaskInstance):
        """태스크 인스턴스 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO task_instances 
                    (id, workflow_instance_id, task_id, name, task_type, status, started_at, completed_at, result, error_message, retry_count, max_retries)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_instance.id, task_instance.workflow_instance_id, task_instance.task_id,
                    task_instance.name, task_instance.task_type.value, task_instance.status.value,
                    task_instance.started_at.isoformat() if task_instance.started_at else None,
                    task_instance.completed_at.isoformat() if task_instance.completed_at else None,
                    json.dumps(task_instance.result) if task_instance.result else None,
                    task_instance.error_message, task_instance.retry_count, task_instance.max_retries
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"태스크 인스턴스 저장 오류: {str(e)}")
    
    def _update_task_instance(self, task_instance: TaskInstance):
        """태스크 인스턴스 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE task_instances 
                    SET status = ?, started_at = ?, completed_at = ?, result = ?, error_message = ?, retry_count = ?
                    WHERE id = ?
                """, (
                    task_instance.status.value,
                    task_instance.started_at.isoformat() if task_instance.started_at else None,
                    task_instance.completed_at.isoformat() if task_instance.completed_at else None,
                    json.dumps(task_instance.result) if task_instance.result else None,
                    task_instance.error_message, task_instance.retry_count, task_instance.id
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"태스크 인스턴스 업데이트 오류: {str(e)}")
    
    def _update_workflow_status(self, instance_id: str, status: WorkflowStatus, error_message: str = None):
        """워크플로우 상태 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE workflow_instances 
                    SET status = ?, completed_at = ?, error_message = ?
                    WHERE id = ?
                """, (
                    status.value,
                    datetime.now().isoformat() if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED] else None,
                    error_message, instance_id
                ))
                conn.commit()
            
            # 메모리에서도 업데이트
            if instance_id in self.running_workflows:
                self.running_workflows[instance_id].status = status
                if error_message:
                    self.running_workflows[instance_id].error_message = error_message
                if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                    self.running_workflows[instance_id].completed_at = datetime.now()
            
            # 이벤트 발생
            self._emit_event('workflow_status_changed', {
                'instance_id': instance_id,
                'status': status.value,
                'error_message': error_message
            })
            
        except Exception as e:
            logger.error(f"워크플로우 상태 업데이트 오류: {str(e)}")
    
    def _get_task_result(self, task_instance_id: str):
        """태스크 결과 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT result FROM task_instances WHERE id = ?", (task_instance_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    return json.loads(row[0])
                return None
        except Exception as e:
            logger.error(f"태스크 결과 조회 오류: {str(e)}")
            return None
    
    def _emit_event(self, event_type: str, data: Dict):
        """이벤트 발생"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"이벤트 핸들러 오류: {str(e)}")
    
    def get_workflow_instances(self, workflow_id: str = None, status: WorkflowStatus = None, 
                             limit: int = 100, offset: int = 0) -> List[WorkflowInstance]:
        """워크플로우 인스턴스 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM workflow_instances WHERE 1=1"
                params = []
                
                if workflow_id:
                    query += " AND workflow_id = ?"
                    params.append(workflow_id)
                
                if status:
                    query += " AND status = ?"
                    params.append(status.value)
                
                query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                instances = []
                for row in rows:
                    instance = WorkflowInstance(
                        id=row[0], workflow_id=row[1], status=WorkflowStatus(row[2]),
                        started_at=datetime.fromisoformat(row[3]),
                        completed_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        variables=json.loads(row[5]), current_task=row[6],
                        error_message=row[7], created_by=row[8], metadata=json.loads(row[9])
                    )
                    instances.append(instance)
                
                return instances
                
        except Exception as e:
            logger.error(f"워크플로우 인스턴스 조회 오류: {str(e)}")
            return []
    
    def cancel_workflow(self, instance_id: str) -> bool:
        """워크플로우 취소"""
        try:
            if instance_id in self.running_workflows:
                self._update_workflow_status(instance_id, WorkflowStatus.CANCELLED)
                return True
            return False
        except Exception as e:
            logger.error(f"워크플로우 취소 오류: {str(e)}")
            return False
    
    def get_workflow_statistics(self) -> Dict:
        """워크플로우 통계 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 전체 워크플로우 수
                cursor.execute("SELECT COUNT(*) FROM workflow_instances")
                total_workflows = cursor.fetchone()[0]
                
                # 상태별 워크플로우 수
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM workflow_instances 
                    GROUP BY status
                """)
                status_counts = dict(cursor.fetchall())
                
                # 오늘 실행된 워크플로우 수
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM workflow_instances 
                    WHERE DATE(started_at) = DATE('now')
                """)
                today_workflows = cursor.fetchone()[0]
                
                # 평균 실행 시간
                cursor.execute("""
                    SELECT AVG((julianday(completed_at) - julianday(started_at)) * 24 * 60 * 60)
                    FROM workflow_instances 
                    WHERE completed_at IS NOT NULL
                """)
                avg_duration = cursor.fetchone()[0] or 0
                
                return {
                    'total_workflows': total_workflows,
                    'status_counts': status_counts,
                    'today_workflows': today_workflows,
                    'avg_duration_seconds': avg_duration,
                    'running_workflows': len(self.running_workflows)
                }
                
        except Exception as e:
            logger.error(f"워크플로우 통계 조회 오류: {str(e)}")
            return {}
    
    def cleanup_old_workflows(self, days: int = 30):
        """오래된 워크플로우 정리"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 오래된 워크플로우 인스턴스 삭제
                cursor.execute("""
                    DELETE FROM workflow_instances 
                    WHERE started_at < datetime('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"오래된 워크플로우 {deleted_count}개 정리 완료")
                return deleted_count
                
        except Exception as e:
            logger.error(f"워크플로우 정리 오류: {str(e)}")
            return 0 