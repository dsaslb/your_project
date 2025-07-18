#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
피드백 시스템 초기화 스크립트
샘플 피드백 데이터를 추가합니다.
"""

import sys
import os


# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.backend.plugin_feedback_system import PluginFeedbackSystem


def init_feedback():
    """피드백 시스템 초기화"""
    feedback_system = PluginFeedbackSystem()

    # 샘플 피드백 데이터
    sample_feedbacks = [
        {
            "type": "plugin_request",
            "title": "재고 관리 플러그인 요청",
            "description": "현재 사용 중인 재고 관리 시스템이 너무 복잡하고 사용하기 어렵습니다. 더 직관적이고 사용하기 쉬운 재고 관리 플러그인을 개발해주세요.",
            "user_id": "user1",
            "user_name": "김레스토랑",
            "plugin_id": None,
            "priority": "high",
            "category": "restaurant",
            "tags": ["재고", "관리", "사용성", "직관적"],
        },
        {
            "type": "feature_request",
            "title": "POS 연동 기능 추가",
            "description": "현재 설치된 POS 시스템과의 연동 기능이 부족합니다. 실시간 주문 데이터 동기화와 매출 통계 기능을 추가해주세요.",
            "user_id": "user2",
            "user_name": "이카페",
            "plugin_id": "pos_integration",
            "priority": "medium",
            "category": "restaurant",
            "tags": ["POS", "연동", "주문", "매출"],
        },
        {
            "type": "bug_report",
            "title": "재고 알림이 제대로 작동하지 않음",
            "description": "재고가 부족할 때 알림이 제대로 발송되지 않는 문제가 있습니다. 특정 재료의 재고가 10% 이하로 떨어져도 알림이 오지 않습니다.",
            "user_id": "user3",
            "user_name": "박마트",
            "plugin_id": "inventory_management",
            "priority": "critical",
            "category": "general",
            "tags": ["버그", "알림", "재고", "긴급"],
        },
        {
            "type": "improvement",
            "title": "고객 관리 시스템 개선",
            "description": "현재 고객 관리 시스템의 UI가 너무 복잡합니다. 더 간단하고 직관적인 인터페이스로 개선해주세요.",
            "user_id": "user4",
            "user_name": "최소매",
            "plugin_id": "customer_loyalty",
            "priority": "medium",
            "category": "retail",
            "tags": ["UI", "개선", "사용성", "고객관리"],
        },
        {
            "type": "plugin_request",
            "title": "직원 스케줄링 플러그인",
            "description": "직원들의 근무 스케줄을 효율적으로 관리할 수 있는 플러그인이 필요합니다. 교대 근무, 휴가 관리, 급여 계산 기능을 포함해주세요.",
            "user_id": "user5",
            "user_name": "정매니저",
            "plugin_id": None,
            "priority": "high",
            "category": "general",
            "tags": ["스케줄", "직원", "근무", "급여"],
        },
        {
            "type": "feature_request",
            "title": "모바일 앱 지원",
            "description": "현재 플러그인들이 데스크톱에서만 작동합니다. 모바일 앱에서도 사용할 수 있도록 모바일 지원 기능을 추가해주세요.",
            "user_id": "user6",
            "user_name": "한모바일",
            "plugin_id": "employee_scheduling",
            "priority": "high",
            "category": "general",
            "tags": ["모바일", "앱", "반응형", "접근성"],
        },
        {
            "type": "bug_report",
            "title": "데이터 백업 실패",
            "description": "자동 백업 기능이 정상적으로 작동하지 않습니다. 백업 파일이 생성되지 않거나 손상되는 경우가 있습니다.",
            "user_id": "user7",
            "user_name": "백업관리자",
            "plugin_id": "financial_reporting",
            "priority": "critical",
            "category": "general",
            "tags": ["백업", "데이터", "손실", "긴급"],
        },
        {
            "type": "improvement",
            "title": "보고서 생성 속도 개선",
            "description": "재무 보고서 생성에 시간이 너무 오래 걸립니다. 대용량 데이터 처리 시 성능을 개선해주세요.",
            "user_id": "user8",
            "user_name": "재무팀",
            "plugin_id": "financial_reporting",
            "priority": "medium",
            "category": "general",
            "tags": ["성능", "속도", "보고서", "최적화"],
        },
    ]

    # 피드백 생성
    created_feedbacks = []
    for feedback_data in sample_feedbacks:
        feedback_id = feedback_system.create_feedback(feedback_data)
        if feedback_id:
            created_feedbacks.append(feedback_id)
            print(f"✓ 피드백 생성 완료: {feedback_data['title']}")
        else:
            print(f"✗ 피드백 생성 실패: {feedback_data['title']}")

    # 샘플 댓글 추가
    sample_comments = [
        {
            "feedback_id": created_feedbacks[0] if len(created_feedbacks) > 0 else None,
            "user_id": "admin",
            "user_name": "관리자",
            "user_role": "admin",
            "content": "재고 관리 플러그인 개발을 검토하겠습니다. 예상 완료일은 2주 후입니다.",
            "is_internal": True,
        },
        {
            "feedback_id": created_feedbacks[1] if len(created_feedbacks) > 1 else None,
            "user_id": "developer1",
            "user_name": "개발자A",
            "user_role": "developer",
            "content": "POS 연동 기능 개발을 시작했습니다. API 문서를 참고하여 구현하겠습니다.",
            "is_internal": True,
        },
        {
            "feedback_id": created_feedbacks[2] if len(created_feedbacks) > 2 else None,
            "user_id": "user3",
            "user_name": "박마트",
            "user_role": "user",
            "content": "이 문제가 해결되면 정말 도움이 될 것 같습니다. 빨리 수정해주세요!",
            "is_internal": False,
        },
        {
            "feedback_id": created_feedbacks[3] if len(created_feedbacks) > 3 else None,
            "user_id": "designer1",
            "user_name": "디자이너",
            "user_role": "developer",
            "content": "UI 개선 작업을 진행하겠습니다. 사용자 테스트를 거쳐 더 나은 인터페이스를 제공하겠습니다.",
            "is_internal": True,
        },
    ]

    # 댓글 추가
    for comment_data in sample_comments:
        if comment_data["feedback_id"]:
            comment_id = feedback_system.add_comment(
                comment_data["feedback_id"],
                comment_data["user_id"],
                comment_data["user_name"],
                comment_data["user_role"],
                comment_data["content"],
                comment_data["is_internal"],
            )
            if comment_id:
                print(f"✓ 댓글 추가 완료: {comment_data['user_name']}")
            else:
                print(f"✗ 댓글 추가 실패: {comment_data['user_name']}")

    # 피드백 상태 업데이트
    if len(created_feedbacks) > 0:
        feedback_system.update_feedback_status(
            created_feedbacks[0], "in_review", "검토를 시작합니다."
        )
        feedback_system.update_feedback_status(
            created_feedbacks[1], "approved", "개발 승인되었습니다."
        )
        feedback_system.update_feedback_status(
            created_feedbacks[2], "in_development", "버그 수정을 시작합니다."
        )
        feedback_system.update_feedback_status(
            created_feedbacks[3], "in_review", "UI 개선 검토를 시작합니다."
        )

    # 피드백 할당
    if len(created_feedbacks) > 1:
        feedback_system.assign_feedback(created_feedbacks[1], "개발팀A", "2024-02-15")
        feedback_system.assign_feedback(created_feedbacks[2], "개발팀B", "2024-02-10")

    # 투표 및 팔로우
    for feedback_id in created_feedbacks[:3]:  # 처음 3개 피드백에만
        feedback_system.vote_feedback(feedback_id, "user1", True)
        feedback_system.vote_feedback(feedback_id, "user2", True)
        feedback_system.follow_feedback(feedback_id, "user1", True)
        feedback_system.follow_feedback(feedback_id, "user2", True)

    print("\n피드백 시스템 초기화가 완료되었습니다!")
    print(f"총 {len(created_feedbacks)}개의 피드백이 생성되었습니다.")


if __name__ == "__main__":
    init_feedback()
