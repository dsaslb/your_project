import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 외부 라이브러리 import를 안전하게 처리
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

try:
    from app import db
    from models.plugin_automation import (
        PluginEvent, PluginTrigger, PluginAction, 
        PluginWorkflow, PluginAutomationLog
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    # 더미 클래스들
    class PluginEvent: pass
    class PluginTrigger: pass
    class PluginAction: pass
    class PluginWorkflow: pass
    class PluginAutomationLog: pass

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """이벤트 타입 정의"""
    PLUGIN_INSTALL = "plugin_install"
    PLUGIN_UPDATE = "plugin_update"
    PLUGIN_UNINSTALL = "plugin_uninstall"
    PLUGIN_EXECUTE = "plugin_execute"
    PLUGIN_ERROR = "plugin_error"
    USER_LOGIN = "user_login"
    USER_ACTION = "user_action"
    SYSTEM_ALERT = "system_alert"
    CUSTOM = "custom"

class ActionType(Enum):
    """액션 타입 정의"""
    NOTIFY = "notify"
    API_CALL = "api_call"
    PLUGIN_EXECUTE = "plugin_execute"
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    CUSTOM = "custom"

@dataclass
class EventData:
    """이벤트 데이터 구조"""
    event_type: str
    plugin_id: Optional[int] = None
    event_source: str = "system"
    event_payload: Dict[str, Any] = None
    triggered_by: Optional[int] = None

@dataclass
class ActionResult:
    """액션 실행 결과"""
    success: bool
    result: Dict[str, Any] = None
    error_message: str = None

class PluginAutomationEngine:
    """플러그인 자동화 엔진"""
    
    def __init__(self):
        self.is_running = False
        self.event_queue = []
        self.processing_thread = None
        self.trigger_cache = {}
        self.action_cache = {}
        self.workflow_cache = {}
        
    def start(self):
        """자동화 엔진 시작"""
        if self.is_running:
            logger.warning("자동화 엔진이 이미 실행 중입니다.")
            return
            
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        logger.info("플러그인 자동화 엔진이 시작되었습니다.")
        
    def stop(self):
        """자동화 엔진 중지"""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("플러그인 자동화 엔진이 중지되었습니다.")
        
    def emit_event(self, event_data: EventData):
        """이벤트 발생"""
        try:
            # 이벤트를 DB에 저장
            if DB_AVAILABLE:
                event = PluginEvent(
                    plugin_id=event_data.plugin_id,
                    event_type=event_data.event_type,
                    event_source=event_data.event_source,
                    event_payload=event_data.event_payload or {},
                    triggered_by=event_data.triggered_by
                )
                db.session.add(event)
                db.session.flush()  # ID 생성을 위해 flush
                
                # 이벤트 큐에 추가
                self.event_queue.append({
                    'event_id': event.id,
                    'event_data': event_data
                })
                
                logger.info(f"이벤트 발생: {event_data.event_type} (ID: {event.id})")
            else:
                # DB가 없을 경우 더미 처리
                logger.info(f"더미 이벤트 발생: {event_data.event_type}")
                
        except Exception as e:
            logger.error(f"이벤트 발생 중 오류: {str(e)}")
            
    def _process_events(self):
        """이벤트 처리 스레드"""
        while self.is_running:
            try:
                if self.event_queue:
                    event_item = self.event_queue.pop(0)
                    self._handle_event(event_item)
                else:
                    time.sleep(0.1)  # 100ms 대기
            except Exception as e:
                logger.error(f"이벤트 처리 중 오류: {str(e)}")
                time.sleep(1)  # 오류 시 1초 대기
                
    def _handle_event(self, event_item: Dict):
        """개별 이벤트 처리"""
        event_id = event_item.get('event_id')
        event_data = event_item['event_data']
        
        try:
            # 트리거 매칭
            matching_triggers = self._find_matching_triggers(event_data)
            
            # 매칭된 트리거에 대해 워크플로우 실행
            for trigger in matching_triggers:
                workflows = self._get_workflows_for_trigger(trigger.id)
                for workflow in workflows:
                    self._execute_workflow(workflow, event_id, event_data)
                    
        except Exception as e:
            logger.error(f"이벤트 처리 중 오류 (ID: {event_id}): {str(e)}")
            
    def _find_matching_triggers(self, event_data: EventData) -> List[PluginTrigger]:
        """이벤트와 매칭되는 트리거 찾기"""
        matching_triggers = []
        
        try:
            if DB_AVAILABLE:
                # 캐시된 트리거 사용
                if not self.trigger_cache:
                    self._load_triggers()
                    
                for trigger in self.trigger_cache.values():
                    if (trigger.is_active and 
                        trigger.event_type == event_data.event_type and
                        self._check_filter_conditions(trigger, event_data)):
                        matching_triggers.append(trigger)
            else:
                # 더미 트리거 반환
                matching_triggers = self._get_dummy_triggers(event_data.event_type)
                
        except Exception as e:
            logger.error(f"트리거 매칭 중 오류: {str(e)}")
            
        return matching_triggers
        
    def _check_filter_conditions(self, trigger: PluginTrigger, event_data: EventData) -> bool:
        """트리거 필터 조건 확인"""
        try:
            conditions = trigger.filter_conditions or {}
            
            # 플러그인 ID 필터
            if 'plugin_id' in conditions:
                if event_data.plugin_id != conditions['plugin_id']:
                    return False
                    
            # 사용자 ID 필터
            if 'user_id' in conditions:
                if event_data.triggered_by != conditions['user_id']:
                    return False
                    
            # 커스텀 조건 필터
            if 'custom_conditions' in conditions:
                custom_conditions = conditions['custom_conditions']
                for condition in custom_conditions:
                    if not self._evaluate_condition(condition, event_data):
                        return False
                        
            return True
            
        except Exception as e:
            logger.error(f"필터 조건 확인 중 오류: {str(e)}")
            return False
            
    def _evaluate_condition(self, condition: Dict, event_data: EventData) -> bool:
        """커스텀 조건 평가"""
        try:
            condition_type = condition.get('type')
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if condition_type == 'payload':
                actual_value = event_data.event_payload.get(field)
            else:
                actual_value = getattr(event_data, field, None)
                
            if operator == 'equals':
                return actual_value == value
            elif operator == 'not_equals':
                return actual_value != value
            elif operator == 'contains':
                return value in str(actual_value)
            elif operator == 'greater_than':
                return actual_value > value
            elif operator == 'less_than':
                return actual_value < value
            else:
                return False
                
        except Exception as e:
            logger.error(f"조건 평가 중 오류: {str(e)}")
            return False
            
    def _get_workflows_for_trigger(self, trigger_id: int) -> List[PluginWorkflow]:
        """트리거에 연결된 워크플로우 가져오기"""
        try:
            if DB_AVAILABLE:
                if not self.workflow_cache:
                    self._load_workflows()
                    
                workflows = [w for w in self.workflow_cache.values() 
                           if w.trigger_id == trigger_id and w.is_active]
                return sorted(workflows, key=lambda w: w.execution_order)
            else:
                return self._get_dummy_workflows(trigger_id)
                
        except Exception as e:
            logger.error(f"워크플로우 조회 중 오류: {str(e)}")
            return []
            
    def _execute_workflow(self, workflow: PluginWorkflow, event_id: int, event_data: EventData):
        """워크플로우 실행"""
        try:
            # 액션 정보 가져오기
            action = self._get_action(workflow.action_id)
            if not action or not action.is_active:
                logger.warning(f"액션이 비활성화되어 있습니다: {workflow.action_id}")
                return
                
            # 액션 실행
            result = self._execute_action(action, event_data)
            
            # 실행 로그 저장
            self._log_automation_execution(workflow, event_id, action, result)
            
            logger.info(f"워크플로우 실행 완료: {workflow.name} -> {action.name}")
            
        except Exception as e:
            logger.error(f"워크플로우 실행 중 오류: {str(e)}")
            # 오류 로그 저장
            error_result = ActionResult(success=False, error_message=str(e))
            self._log_automation_execution(workflow, event_id, None, error_result)
            
    def _execute_action(self, action: PluginAction, event_data: EventData) -> ActionResult:
        """액션 실행"""
        try:
            action_type = action.action_type
            payload = action.action_payload or {}
            
            if action_type == ActionType.NOTIFY.value:
                return self._execute_notify_action(payload, event_data)
            elif action_type == ActionType.API_CALL.value:
                return self._execute_api_call_action(payload, event_data)
            elif action_type == ActionType.PLUGIN_EXECUTE.value:
                return self._execute_plugin_action(payload, event_data)
            elif action_type == ActionType.EMAIL.value:
                return self._execute_email_action(payload, event_data)
            elif action_type == ActionType.SLACK.value:
                return self._execute_slack_action(payload, event_data)
            else:
                return ActionResult(success=False, error_message=f"지원하지 않는 액션 타입: {action_type}")
                
        except Exception as e:
            logger.error(f"액션 실행 중 오류: {str(e)}")
            return ActionResult(success=False, error_message=str(e))
            
    def _execute_notify_action(self, payload: Dict, event_data: EventData) -> ActionResult:
        """알림 액션 실행"""
        try:
            message = payload.get('message', '알림이 발생했습니다.')
            notification_type = payload.get('type', 'info')
            
            # 실제 알림 시스템과 연동 (현재는 더미)
            logger.info(f"알림 전송: {message} (타입: {notification_type})")
            
            return ActionResult(
                success=True,
                result={'message': message, 'type': notification_type}
            )
            
        except Exception as e:
            return ActionResult(success=False, error_message=str(e))
            
    def _execute_api_call_action(self, payload: Dict, event_data: EventData) -> ActionResult:
        """API 호출 액션 실행"""
        try:
            if not REQUESTS_AVAILABLE:
                return ActionResult(success=False, error_message="requests 라이브러리가 설치되지 않았습니다.")
                
            url = payload.get('url')
            method = payload.get('method', 'POST')
            headers = payload.get('headers', {})
            data = payload.get('data', {})
            
            if not url:
                return ActionResult(success=False, error_message="URL이 지정되지 않았습니다.")
                
            # API 호출
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            return ActionResult(
                success=response.status_code < 400,
                result={
                    'status_code': response.status_code,
                    'response': response.text
                }
            )
            
        except Exception as e:
            return ActionResult(success=False, error_message=str(e))
            
    def _execute_plugin_action(self, payload: Dict, event_data: EventData) -> ActionResult:
        """플러그인 실행 액션"""
        try:
            plugin_id = payload.get('plugin_id')
            function_name = payload.get('function', 'execute')
            parameters = payload.get('parameters', {})
            
            if not plugin_id:
                return ActionResult(success=False, error_message="플러그인 ID가 지정되지 않았습니다.")
                
            # 플러그인 실행 로직 (현재는 더미)
            logger.info(f"플러그인 실행: {plugin_id}.{function_name}")
            
            return ActionResult(
                success=True,
                result={'plugin_id': plugin_id, 'function': function_name}
            )
            
        except Exception as e:
            return ActionResult(success=False, error_message=str(e))
            
    def _execute_email_action(self, payload: Dict, event_data: EventData) -> ActionResult:
        """이메일 액션 실행"""
        try:
            to_email = payload.get('to')
            subject = payload.get('subject', '자동화 알림')
            body = payload.get('body', '자동화가 실행되었습니다.')
            
            if not to_email:
                return ActionResult(success=False, error_message="수신자 이메일이 지정되지 않았습니다.")
                
            # 이메일 전송 로직 (현재는 더미)
            logger.info(f"이메일 전송: {to_email} - {subject}")
            
            return ActionResult(
                success=True,
                result={'to': to_email, 'subject': subject}
            )
            
        except Exception as e:
            return ActionResult(success=False, error_message=str(e))
            
    def _execute_slack_action(self, payload: Dict, event_data: EventData) -> ActionResult:
        """Slack 액션 실행"""
        try:
            webhook_url = payload.get('webhook_url')
            channel = payload.get('channel', '#general')
            message = payload.get('message', '자동화가 실행되었습니다.')
            
            if not webhook_url:
                return ActionResult(success=False, error_message="Slack Webhook URL이 지정되지 않았습니다.")
                
            # Slack 전송 로직 (현재는 더미)
            logger.info(f"Slack 전송: {channel} - {message}")
            
            return ActionResult(
                success=True,
                result={'channel': channel, 'message': message}
            )
            
        except Exception as e:
            return ActionResult(success=False, error_message=str(e))
            
    def _load_triggers(self):
        """트리거 캐시 로드"""
        try:
            if DB_AVAILABLE:
                triggers = PluginTrigger.query.filter_by(is_active=True).all()
                self.trigger_cache = {t.id: t for t in triggers}
            else:
                self.trigger_cache = {}
        except Exception as e:
            logger.error(f"트리거 로드 중 오류: {str(e)}")
            self.trigger_cache = {}
            
    def _load_workflows(self):
        """워크플로우 캐시 로드"""
        try:
            if DB_AVAILABLE:
                workflows = PluginWorkflow.query.filter_by(is_active=True).all()
                self.workflow_cache = {w.id: w for w in workflows}
            else:
                self.workflow_cache = {}
        except Exception as e:
            logger.error(f"워크플로우 로드 중 오류: {str(e)}")
            self.workflow_cache = {}
            
    def _get_action(self, action_id: int) -> Optional[PluginAction]:
        """액션 정보 가져오기"""
        try:
            if DB_AVAILABLE:
                if not self.action_cache:
                    actions = PluginAction.query.filter_by(is_active=True).all()
                    self.action_cache = {a.id: a for a in actions}
                return self.action_cache.get(action_id)
            else:
                return self._get_dummy_action(action_id)
        except Exception as e:
            logger.error(f"액션 조회 중 오류: {str(e)}")
            return None
            
    def _log_automation_execution(self, workflow: PluginWorkflow, event_id: int, 
                                action: Optional[PluginAction], result: ActionResult):
        """자동화 실행 로그 저장"""
        try:
            if DB_AVAILABLE:
                log = PluginAutomationLog(
                    workflow_id=workflow.id,
                    event_id=event_id,
                    action_id=action.id if action else None,
                    status='success' if result.success else 'failed',
                    result=result.result or {},
                    error_message=result.error_message
                )
                db.session.add(log)
                db.session.commit()
        except Exception as e:
            logger.error(f"자동화 로그 저장 중 오류: {str(e)}")
            
    # 더미 데이터 메서드들
    def _get_dummy_triggers(self, event_type: str) -> List[PluginTrigger]:
        """더미 트리거 반환"""
        dummy_triggers = []
        
        if event_type == EventType.PLUGIN_INSTALL.value:
            trigger = type('DummyTrigger', (), {
                'id': 1,
                'name': '플러그인 설치 알림',
                'event_type': event_type,
                'is_active': True
            })()
            dummy_triggers.append(trigger)
            
        return dummy_triggers
        
    def _get_dummy_workflows(self, trigger_id: int) -> List[PluginWorkflow]:
        """더미 워크플로우 반환"""
        if trigger_id == 1:
            workflow = type('DummyWorkflow', (), {
                'id': 1,
                'name': '설치 알림 워크플로우',
                'trigger_id': trigger_id,
                'action_id': 1,
                'is_active': True,
                'execution_order': 1
            })()
            return [workflow]
        return []
        
    def _get_dummy_action(self, action_id: int) -> Optional[PluginAction]:
        """더미 액션 반환"""
        if action_id == 1:
            return type('DummyAction', (), {
                'id': 1,
                'name': '알림 전송',
                'action_type': ActionType.NOTIFY.value,
                'is_active': True,
                'action_payload': {'message': '새로운 플러그인이 설치되었습니다.'}
            })()
        return None

# 전역 자동화 엔진 인스턴스
automation_engine = PluginAutomationEngine() 