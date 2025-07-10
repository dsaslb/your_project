"""
피드백 시스템
사용자 피드백을 수집, 분석, 처리하는 시스템
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    """피드백 타입"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT = "improvement"
    QUESTION = "question"
    COMPLIMENT = "compliment"
    OTHER = "other"

class FeedbackStatus(Enum):
    """피드백 상태"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"

@dataclass
class Feedback:
    """피드백 데이터"""
    id: str
    user_id: str
    type: FeedbackType
    title: str
    description: str
    category: str
    priority: str
    status: FeedbackStatus
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    attachments: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

class FeedbackSystem:
    """피드백 시스템"""
    
    def __init__(self, storage_file: str = "feedback_data.json"):
        self.storage_file = storage_file
        self.feedbacks: Dict[str, Feedback] = {}
        self.categories: List[str] = []
        self.tags: List[str] = []
        
        # 초기 데이터 로드
        self._load_data()
    
    def submit_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> str:
        """피드백 제출"""
        try:
            feedback_id = str(uuid.uuid4())
            
            feedback = Feedback(
                id=feedback_id,
                user_id=user_id,
                type=FeedbackType(feedback_data.get('type', 'other')),
                title=feedback_data.get('title', ''),
                description=feedback_data.get('description', ''),
                category=feedback_data.get('category', 'general'),
                priority=feedback_data.get('priority', 'medium'),
                status=FeedbackStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=feedback_data.get('tags', []),
                attachments=feedback_data.get('attachments', []),
                metadata=feedback_data.get('metadata', {})
            )
            
            self.feedbacks[feedback_id] = feedback
            
            # 카테고리와 태그 업데이트
            self._update_categories_and_tags(feedback)
            
            # 데이터 저장
            self._save_data()
            
            logger.info(f"피드백 제출 완료: {feedback_id}")
            return feedback_id
            
        except Exception as e:
            logger.error(f"피드백 제출 실패: {e}")
            raise
    
    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """피드백 조회"""
        return self.feedbacks.get(feedback_id)
    
    def get_user_feedbacks(self, user_id: str) -> List[Feedback]:
        """사용자의 피드백 목록 조회"""
        return [
            feedback for feedback in self.feedbacks.values()
            if feedback.user_id == user_id
        ]
    
    def get_all_feedbacks(self, 
                         status: Optional[FeedbackStatus] = None,
                         category: Optional[str] = None,
                         type: Optional[FeedbackType] = None) -> List[Feedback]:
        """모든 피드백 조회 (필터링 가능)"""
        feedbacks = list(self.feedbacks.values())
        
        if status:
            feedbacks = [f for f in feedbacks if f.status == status]
        
        if category:
            feedbacks = [f for f in feedbacks if f.category == category]
        
        if type:
            feedbacks = [f for f in feedbacks if f.type == type]
        
        return sorted(feedbacks, key=lambda x: x.created_at, reverse=True)
    
    def update_feedback_status(self, feedback_id: str, status: FeedbackStatus, 
                              admin_id: str, comment: str = "") -> bool:
        """피드백 상태 업데이트"""
        if feedback_id not in self.feedbacks:
            logger.error(f"피드백 {feedback_id}을 찾을 수 없습니다")
            return False
        
        try:
            feedback = self.feedbacks[feedback_id]
            feedback.status = status
            feedback.updated_at = datetime.now()
            
            # 메타데이터에 관리자 정보 추가
            if 'admin_updates' not in feedback.metadata:
                feedback.metadata['admin_updates'] = []
            
            feedback.metadata['admin_updates'].append({
                'admin_id': admin_id,
                'status': status.value,
                'comment': comment,
                'timestamp': datetime.now().isoformat()
            })
            
            self._save_data()
            
            logger.info(f"피드백 {feedback_id} 상태 업데이트: {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"피드백 상태 업데이트 실패: {e}")
            return False
    
    def add_feedback_comment(self, feedback_id: str, user_id: str, 
                           comment: str, is_admin: bool = False) -> bool:
        """피드백에 댓글 추가"""
        if feedback_id not in self.feedbacks:
            logger.error(f"피드백 {feedback_id}을 찾을 수 없습니다")
            return False
        
        try:
            feedback = self.feedbacks[feedback_id]
            
            if 'comments' not in feedback.metadata:
                feedback.metadata['comments'] = []
            
            feedback.metadata['comments'].append({
                'user_id': user_id,
                'comment': comment,
                'is_admin': is_admin,
                'timestamp': datetime.now().isoformat()
            })
            
            feedback.updated_at = datetime.now()
            self._save_data()
            
            logger.info(f"피드백 {feedback_id}에 댓글 추가")
            return True
            
        except Exception as e:
            logger.error(f"피드백 댓글 추가 실패: {e}")
            return False
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """피드백 통계 조회"""
        total_count = len(self.feedbacks)
        
        # 상태별 통계
        status_stats = {}
        for status in FeedbackStatus:
            status_stats[status.value] = len([
                f for f in self.feedbacks.values() if f.status == status
            ])
        
        # 타입별 통계
        type_stats = {}
        for feedback_type in FeedbackType:
            type_stats[feedback_type.value] = len([
                f for f in self.feedbacks.values() if f.type == feedback_type
            ])
        
        # 카테고리별 통계
        category_stats = {}
        for category in self.categories:
            category_stats[category] = len([
                f for f in self.feedbacks.values() if f.category == category
            ])
        
        return {
            'total_count': total_count,
            'status_stats': status_stats,
            'type_stats': type_stats,
            'category_stats': category_stats,
            'categories': self.categories,
            'tags': self.tags
        }
    
    def search_feedbacks(self, query: str) -> List[Feedback]:
        """피드백 검색"""
        query_lower = query.lower()
        results = []
        
        for feedback in self.feedbacks.values():
            if (query_lower in feedback.title.lower() or
                query_lower in feedback.description.lower() or
                any(query_lower in tag.lower() for tag in feedback.tags)):
                results.append(feedback)
        
        return sorted(results, key=lambda x: x.created_at, reverse=True)
    
    def _update_categories_and_tags(self, feedback: Feedback):
        """카테고리와 태그 업데이트"""
        if feedback.category not in self.categories:
            self.categories.append(feedback.category)
        
        for tag in feedback.tags:
            if tag not in self.tags:
                self.tags.append(tag)
    
    def _load_data(self):
        """데이터 로드"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 피드백 데이터 로드
            for feedback_data in data.get('feedbacks', []):
                feedback = Feedback(
                    id=feedback_data['id'],
                    user_id=feedback_data['user_id'],
                    type=FeedbackType(feedback_data['type']),
                    title=feedback_data['title'],
                    description=feedback_data['description'],
                    category=feedback_data['category'],
                    priority=feedback_data['priority'],
                    status=FeedbackStatus(feedback_data['status']),
                    created_at=datetime.fromisoformat(feedback_data['created_at']),
                    updated_at=datetime.fromisoformat(feedback_data['updated_at']),
                    tags=feedback_data['tags'],
                    attachments=feedback_data['attachments'],
                    metadata=feedback_data['metadata']
                )
                self.feedbacks[feedback.id] = feedback
            
            # 카테고리와 태그 로드
            self.categories = data.get('categories', [])
            self.tags = data.get('tags', [])
            
            logger.info(f"피드백 데이터 로드 완료: {len(self.feedbacks)}개")
            
        except FileNotFoundError:
            logger.info("피드백 데이터 파일이 없습니다. 새로 생성합니다.")
        except Exception as e:
            logger.error(f"피드백 데이터 로드 실패: {e}")
    
    def _save_data(self):
        """데이터 저장"""
        try:
            data = {
                'feedbacks': [feedback.to_dict() for feedback in self.feedbacks.values()],
                'categories': self.categories,
                'tags': self.tags
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("피드백 데이터 저장 완료")
            
        except Exception as e:
            logger.error(f"피드백 데이터 저장 실패: {e}")

# 전역 피드백 시스템 인스턴스
feedback_system = FeedbackSystem() 