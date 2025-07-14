"""
승인 워크플로우 시스템
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    """승인 상태"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class WorkflowType(Enum):
    """워크플로우 타입"""
    USER_APPROVAL = "user_approval"
    IMPROVEMENT_APPROVAL = "improvement_approval"
    AI_SUGGESTION_APPROVAL = "ai_suggestion_approval"

class ApprovalWorkflowSystem:
    """승인 워크플로우 시스템"""
    
    def __init__(self):
        self.workflows = {}
        self.approval_history = {}
        self.last_update = datetime.utcnow()
        
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 생성"""
        try:
            workflow_id = f"workflow_{len(self.workflows) + 1}"
            workflow_data['id'] = workflow_id
            workflow_data['status'] = ApprovalStatus.PENDING.value
            workflow_data['created_at'] = datetime.utcnow().isoformat()
            workflow_data['updated_at'] = datetime.utcnow().isoformat()
            
            self.workflows[workflow_id] = workflow_data
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'message': '워크플로우가 성공적으로 생성되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"워크플로우 생성 실패: {e}")
            return {'error': str(e)}
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """워크플로우 조회"""
        return self.workflows.get(workflow_id)
    
    def approve_workflow(self, workflow_id: str, approver_id: int, comments: str = "") -> Dict[str, Any]:
        """워크플로우 승인"""
        try:
            if workflow_id not in self.workflows:
                return {'error': '워크플로우를 찾을 수 없습니다.'}
            
            workflow = self.workflows[workflow_id]
            workflow['status'] = ApprovalStatus.APPROVED.value
            workflow['approver_id'] = approver_id
            workflow['approved_at'] = datetime.utcnow().isoformat()
            workflow['comments'] = comments
            workflow['updated_at'] = datetime.utcnow().isoformat()
            
            # 승인 히스토리 기록
            self._add_approval_history(workflow_id, 'approved', approver_id, comments)
            
            return {
                'success': True,
                'message': '워크플로우가 승인되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"워크플로우 승인 실패: {e}")
            return {'error': str(e)}
    
    def reject_workflow(self, workflow_id: str, rejecter_id: int, comments: str = "") -> Dict[str, Any]:
        """워크플로우 거부"""
        try:
            if workflow_id not in self.workflows:
                return {'error': '워크플로우를 찾을 수 없습니다.'}
            
            workflow = self.workflows[workflow_id]
            workflow['status'] = ApprovalStatus.REJECTED.value
            workflow['rejecter_id'] = rejecter_id
            workflow['rejected_at'] = datetime.utcnow().isoformat()
            workflow['comments'] = comments
            workflow['updated_at'] = datetime.utcnow().isoformat()
            
            # 승인 히스토리 기록
            self._add_approval_history(workflow_id, 'rejected', rejecter_id, comments)
            
            return {
                'success': True,
                'message': '워크플로우가 거부되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"워크플로우 거부 실패: {e}")
            return {'error': str(e)}
    
    def cancel_workflow(self, workflow_id: str, canceller_id: int, comments: str = "") -> Dict[str, Any]:
        """워크플로우 취소"""
        try:
            if workflow_id not in self.workflows:
                return {'error': '워크플로우를 찾을 수 없습니다.'}
            
            workflow = self.workflows[workflow_id]
            workflow['status'] = ApprovalStatus.CANCELLED.value
            workflow['canceller_id'] = canceller_id
            workflow['cancelled_at'] = datetime.utcnow().isoformat()
            workflow['comments'] = comments
            workflow['updated_at'] = datetime.utcnow().isoformat()
            
            # 승인 히스토리 기록
            self._add_approval_history(workflow_id, 'cancelled', canceller_id, comments)
            
            return {
                'success': True,
                'message': '워크플로우가 취소되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"워크플로우 취소 실패: {e}")
            return {'error': str(e)}
    
    def list_workflows(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """워크플로우 목록 조회"""
        workflows = list(self.workflows.values())
        
        if status:
            workflows = [w for w in workflows if w['status'] == status]
        
        return workflows
    
    def get_pending_workflows(self) -> List[Dict[str, Any]]:
        """대기 중인 워크플로우 조회"""
        return self.list_workflows(ApprovalStatus.PENDING.value)
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """워크플로우 히스토리 조회"""
        return self.approval_history.get(workflow_id, [])
    
    def _add_approval_history(self, workflow_id: str, action: str, user_id: int, comments: str):
        """승인 히스토리 추가"""
        if workflow_id not in self.approval_history:
            self.approval_history[workflow_id] = []
        
        history_entry = {
            'action': action,
            'user_id': user_id,
            'comments': comments,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.approval_history[workflow_id].append(history_entry)

# 전역 인스턴스
approval_workflow_system = ApprovalWorkflowSystem() 