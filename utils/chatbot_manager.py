from typing import Optional
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random


@dataclass
class ChatMessage:
    """채팅 메시지 데이터 클래스"""
    user_id: int
    message: str
    timestamp: datetime
    message_type: str = "user"  # user, bot, system
    intent: str = ""
    confidence: float = 0.0
    entities: Dict = None
    response: str = ""


class ChatbotManager:
    """AI 챗봇 관리 시스템"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 의도 패턴 정의
        self.intent_patterns = {
            "order_status": [
                r"주문.*상태|주문.*어디|주문.*언제|주문.*확인",
                r"order.*status|order.*where|order.*when|order.*check"
            ],
            "menu_inquiry": [
                r"메뉴.*뭐|메뉴.*추천|메뉴.*가격|메뉴.*종류",
                r"menu.*what|menu.*recommend|menu.*price|menu.*type"
            ],
            "reservation": [
                r"예약.*하고|예약.*가능|예약.*시간|예약.*인원",
                r"reservation.*make|reservation.*available|reservation.*time|reservation.*people"
            ],
            "business_hours": [
                r"영업.*시간|영업.*언제|영업.*몇시|영업.*마감",
                r"business.*hours|business.*when|business.*time|business.*close"
            ],
            "location": [
                r"위치.*어디|위치.*찾기|위치.*오시는길|위치.*주소",
                r"location.*where|location.*find|location.*direction|location.*address"
            ],
            "complaint": [
                r"불만.*있어|불만.*말씀|불만.*제기|불만.*해결",
                r"complaint.*have|complaint.*tell|complaint.*file|complaint.*resolve"
            ],
            "praise": [
                r"칭찬.*좋아|칭찬.*맛있어|칭찬.*서비스|칭찬.*감사",
                r"praise.*good|praise.*delicious|praise.*service|praise.*thank"
            ],
            "general_inquiry": [
                r"문의.*있어|문의.*질문|문의.*궁금|문의.*알려",
                r"inquiry.*have|inquiry.*question|inquiry.*wonder|inquiry.*tell"
            ]
        }

        # 응답 템플릿
        self.response_templates = {
            "order_status": {
                "greeting": [
                    "주문 상태를 확인해드리겠습니다.",
                    "주문하신 내용을 확인해보겠습니다.",
                    "주문 상태를 알려드리겠습니다."
                ],
                "not_found": [
                    "죄송합니다. 주문 정보를 찾을 수 없습니다. 주문 번호를 다시 확인해주세요.",
                    "해당 주문을 찾을 수 없습니다. 정확한 주문 번호를 알려주세요."
                ],
                "status_update": [
                    "주문 번호 {order_id}의 현재 상태는 {status}입니다.",
                    "주문하신 {order_id}번은 현재 {status} 상태입니다."
                ]
            },
            "menu_inquiry": {
                "greeting": [
                    "메뉴에 대해 알려드리겠습니다.",
                    "어떤 메뉴가 궁금하신가요?",
                    "메뉴 정보를 확인해드리겠습니다."
                ],
                "popular": [
                    "인기 메뉴는 {menu_list}입니다.",
                    "고객들이 많이 주문하시는 메뉴는 {menu_list}입니다."
                ],
                "price": [
                    "{menu_name}의 가격은 {price}원입니다.",
                    "{menu_name}는 {price}원에 판매하고 있습니다."
                ]
            },
            "reservation": {
                "greeting": [
                    "예약 서비스를 도와드리겠습니다.",
                    "예약에 대해 문의해주셨네요.",
                    "예약 관련 정보를 알려드리겠습니다."
                ],
                "available": [
                    "예약 가능한 시간은 {time_list}입니다.",
                    "현재 {time_list}에 예약이 가능합니다."
                ],
                "process": [
                    "예약은 전화로만 가능합니다. {phone_number}로 연락해주세요.",
                    "예약은 {phone_number}로 전화 주시면 됩니다."
                ]
            },
            "business_hours": {
                "greeting": [
                    "영업 시간을 알려드리겠습니다.",
                    "영업 시간에 대해 문의해주셨네요."
                ],
                "hours": [
                    "영업 시간은 {hours}입니다.",
                    "매일 {hours}에 영업하고 있습니다."
                ]
            },
            "location": {
                "greeting": [
                    "위치 정보를 알려드리겠습니다.",
                    "오시는 길을 안내해드리겠습니다."
                ],
                "address": [
                    "주소는 {address}입니다.",
                    "{address}에 위치해 있습니다."
                ],
                "direction": [
                    "오시는 길: {direction}",
                    "찾아오시는 방법: {direction}"
                ]
            },
            "complaint": [
                "불편을 끼쳐 죄송합니다. 더 자세한 내용을 전화로 말씀해주시면 빠르게 해결해드리겠습니다.",
                "고객님의 불편사항을 해결해드리겠습니다. {phone_number}로 연락해주세요."
            ],
            "praise": [
                "좋은 말씀 감사합니다! 더 나은 서비스로 보답하겠습니다.",
                "고객님의 만족이 저희의 기쁨입니다. 감사합니다!",
                "좋은 평가 감사합니다. 앞으로도 최선을 다하겠습니다."
            ],
            "general_inquiry": [
                "문의사항이 있으시면 언제든 연락해주세요. {phone_number}",
                "궁금한 점이 있으시면 전화로 문의해주세요.",
                "추가 문의사항은 {phone_number}로 연락해주세요."
            ],
            "fallback": [
                "죄송합니다. 질문을 이해하지 못했습니다. 다시 말씀해주시거나 전화로 문의해주세요.",
                "죄송합니다. 다른 방법으로 문의해주시겠어요?",
                "이해하지 못했습니다. 전화로 문의해주시면 더 정확한 답변을 드릴 수 있습니다."
            ]
        }

        # 엔티티 추출 패턴
        self.entity_patterns = {
            "order_id": r"주문[번호] if 주문 is not None else None*\s*[#]?\s*(\d+)",
            "menu_name": r"(피자|파스타|스테이크|샐러드|음료|커피|디저트)",
            "time": r"(\d{1,2}시|\d{1,2}:\d{2})",
            "date": r"(\d{1,2}월\s*\d{1,2}일|\d{4}년\s*\d{1,2}월\s*\d{1,2}일)",
            "phone_number": r"(\d{2,3}-\d{3,4}-\d{4})"
        }

        # 대화 컨텍스트 저장
        self.conversation_contexts = {}

        # 기본 정보
        self.your_program_info = {
            "name": "레스토랑 매니저",
            "phone": "02-1234-5678",
            "address": "서울시 강남구 테헤란로 123",
            "hours": "평일 11:00-22:00, 주말 10:00-23:00",
            "popular_menus": ["마르게리타 피자", "까르보나라 파스타", "리브 아이 스테이크"]
        }

    def detect_intent(self,  message: str) -> Tuple[str, float] if Tuple is not None else None:
        """의도 감지"""
        message_lower = message.lower() if message is not None else ''
        max_confidence = 0.0
        detected_intent = "general_inquiry"

        for intent, patterns in self.intent_patterns.items() if intent_patterns is not None else []:
            for pattern in patterns if patterns is not None:
                matches = re.findall(pattern, message_lower)
                if matches:
                    confidence = len(matches) / len(patterns) * 0.8 + 0.2
                    if confidence > max_confidence:
                        max_confidence = confidence
                        detected_intent = intent

        return detected_intent, max_confidence

    def extract_entities(self, message: str) -> Dict:
        """엔티티 추출"""
        entities = {}

        for entity_type, pattern in self.entity_patterns.items() if entity_patterns is not None else []:
            matches = re.findall(pattern, message)
            if matches:
                entities[entity_type] if entities is not None else None = matches[0] if matches is not None else None if len(matches) == 1 else matches

        return entities

    def generate_response(self, intent: str, entities: Dict, context: Optional[Dict] = None) -> str:
        """응답 생성"""
        templates = self.response_templates.get() if response_templates else Noneintent, {}) if response_templates else None

        if isinstance(templates, list):
            # 단순 리스트인 경우
            response = random.choice(templates)
        else:
            # 딕셔너리인 경우 (greeting, specific 등)
            if "greeting" in templates:
                response = random.choice(templates["greeting"] if templates is not None else None)
            else:
                response = random.choice(templates.get() if templates else None"fallback", self.response_templates["fallback"] if response_templates is not None else None) if templates else None)

        # 엔티티 치환
        if entities:
            for entity_type, value in entities.items() if entities is not None else []:
                placeholder = f"{{{entity_type}}}"
                if placeholder in response:
                    response = response.replace(placeholder, str(value))

        # 레스토랑 정보 치환
        response = response.replace("{phone_number}", self.your_program_info["phone"] if your_program_info is not None else None)
        response = response.replace("{address}", self.your_program_info["address"] if your_program_info is not None else None)
        response = response.replace("{hours}", self.your_program_info["hours"] if your_program_info is not None else None)

        # 메뉴 정보 치환
        if "menu_list" in response:
            menu_list = ", ".join(self.your_program_info["popular_menus"] if your_program_info is not None else None)
            response = response.replace("{menu_list}", menu_list)

        return response

    def process_message(self,  user_id: int,  message: str) -> ChatMessage:
        """메시지 처리"""
        timestamp = datetime.now()

        # 의도 감지
        intent, confidence = self.detect_intent(message)

        # 엔티티 추출
        entities = self.extract_entities(message)

        # 컨텍스트 가져오기
        context = self.conversation_contexts.get() if conversation_contexts else Noneuser_id, {}) if conversation_contexts else None

        # 응답 생성
        response = self.generate_response(intent, entities, context)

        # 컨텍스트 업데이트
        context.update({
            "last_intent": intent,
            "last_entities": entities,
            "last_message": message,
            "timestamp": timestamp
        })
        self.conversation_contexts[user_id] if conversation_contexts is not None else None = context

        # 채팅 메시지 생성
        chat_message = ChatMessage(
            user_id=user_id,
            message=message,
            timestamp=timestamp,
            intent=intent,
            confidence=confidence,
            entities=entities,
            response=response
        )

        self.logger.info(f"Chat processed - User: {user_id}, Intent: {intent}, Confidence: {confidence}")

        return chat_message

    def get_conversation_history(self, user_id: int, limit: int = 10) -> List[ChatMessage] if List is not None else None:
        """대화 히스토리 조회"""
        # 실제 구현에서는 데이터베이스에서 조회
        return []

    def clear_context(self, user_id: int):
        """대화 컨텍스트 초기화"""
        if user_id in self.conversation_contexts:
            del self.conversation_contexts[user_id] if conversation_contexts is not None else None

    def get_chat_statistics(self) -> Dict:
        """채팅 통계"""
        total_conversations = len(self.conversation_contexts)

        intent_counts = {}
        for context in self.conversation_contexts.value if conversation_contexts is not None else Nones():
            intent = context.get() if context else None"last_intent", "unknown") if context else None
            intent_counts[intent] if intent_counts is not None else None = intent_counts.get() if intent_counts else Noneintent, 0) if intent_counts else None + 1

        return {
            "total_conversations": total_conversations,
            "intent_distribution": intent_counts,
            "active_contexts": len(self.conversation_contexts)
        }


# 전역 챗봇 매니저 인스턴스
chatbot_manager = ChatbotManager()
