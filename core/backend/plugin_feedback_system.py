from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import json
from typing import Optional
from flask import request

form = None  # pyright: ignore


class FeedbackStatus(Enum):
    """피드백 상태"""

    PENDING = "pending"  # 대기중
    IN_REVIEW = "in_review"  # 검토중
    APPROVED = "approved"  # 승인됨
    REJECTED = "rejected"  # 거부됨
    IN_DEVELOPMENT = "in_development"  # 개발중
    COMPLETED = "completed"  # 완료됨
    CANCELLED = "cancelled"  # 취소됨


class FeedbackType(Enum):
    """피드백 유형"""

    PLUGIN_REQUEST = "plugin_request"  # 플러그인 요청
    FEATURE_REQUEST = "feature_request"  # 기능 요청
    BUG_REPORT = "bug_report"  # 버그 신고
    IMPROVEMENT = "improvement"  # 개선 제안
    FEEDBACK = "feedback"  # 일반 피드백


@dataclass
class PluginFeedback:
    """플러그인 피드백"""

    id: str
    type: str
    title: str
    description: str
    user_id: str
    user_name: str
    plugin_id: Optional[str] = None
    status: str = ""
    priority: str = "medium"
    category: str = "general"
    tags: List[str] = field(default_factory=list)  # pyright: ignore
    attachments: List[str] = field(default_factory=list)  # pyright: ignore
    created_at: str = ""
    updated_at: str = ""
    assigned_to: Optional[str] = None
    estimated_completion: Optional[str] = None
    actual_completion: Optional[str] = None
    comments: List[Dict[str, Any]] = field(default_factory=list)  # pyright: ignore
    votes: int = 0
    followers: List[str] = field(default_factory=list)  # pyright: ignore


@dataclass
class FeedbackComment:
    """피드백 댓글"""

    id: str
    feedback_id: str
    user_id: str
    user_name: str
    user_role: str  # user, developer, admin
    content: str
    created_at: str
    updated_at: str
    is_internal: bool  # 내부 댓글 (개발자/관리자만)


@dataclass
class FeedbackWorkflow:
    """피드백 워크플로우"""

    id: str
    name: str
    description: str
    steps: List[Dict[str, Any]] = field(default_factory=list)  # pyright: ignore
    current_step: int = 0
    feedback_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None


class PluginFeedbackSystem:
    """플러그인 피드백/승인 시스템"""

    def __init__(self, feedback_dir="feedback"):
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(exist_ok=True)

        # 피드백 데이터 파일
        self.feedback_file = self.feedback_dir / "feedback.json"
        self.comments_file = self.feedback_dir / "comments.json"
        self.workflows_file = self.feedback_dir / "workflows.json"
        self.templates_file = self.feedback_dir / "templates.json"

        # 초기화
        self._init_feedback_system()

    def _init_feedback_system(self):
        """피드백 시스템 초기화"""
        # 피드백 목록 초기화
        if not self.feedback_file.exists():
            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 댓글 목록 초기화
        if not self.comments_file.exists():
            with open(self.comments_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 워크플로우 목록 초기화
        if not self.workflows_file.exists():
            with open(self.workflows_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 템플릿 초기화
        if not self.templates_file.exists():
            templates = {
                "plugin_request": {
                    "title": "새 플러그인 요청",
                    "description": "필요한 플러그인에 대한 상세한 설명을 작성해주세요.",
                    "fields": [
                        {
                            "name": "plugin_name",
                            "label": "플러그인 이름",
                            "type": "text",
                            "required": True,
                        },
                        {
                            "name": "category",
                            "label": "카테고리",
                            "type": "select",
                            "required": True,
                        },
                        {
                            "name": "description",
                            "label": "상세 설명",
                            "type": "textarea",
                            "required": True,
                        },
                        {
                            "name": "use_case",
                            "label": "사용 사례",
                            "type": "textarea",
                            "required": False,
                        },
                        {
                            "name": "priority",
                            "label": "우선순위",
                            "type": "select",
                            "required": True,
                        },
                    ],
                },
                "feature_request": {
                    "title": "기능 요청",
                    "description": "기존 플러그인에 추가하고 싶은 기능을 설명해주세요.",
                    "fields": [
                        {
                            "name": "plugin_id",
                            "label": "플러그인",
                            "type": "select",
                            "required": True,
                        },
                        {
                            "name": "feature_name",
                            "label": "기능 이름",
                            "type": "text",
                            "required": True,
                        },
                        {
                            "name": "description",
                            "label": "기능 설명",
                            "type": "textarea",
                            "required": True,
                        },
                        {
                            "name": "benefit",
                            "label": "기대 효과",
                            "type": "textarea",
                            "required": False,
                        },
                        {
                            "name": "priority",
                            "label": "우선순위",
                            "type": "select",
                            "required": True,
                        },
                    ],
                },
                "bug_report": {
                    "title": "버그 신고",
                    "description": "발견한 버그에 대한 상세한 정보를 제공해주세요.",
                    "fields": [
                        {
                            "name": "plugin_id",
                            "label": "플러그인",
                            "type": "select",
                            "required": True,
                        },
                        {
                            "name": "bug_title",
                            "label": "버그 제목",
                            "type": "text",
                            "required": True,
                        },
                        {
                            "name": "description",
                            "label": "버그 설명",
                            "type": "textarea",
                            "required": True,
                        },
                        {
                            "name": "steps",
                            "label": "재현 단계",
                            "type": "textarea",
                            "required": True,
                        },
                        {
                            "name": "expected",
                            "label": "예상 동작",
                            "type": "textarea",
                            "required": False,
                        },
                        {
                            "name": "actual",
                            "label": "실제 동작",
                            "type": "textarea",
                            "required": False,
                        },
                        {
                            "name": "severity",
                            "label": "심각도",
                            "type": "select",
                            "required": True,
                        },
                    ],
                },
            }
            with open(self.templates_file, "w", encoding="utf-8") as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)

    def create_feedback(self, feedback_data: Dict[str, Any]) -> Optional[str]:
        """피드백 생성"""
        try:
            feedbacks = self._load_feedback()

            feedback_id = str(uuid.uuid4())
            feedback = {
                "id": feedback_id,
                "type": feedback_data.get("type", "feedback"),
                "title": feedback_data.get("title", ""),
                "description": feedback_data.get("description", ""),
                "user_id": feedback_data.get("user_id", "anonymous"),
                "user_name": feedback_data.get("user_name", "Anonymous"),
                "plugin_id": feedback_data.get("plugin_id"),
                "status": FeedbackStatus.PENDING.value,
                "priority": feedback_data.get("priority", "medium"),
                "category": feedback_data.get("category", "general"),
                "tags": feedback_data.get("tags", []),
                "attachments": feedback_data.get("attachments", []),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "assigned_to": None,
                "estimated_completion": None,
                "actual_completion": None,
                "comments": [],
                "votes": 0,
                "followers": [feedback_data.get("user_id", "anonymous")],
            }

            feedbacks.append(feedback)
            self._save_feedback(feedbacks)

            # 워크플로우 생성
            self._create_workflow(feedback_id, str(feedback["type"]))

            return feedback_id

        except Exception as e:
            print(f"피드백 생성 실패: {e}")
            return None

    def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """피드백 조회"""
        try:
            feedbacks = self._load_feedback()
            feedback = next((f for f in feedbacks if f["id"] == feedback_id), None)
            return feedback
        except Exception as e:
            print(f"피드백 조회 실패: {e}")
            return None

    def get_feedback_list(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None,
        plugin_id: Optional[str] = None,
        user_id: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """피드백 목록 조회"""
        try:
            feedbacks = self._load_feedback()

            # 필터링
            if status:
                feedbacks = [f for f in feedbacks if f.get("status") == status]
            if type:
                feedbacks = [f for f in feedbacks if f.get("type") == type]
            if plugin_id:
                feedbacks = [f for f in feedbacks if f.get("plugin_id") == plugin_id]
            if user_id:
                feedbacks = [f for f in feedbacks if f.get("user_id") == user_id]

            # 정렬
            reverse = sort_order == "desc"
            if sort_by == "created_at":
                feedbacks.sort(key=lambda x: x.get("created_at", ""), reverse=reverse)
            elif sort_by == "updated_at":
                feedbacks.sort(key=lambda x: x.get("updated_at", ""), reverse=reverse)
            elif sort_by == "votes":
                feedbacks.sort(key=lambda x: x.get("votes", 0), reverse=reverse)
            elif sort_by == "priority":
                priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
                feedbacks.sort(
                    key=lambda x: priority_order.get(x.get("priority", "medium"), 0),
                    reverse=reverse,
                )

            return feedbacks

        except Exception as e:
            print(f"피드백 목록 조회 실패: {e}")
            return []

    def update_feedback_status(
        self, feedback_id: str, status: str, user_id: str, comment: str = ""
    ) -> bool:
        """피드백 상태 업데이트"""
        try:
            feedbacks = self._load_feedback()
            feedback = next((f for f in feedbacks if f["id"] == feedback_id), None)

            if not feedback:
                return False

            # 상태 업데이트
            feedback["status"] = status
            feedback["updated_at"] = datetime.now().isoformat()

            # 댓글 추가
            if comment:
                self.add_comment(
                    feedback_id, user_id, "Admin", "admin", comment, is_internal=True
                )

            # 워크플로우 업데이트
            self._update_workflow(feedback_id, status)

            self._save_feedback(feedbacks)
            return True

        except Exception as e:
            print(f"피드백 상태 업데이트 실패: {e}")
            return False

    def assign_feedback(
        self,
        feedback_id: str,
        assigned_to: str,
        estimated_completion: Optional[str] = None,
    ) -> bool:
        """피드백 할당"""
        try:
            feedbacks = self._load_feedback()
            feedback = next((f for f in feedbacks if f["id"] == feedback_id), None)

            if not feedback:
                return False

            feedback["assigned_to"] = assigned_to
            feedback["estimated_completion"] = estimated_completion
            feedback["updated_at"] = datetime.now().isoformat()

            self._save_feedback(feedbacks)
            return True

        except Exception as e:
            print(f"피드백 할당 실패: {e}")
            return False

    def add_comment(
        self,
        feedback_id: str,
        user_id: str,
        user_name: str,
        user_role: str,
        content: str,
        is_internal: bool = False,
    ) -> Optional[str]:
        """댓글 추가"""
        try:
            comments = self._load_comments()

            comment_id = str(uuid.uuid4())
            comment = {
                "id": comment_id,
                "feedback_id": feedback_id,
                "user_id": user_id,
                "user_name": user_name,
                "user_role": user_role,
                "content": content,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_internal": is_internal,
            }

            comments.append(comment)
            self._save_comments(comments)

            # 피드백의 댓글 목록 업데이트
            feedbacks = self._load_feedback()
            feedback = next((f for f in feedbacks if f["id"] == feedback_id), None)
            if feedback:
                feedback["comments"].append(
                    {
                        "id": comment_id,
                        "user_name": user_name,
                        "user_role": user_role,
                        "content": content,
                        "created_at": comment["created_at"],
                        "is_internal": is_internal,
                    }
                )
                feedback["updated_at"] = datetime.now().isoformat()
                self._save_feedback(feedbacks)

            return comment_id

        except Exception as e:
            print(f"댓글 추가 실패: {e}")
            return None

    def get_comments(
        self, feedback_id: str, include_internal: bool = False
    ) -> List[Dict[str, Any]]:
        """댓글 목록 조회"""
        try:
            comments = self._load_comments()
            feedback_comments = [c for c in comments if c["feedback_id"] == feedback_id]

            if not include_internal:
                feedback_comments = [
                    c for c in feedback_comments if not c.get("is_internal", False)
                ]

            # 시간순 정렬
            feedback_comments.sort(key=lambda x: x.get("created_at", ""), reverse=False)

            return feedback_comments

        except Exception as e:
            print(f"댓글 목록 조회 실패: {e}")
            return []

    def vote_feedback(self, feedback_id: str, user_id: str, vote: bool = True) -> bool:
        """피드백 투표"""
        try:
            feedbacks = self._load_feedback()
            feedback = next((f for f in feedbacks if f["id"] == feedback_id), None)

            if not feedback:
                return False

            if vote:
                feedback["votes"] = feedback.get("votes", 0) + 1
            else:
                feedback["votes"] = max(0, feedback.get("votes", 0) - 1)

            feedback["updated_at"] = datetime.now().isoformat()
            self._save_feedback(feedbacks)
            return True

        except Exception as e:
            print(f"피드백 투표 실패: {e}")
            return False

    def follow_feedback(
        self, feedback_id: str, user_id: str, follow: bool = True
    ) -> bool:
        """피드백 팔로우"""
        try:
            feedbacks = self._load_feedback()
            feedback = next((f for f in feedbacks if f["id"] == feedback_id), None)

            if not feedback:
                return False

            followers = feedback.get("followers", [])

            if follow and user_id not in followers:
                followers.append(user_id)
            elif not follow and user_id in followers:
                followers.remove(user_id)

            feedback["followers"] = followers
            feedback["updated_at"] = datetime.now().isoformat()
            self._save_feedback(feedbacks)
            return True

        except Exception as e:
            print(f"피드백 팔로우 실패: {e}")
            return False

    def get_templates(self) -> Dict[str, Any]:
        """피드백 템플릿 조회"""
        try:
            with open(self.templates_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_workflow(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """워크플로우 조회"""
        try:
            workflows = self._load_workflows()
            workflow = next(
                (w for w in workflows if w["feedback_id"] == feedback_id), None
            )
            return workflow
        except Exception as e:
            print(f"워크플로우 조회 실패: {e}")
            return None

    def _create_workflow(self, feedback_id: str, feedback_type: str):
        """워크플로우 생성"""
        try:
            workflows = self._load_workflows()

            # 피드백 유형별 워크플로우 정의
            workflow_steps = {
                "plugin_request": [
                    {"step": 1, "name": "요청 접수", "status": "completed"},
                    {"step": 2, "name": "검토", "status": "pending"},
                    {"step": 3, "name": "승인/거부", "status": "pending"},
                    {"step": 4, "name": "개발", "status": "pending"},
                    {"step": 5, "name": "테스트", "status": "pending"},
                    {"step": 6, "name": "배포", "status": "pending"},
                ],
                "feature_request": [
                    {"step": 1, "name": "요청 접수", "status": "completed"},
                    {"step": 2, "name": "검토", "status": "pending"},
                    {"step": 3, "name": "승인/거부", "status": "pending"},
                    {"step": 4, "name": "개발", "status": "pending"},
                    {"step": 5, "name": "테스트", "status": "pending"},
                    {"step": 6, "name": "배포", "status": "pending"},
                ],
                "bug_report": [
                    {"step": 1, "name": "버그 신고", "status": "completed"},
                    {"step": 2, "name": "검증", "status": "pending"},
                    {"step": 3, "name": "우선순위 결정", "status": "pending"},
                    {"step": 4, "name": "수정", "status": "pending"},
                    {"step": 5, "name": "테스트", "status": "pending"},
                    {"step": 6, "name": "배포", "status": "pending"},
                ],
                "improvement": [
                    {"step": 1, "name": "제안 접수", "status": "completed"},
                    {"step": 2, "name": "검토", "status": "pending"},
                    {"step": 3, "name": "승인/거부", "status": "pending"},
                    {"step": 4, "name": "개발", "status": "pending"},
                    {"step": 5, "name": "테스트", "status": "pending"},
                    {"step": 6, "name": "배포", "status": "pending"},
                ],
            }

            workflow = {
                "id": str(uuid.uuid4()),
                "name": f"{feedback_type} 워크플로우",
                "description": f"{feedback_type} 처리 워크플로우",
                "steps": workflow_steps.get(feedback_type, []),
                "current_step": 1,
                "feedback_id": feedback_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "completed_at": None,
            }

            workflows.append(workflow)
            self._save_workflows(workflows)

        except Exception as e:
            print(f"워크플로우 생성 실패: {e}")

    def _update_workflow(self, feedback_id: str, status: str):
        """워크플로우 업데이트"""
        try:
            workflows = self._load_workflows()
            workflow = next(
                (w for w in workflows if w["feedback_id"] == feedback_id), None
            )

            if not workflow:
                return

            # 상태에 따른 단계 업데이트
            status_to_step = {
                FeedbackStatus.PENDING.value: 1,
                FeedbackStatus.IN_REVIEW.value: 2,
                FeedbackStatus.APPROVED.value: 3,
                FeedbackStatus.IN_DEVELOPMENT.value: 4,
                FeedbackStatus.COMPLETED.value: 6,
                FeedbackStatus.REJECTED.value: 3,
                FeedbackStatus.CANCELLED.value: 1,
            }

            new_step = (
                status_to_step.get(status, workflow["current_step"])
                if status_to_step
                else workflow["current_step"]
            )
            workflow["current_step"] = new_step
            workflow["updated_at"] = datetime.now().isoformat()

            # 완료된 경우
            if status in [
                FeedbackStatus.COMPLETED.value,
                FeedbackStatus.REJECTED.value,
                FeedbackStatus.CANCELLED.value,
            ]:
                workflow["completed_at"] = datetime.now().isoformat()

            self._save_workflows(workflows)

        except Exception as e:
            print(f"워크플로우 업데이트 실패: {e}")

    def _load_feedback(self) -> List[Dict[str, Any]]:
        """피드백 목록 로드"""
        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_feedback(self, feedbacks: List[Dict[str, Any]]):
        """피드백 목록 저장"""
        with open(self.feedback_file, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    def _load_comments(self) -> List[Dict[str, Any]]:
        """댓글 목록 로드"""
        try:
            with open(self.comments_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_comments(self, comments: List[Dict[str, Any]]):
        """댓글 목록 저장"""
        with open(self.comments_file, "w", encoding="utf-8") as f:
            json.dump(comments, f, indent=2, ensure_ascii=False)

    def _load_workflows(self) -> List[Dict[str, Any]]:
        """워크플로우 목록 로드"""
        try:
            with open(self.workflows_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_workflows(self, workflows: List[Dict[str, Any]]):
        """워크플로우 목록 저장"""
        with open(self.workflows_file, "w", encoding="utf-8") as f:
            json.dump(workflows, f, indent=2, ensure_ascii=False)
