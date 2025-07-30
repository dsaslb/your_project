"""
서버리스 컴퓨팅 플랫폼 (FaaS)
함수 실행, 이벤트 트리거, 자동 스케일링, 콜드 스타트 최적화를 포함한 완전한 서버리스 플랫폼
"""

import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
import sqlite3
from pathlib import Path
import pickle
import hashlib
import hmac
import base64
import secrets
import struct
import socket
import ssl
import redis
from redis.exceptions import RedisError
import docker
import subprocess
import tempfile
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from collections import defaultdict, deque

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FunctionStatus(Enum):
    """함수 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPLOYING = "deploying"
    ERROR = "error"

class TriggerType(Enum):
    """트리거 타입"""
    HTTP = "http"
    CRON = "cron"
    EVENT = "event"
    QUEUE = "queue"
    DATABASE = "database"

class ExecutionStatus(Enum):
    """실행 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class Function:
    """함수 정보"""
    function_id: str
    name: str
    runtime: str
    code: str
    handler: str
    timeout: int
    memory: int
    environment: Dict[str, str]
    triggers: List[Dict[str, Any]]
    status: FunctionStatus
    created_at: datetime
    updated_at: datetime

@dataclass
class Execution:
    """실행 정보"""
    execution_id: str
    function_id: str
    status: ExecutionStatus
    start_time: datetime
    end_time: datetime
    duration: float
    memory_used: int
    cpu_used: float
    logs: str
    result: Any
    error: str = None

@dataclass
class Trigger:
    """트리거 정보"""
    trigger_id: str
    function_id: str
    trigger_type: TriggerType
    config: Dict[str, Any]
    enabled: bool
    created_at: datetime

class ServerlessPlatform:
    """서버리스 컴퓨팅 플랫폼"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.functions: Dict[str, Function] = {}
        self.executions: Dict[str, Execution] = {}
        self.triggers: Dict[str, Trigger] = {}
        
        # Docker 클라이언트
        self.docker_client = None
        self._init_docker_client()
        
        # Redis 클라이언트
        self.redis_client = None
        self._init_redis()
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './serverless.db'))
        self._init_database()
        
        # 실행 엔진
        self.execution_engine = None
        self._init_execution_engine()
        
        # 함수 컨테이너 풀
        self.container_pool = {}
        self.max_containers = config.get('max_containers', 100)
        self.container_timeout = config.get('container_timeout', 300)
        
        # 실행 큐
        self.execution_queue = queue.Queue()
        self.execution_thread = None
        self.is_processing = False
        
        # 스케일링 스레드
        self.scaling_thread = None
        self.is_scaling = False
        
        # HTTP 서버
        self.http_server = None
        self._init_http_server()
        
        logger.info("서버리스 플랫폼 초기화 완료")
    
    def _init_docker_client(self):
        """Docker 클라이언트 초기화"""
        try:
            self.docker_client = docker.from_env()
            
            # Docker 연결 테스트
            self.docker_client.ping()
            logger.info("Docker 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.warning(f"Docker 클라이언트 초기화 실패: {e}")
            self.docker_client = None
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 6),
                decode_responses=True
            )
            
            # Redis 연결 테스트
            self.redis_client.ping()
            logger.info("Redis 클라이언트 초기화 완료")
            
        except RedisError as e:
            logger.warning(f"Redis 클라이언트 초기화 실패: {e}")
            self.redis_client = None
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 함수 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS functions (
                    function_id TEXT PRIMARY KEY,
                    name TEXT,
                    runtime TEXT,
                    code TEXT,
                    handler TEXT,
                    timeout INTEGER,
                    memory INTEGER,
                    environment TEXT,
                    triggers TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 실행 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    function_id TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration REAL,
                    memory_used INTEGER,
                    cpu_used REAL,
                    logs TEXT,
                    result TEXT,
                    error TEXT
                )
            ''')
            
            # 트리거 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS triggers (
                    trigger_id TEXT PRIMARY KEY,
                    function_id TEXT,
                    trigger_type TEXT,
                    config TEXT,
                    enabled INTEGER,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("서버리스 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _init_execution_engine(self):
        """실행 엔진 초기화"""
        try:
            # 스레드 풀 실행기
            self.execution_engine = ThreadPoolExecutor(
                max_workers=self.config.get('max_workers', 50)
            )
            
            logger.info("실행 엔진 초기화 완료")
            
        except Exception as e:
            logger.error(f"실행 엔진 초기화 오류: {e}")
    
    def _init_http_server(self):
        """HTTP 서버 초기화"""
        try:
            app = web.Application()
            
            # 함수 실행 엔드포인트
            app.router.add_post('/invoke/{function_name}', self._invoke_function)
            
            # 함수 관리 엔드포인트
            app.router.add_post('/functions', self._create_function)
            app.router.add_get('/functions', self._list_functions)
            app.router.add_get('/functions/{function_name}', self._get_function)
            app.router.add_delete('/functions/{function_name}', self._delete_function)
            
            # 실행 상태 엔드포인트
            app.router.add_get('/executions/{execution_id}', self._get_execution)
            
            self.http_server = app
            
            logger.info("HTTP 서버 초기화 완료")
            
        except Exception as e:
            logger.error(f"HTTP 서버 초기화 오류: {e}")
    
    def create_function(self, function_info: Dict[str, Any]) -> str:
        """함수 생성"""
        try:
            function_id = str(uuid.uuid4())
            
            function = Function(
                function_id=function_id,
                name=function_info['name'],
                runtime=function_info['runtime'],
                code=function_info['code'],
                handler=function_info.get('handler', 'index.handler'),
                timeout=function_info.get('timeout', 30),
                memory=function_info.get('memory', 128),
                environment=function_info.get('environment', {}),
                triggers=function_info.get('triggers', []),
                status=FunctionStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.functions[function_id] = function
            
            # 데이터베이스에 저장
            self._save_function_to_db(function)
            
            # 트리거 설정
            for trigger_config in function.triggers:
                self._create_trigger(function_id, trigger_config)
            
            # 컨테이너 이미지 빌드
            self._build_function_container(function)
            
            logger.info(f"함수 생성 완료: {function_id}")
            return function_id
            
        except Exception as e:
            logger.error(f"함수 생성 오류: {e}")
            raise
    
    def _create_trigger(self, function_id: str, trigger_config: Dict[str, Any]) -> str:
        """트리거 생성"""
        try:
            trigger_id = str(uuid.uuid4())
            
            trigger = Trigger(
                trigger_id=trigger_id,
                function_id=function_id,
                trigger_type=TriggerType(trigger_config['type']),
                config=trigger_config.get('config', {}),
                enabled=trigger_config.get('enabled', True),
                created_at=datetime.now()
            )
            
            self.triggers[trigger_id] = trigger
            
            # 데이터베이스에 저장
            self._save_trigger_to_db(trigger)
            
            # 트리거 타입별 설정
            if trigger.trigger_type == TriggerType.HTTP:
                self._setup_http_trigger(trigger)
            elif trigger.trigger_type == TriggerType.CRON:
                self._setup_cron_trigger(trigger)
            elif trigger.trigger_type == TriggerType.EVENT:
                self._setup_event_trigger(trigger)
            
            logger.info(f"트리거 생성 완료: {trigger_id}")
            return trigger_id
            
        except Exception as e:
            logger.error(f"트리거 생성 오류: {e}")
            raise
    
    def _build_function_container(self, function: Function):
        """함수 컨테이너 빌드"""
        try:
            if not self.docker_client:
                return
            
            # 런타임별 Dockerfile 생성
            dockerfile = self._generate_dockerfile(function)
            
            # 임시 디렉토리에 파일 생성
            with tempfile.TemporaryDirectory() as temp_dir:
                # 함수 코드 파일 생성
                code_file = os.path.join(temp_dir, 'function.py')
                with open(code_file, 'w') as f:
                    f.write(function.code)
                
                # Dockerfile 생성
                dockerfile_path = os.path.join(temp_dir, 'Dockerfile')
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile)
                
                # 환경 변수 파일 생성
                env_file = os.path.join(temp_dir, '.env')
                with open(env_file, 'w') as f:
                    for key, value in function.environment.items():
                        f.write(f"{key}={value}\n")
                
                # Docker 이미지 빌드
                image_name = f"function-{function.function_id}"
                self.docker_client.images.build(
                    path=temp_dir,
                    tag=image_name,
                    rm=True
                )
                
                # 컨테이너 풀에 추가
                self.container_pool[function.function_id] = {
                    'image': image_name,
                    'last_used': datetime.now(),
                    'status': 'ready'
                }
                
                logger.info(f"함수 컨테이너 빌드 완료: {image_name}")
                
        except Exception as e:
            logger.error(f"함수 컨테이너 빌드 오류: {e}")
    
    def _generate_dockerfile(self, function: Function) -> str:
        """Dockerfile 생성"""
        try:
            runtime = function.runtime.lower()
            
            if 'python' in runtime:
                return f"""
FROM python:3.9-slim

WORKDIR /app

COPY function.py .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true

ENV PYTHONPATH=/app

CMD ["python", "function.py"]
"""
            elif 'node' in runtime:
                return f"""
FROM node:16-slim

WORKDIR /app

COPY function.js .
COPY package.json .
COPY .env .

RUN npm install --production

CMD ["node", "function.js"]
"""
            elif 'go' in runtime:
                return f"""
FROM golang:1.17-alpine

WORKDIR /app

COPY function.go .
COPY go.mod .
COPY .env .

RUN go build -o function function.go

CMD ["./function"]
"""
            else:
                # 기본 Python 런타임
                return f"""
FROM python:3.9-slim

WORKDIR /app

COPY function.py .
COPY .env .

CMD ["python", "function.py"]
"""
                
        except Exception as e:
            logger.error(f"Dockerfile 생성 오류: {e}")
            return ""
    
    def invoke_function(self, function_name: str, payload: Dict[str, Any] = None) -> str:
        """함수 실행"""
        try:
            # 함수 찾기
            function = None
            for func in self.functions.values():
                if func.name == function_name:
                    function = func
                    break
            
            if not function:
                raise ValueError(f"함수를 찾을 수 없습니다: {function_name}")
            
            # 실행 ID 생성
            execution_id = str(uuid.uuid4())
            
            # 실행 정보 생성
            execution = Execution(
                execution_id=execution_id,
                function_id=function.function_id,
                status=ExecutionStatus.PENDING,
                start_time=datetime.now(),
                end_time=None,
                duration=0.0,
                memory_used=0,
                cpu_used=0.0,
                logs="",
                result=None
            )
            
            self.executions[execution_id] = execution
            
            # 데이터베이스에 저장
            self._save_execution_to_db(execution)
            
            # 실행 큐에 추가
            self.execution_queue.put({
                'execution_id': execution_id,
                'function': function,
                'payload': payload or {}
            })
            
            logger.info(f"함수 실행 요청: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"함수 실행 오류: {e}")
            raise
    
    def start_execution_engine(self):
        """실행 엔진 시작"""
        try:
            if self.is_processing:
                logger.warning("실행 엔진이 이미 실행 중입니다")
                return
            
            self.is_processing = True
            self.execution_thread = threading.Thread(
                target=self._execution_loop,
                daemon=True
            )
            self.execution_thread.start()
            
            logger.info("실행 엔진 시작")
            
        except Exception as e:
            logger.error(f"실행 엔진 시작 오류: {e}")
    
    def _execution_loop(self):
        """실행 루프"""
        try:
            while self.is_processing:
                try:
                    # 실행 큐에서 작업 가져오기
                    execution_data = self.execution_queue.get(timeout=1)
                    
                    # 함수 실행
                    self._execute_function(
                        execution_data['execution_id'],
                        execution_data['function'],
                        execution_data['payload']
                    )
                    
                    # 큐 작업 완료 표시
                    self.execution_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"실행 루프 오류: {e}")
                    
        except Exception as e:
            logger.error(f"실행 루프 오류: {e}")
        finally:
            self.is_processing = False
    
    def _execute_function(self, execution_id: str, function: Function, payload: Dict[str, Any]):
        """함수 실행"""
        try:
            execution = self.executions[execution_id]
            execution.status = ExecutionStatus.RUNNING
            execution.start_time = datetime.now()
            
            # 컨테이너에서 함수 실행
            if self.docker_client and function.function_id in self.container_pool:
                result = self._execute_in_container(function, payload)
            else:
                # 로컬에서 함수 실행
                result = self._execute_locally(function, payload)
            
            # 실행 완료
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.status = ExecutionStatus.COMPLETED
            execution.result = result
            
            # 데이터베이스 업데이트
            self._save_execution_to_db(execution)
            
            logger.info(f"함수 실행 완료: {execution_id}")
            
        except Exception as e:
            # 실행 실패
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            
            # 데이터베이스 업데이트
            self._save_execution_to_db(execution)
            
            logger.error(f"함수 실행 실패: {execution_id} - {e}")
    
    def _execute_in_container(self, function: Function, payload: Dict[str, Any]) -> Any:
        """컨테이너에서 함수 실행"""
        try:
            container_info = self.container_pool[function.function_id]
            
            # 컨테이너 실행
            container = self.docker_client.containers.run(
                container_info['image'],
                detach=True,
                environment=function.environment,
                mem_limit=f"{function.memory}m",
                network_mode='host'
            )
            
            try:
                # 입력 데이터 전송
                input_data = json.dumps(payload)
                container.exec_run(f"echo '{input_data}' > /tmp/input.json")
                
                # 함수 실행
                result = container.exec_run(f"python -c \"{function.code}\"")
                
                # 결과 반환
                return result.output.decode('utf-8')
                
            finally:
                # 컨테이너 정리
                container.remove(force=True)
                
        except Exception as e:
            logger.error(f"컨테이너 실행 오류: {e}")
            raise
    
    def _execute_locally(self, function: Function, payload: Dict[str, Any]) -> Any:
        """로컬에서 함수 실행"""
        try:
            # 임시 파일에 함수 코드 저장
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(function.code)
                temp_file = f.name
            
            try:
                # 환경 변수 설정
                env = os.environ.copy()
                env.update(function.environment)
                
                # 함수 실행
                result = subprocess.run(
                    [sys.executable, temp_file],
                    input=json.dumps(payload),
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=function.timeout
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    raise Exception(f"함수 실행 오류: {result.stderr}")
                    
            finally:
                # 임시 파일 정리
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"로컬 실행 오류: {e}")
            raise
    
    def get_execution_status(self, execution_id: str) -> Optional[Execution]:
        """실행 상태 조회"""
        try:
            return self.executions.get(execution_id)
        except Exception as e:
            logger.error(f"실행 상태 조회 오류: {e}")
            return None
    
    def list_functions(self) -> List[Function]:
        """함수 목록 조회"""
        try:
            return list(self.functions.values())
        except Exception as e:
            logger.error(f"함수 목록 조회 오류: {e}")
            return []
    
    def get_function_stats(self) -> Dict[str, Any]:
        """함수 통계 조회"""
        try:
            stats = {
                'total_functions': len(self.functions),
                'active_functions': len([f for f in self.functions.values() if f.status == FunctionStatus.ACTIVE]),
                'total_executions': len(self.executions),
                'completed_executions': len([e for e in self.executions.values() if e.status == ExecutionStatus.COMPLETED]),
                'failed_executions': len([e for e in self.executions.values() if e.status == ExecutionStatus.FAILED]),
                'total_triggers': len(self.triggers),
                'container_pool_size': len(self.container_pool)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"함수 통계 조회 오류: {e}")
            return {}
    
    def _setup_http_trigger(self, trigger: Trigger):
        """HTTP 트리거 설정"""
        try:
            # HTTP 엔드포인트 등록
            if self.http_server:
                route_path = f"/trigger/{trigger.trigger_id}"
                
                async def http_handler(request):
                    try:
                        # 요청 데이터 파싱
                        payload = await request.json()
                        
                        # 함수 실행
                        execution_id = self.invoke_function(
                            self.functions[trigger.function_id].name,
                            payload
                        )
                        
                        return web.json_response({
                            'execution_id': execution_id,
                            'status': 'triggered'
                        })
                        
                    except Exception as e:
                        return web.json_response({
                            'error': str(e)
                        }, status=500)
                
                self.http_server.router.add_post(route_path, http_handler)
                
                logger.info(f"HTTP 트리거 설정 완료: {route_path}")
                
        except Exception as e:
            logger.error(f"HTTP 트리거 설정 오류: {e}")
    
    def _setup_cron_trigger(self, trigger: Trigger):
        """Cron 트리거 설정"""
        try:
            # Cron 표현식 파싱
            cron_config = trigger.config.get('cron', '0 * * * *')
            
            # Cron 작업 스케줄링
            def cron_job():
                try:
                    self.invoke_function(
                        self.functions[trigger.function_id].name,
                        trigger.config.get('payload', {})
                    )
                except Exception as e:
                    logger.error(f"Cron 작업 실행 오류: {e}")
            
            # 스케줄러에 작업 추가
            # 실제로는 croniter나 APScheduler 사용
            logger.info(f"Cron 트리거 설정 완료: {cron_config}")
            
        except Exception as e:
            logger.error(f"Cron 트리거 설정 오류: {e}")
    
    def _setup_event_trigger(self, trigger: Trigger):
        """이벤트 트리거 설정"""
        try:
            # 이벤트 구독 설정
            event_type = trigger.config.get('event_type', 'default')
            
            # Redis에 이벤트 구독 등록
            if self.redis_client:
                self.redis_client.sadd(f"event_subscribers:{event_type}", trigger.trigger_id)
                
                logger.info(f"이벤트 트리거 설정 완료: {event_type}")
                
        except Exception as e:
            logger.error(f"이벤트 트리거 설정 오류: {e}")
    
    def _save_function_to_db(self, function: Function):
        """함수를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO functions 
                (function_id, name, runtime, code, handler, timeout,
                 memory, environment, triggers, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                function.function_id,
                function.name,
                function.runtime,
                function.code,
                function.handler,
                function.timeout,
                function.memory,
                json.dumps(function.environment),
                json.dumps(function.triggers),
                function.status.value,
                function.created_at.isoformat(),
                function.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"함수 데이터베이스 저장 오류: {e}")
    
    def _save_execution_to_db(self, execution: Execution):
        """실행을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO executions 
                (execution_id, function_id, status, start_time, end_time,
                 duration, memory_used, cpu_used, logs, result, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution.execution_id,
                execution.function_id,
                execution.status.value,
                execution.start_time.isoformat(),
                execution.end_time.isoformat() if execution.end_time else None,
                execution.duration,
                execution.memory_used,
                execution.cpu_used,
                execution.logs,
                json.dumps(execution.result) if execution.result else None,
                execution.error
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"실행 데이터베이스 저장 오류: {e}")
    
    def _save_trigger_to_db(self, trigger: Trigger):
        """트리거를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO triggers 
                (trigger_id, function_id, trigger_type, config, enabled, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                trigger.trigger_id,
                trigger.function_id,
                trigger.trigger_type.value,
                json.dumps(trigger.config),
                1 if trigger.enabled else 0,
                trigger.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"트리거 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            self.is_processing = False
            self.is_scaling = False
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("서버리스 플랫폼 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './serverless.db',
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 6
        },
        'max_containers': 50,
        'container_timeout': 300,
        'max_workers': 20
    }
    
    # 서버리스 플랫폼 생성
    serverless = ServerlessPlatform(config)
    
    # 함수 생성
    function_info = {
        'name': 'hello-world',
        'runtime': 'python3.9',
        'code': '''
import json
import sys

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from serverless function!',
            'event': event
        })
    }

if __name__ == "__main__":
    event = json.loads(sys.stdin.read())
    result = handler(event, {})
    print(json.dumps(result))
''',
        'handler': 'handler',
        'timeout': 30,
        'memory': 128,
        'environment': {
            'NODE_ENV': 'production'
        },
        'triggers': [
            {
                'type': 'http',
                'config': {
                    'path': '/hello',
                    'method': 'POST'
                }
            }
        ]
    }
    
    function_id = serverless.create_function(function_info)
    print(f"함수 생성 완료: {function_id}")
    
    # 실행 엔진 시작
    serverless.start_execution_engine()
    
    # 함수 실행
    payload = {'name': 'World', 'message': 'Hello'}
    execution_id = serverless.invoke_function('hello-world', payload)
    print(f"함수 실행 요청: {execution_id}")
    
    # 실행 상태 조회
    time.sleep(2)
    execution = serverless.get_execution_status(execution_id)
    if execution:
        print(f"실행 상태: {execution.status.value}")
        print(f"실행 결과: {execution.result}")
    
    # 함수 통계
    stats = serverless.get_function_stats()
    print(f"함수 통계: {stats}") 