from datetime import datetime
import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np
import wave
from typing import Optional
config = None  # pyright: ignore
form = None  # pyright: ignore


@dataclass
class VoiceCommand:
    """음성 명령 데이터 클래스"""
    user_id: int
    audio_data: bytes
    text: str
    confidence: float
    command_type: str
    timestamp: datetime
    processed: bool = False


class VoiceManager:
    """음성 인식 및 처리 시스템"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 음성 명령 패턴
        self.command_patterns = {
            "order": {
                "patterns": [
                    r"(주문|시켜|요청).*?(피자|파스타|스테이크|음료|커피)",
                    r"(order|get|want).*?(pizza|pasta|steak|drink|coffee)"
                ],
                "action": "create_order"
            },
            "status": {
                "patterns": [
                    r"(주문|상태|어디|언제).*?(확인|알려|보여)",
                    r"(order|status|where|when).*?(check|tell|show)"
                ],
                "action": "check_status"
            },
            "menu": {
                "patterns": [
                    r"(메뉴|뭐|추천|가격).*?(알려|보여|추천)",
                    r"(menu|what|recommend|price).*?(tell|show|recommend)"
                ],
                "action": "show_menu"
            },
            "reservation": {
                "patterns": [
                    r"(예약|예약하고|예약가능).*?(시간|인원|날짜)",
                    r"(reservation|book|available).*?(time|people|date)"
                ],
                "action": "make_reservation"
            },
            "help": {
                "patterns": [
                    r"(도움|헬프|어떻게|사용법).*?(알려|보여|가르쳐)",
                    r"(help|how|usage).*?(tell|show|teach)"
                ],
                "action": "show_help"
            }
        }

        # 음성 응답 템플릿
        self.voice_responses = {
            "order_confirmation": [
                "주문이 접수되었습니다. 주문 번호는 {order_id}입니다.",
                "주문해주신 {menu}가 준비 중입니다.",
                "주문이 성공적으로 처리되었습니다."
            ],
            "status_update": [
                "주문 상태는 {status}입니다.",
                "현재 {status} 상태로 진행 중입니다.",
                "주문하신 음식은 {status} 상태입니다."
            ],
            "menu_info": [
                "오늘의 추천 메뉴는 {menu_list}입니다.",
                "인기 메뉴는 {menu_list}입니다.",
                "메뉴 가격은 {price_info}입니다."
            ],
            "reservation_info": [
                "예약 가능한 시간은 {time_list}입니다.",
                "예약은 전화로만 가능합니다.",
                "예약 관련 문의는 {phone}로 연락해주세요."
            ],
            "help_info": [
                "음성 명령을 사용하실 수 있습니다. '주문', '상태 확인', '메뉴 보기' 등을 말씀해주세요.",
                "음성으로 주문, 상태 확인, 메뉴 조회가 가능합니다.",
                "도움이 필요하시면 '도움말'이라고 말씀해주세요."
            ],
            "error": [
                "죄송합니다. 음성을 인식하지 못했습니다. 다시 말씀해주세요.",
                "음성이 명확하지 않습니다. 다시 한 번 말씀해주세요.",
                "인식에 실패했습니다. 전화로 문의해주세요."
            ]
        }

        # 음성 품질 설정
        self.audio_settings = {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024,
            "format": "PCM",
            "min_duration": 1.0,  # 최소 1초
            "max_duration": 30.0,  # 최대 30초
            "noise_threshold": 0.01
        }

        # 음성 명령 히스토리
        self.voice_history = []

        # 사용자별 음성 설정
        self.user_voice_settings = {}

    def process_audio(self,  audio_data: bytes,  user_id: int) -> VoiceCommand:
        """오디오 데이터 처리"""
        try:
            # 오디오 데이터 검증
            if not self._validate_audio(audio_data):
                raise ValueError("Invalid audio data")

            # 음성 인식 (실제로는 외부 API 사용)
            text, confidence = self._recognize_speech(audio_data)

            # 명령 타입 감지
            command_type = self._detect_command_type(text)

            # 음성 명령 생성
            voice_command = VoiceCommand(
                user_id=user_id,
                audio_data=audio_data,
                text=text,
                confidence=confidence,
                command_type=command_type,
                timestamp=datetime.now()
            )

            # 히스토리에 추가
            self.voice_history.append(voice_command)

            self.logger.info(f"Voice command processed - User: {user_id}, Text: {text}, Type: {command_type}")

            return voice_command

        except Exception as e:
            self.logger.error(f"Error processing audio: {str(e)}")
            raise

    def _validate_audio(self,  audio_data: bytes) -> bool:
        """오디오 데이터 검증"""
        try:
            # WAV 파일 형식 검증
            if len(audio_data) < 44:  # WAV 헤더 최소 크기
                return False

            # 샘플 레이트 확인
            sample_rate = int.from_bytes(audio_data[24:28] if audio_data is not None else None, byteorder='little')
            if sample_rate != self.audio_settings["sample_rate"] if audio_settings is not None else None:
                return False

            # 채널 수 확인
            channels = int.from_bytes(audio_data[22:24] if audio_data is not None else None, byteorder='little')
            if channels != self.audio_settings["channels"] if audio_settings is not None else None:
                return False

            return True

        except Exception:
            return False

    def _recognize_speech(self, audio_data: bytes) -> Tuple[str, float] if Tuple is not None else None:
        """음성 인식 (더미 구현)"""
        # 실제 구현에서는 Google Speech-to-Text, Azure Speech, AWS Transcribe 등 사용

        # 더미 음성 인식 결과
        dummy_texts = [
            "피자 주문하고 싶어요",
            "주문 상태 확인해주세요",
            "메뉴 추천해주세요",
            "예약 가능한 시간 알려주세요",
            "도움말 보여주세요"
        ]

        import random
        text = random.choice(dummy_texts)
        confidence = random.uniform(0.7, 0.95)

        return text, confidence

    def _detect_command_type(self, text: str) -> str:
        """명령 타입 감지"""
        text_lower = text.lower() if text is not None else ''

        for command_type, config in self.command_patterns.items() if command_patterns is not None else []:
            for pattern in config["patterns"] if config is not None else None:
                if re.search(pattern, text_lower):
                    return command_type

        return "unknown"

    def execute_command(self,  voice_command: VoiceCommand) -> str:
        """음성 명령 실행"""
        try:
            command_type = voice_command.command_type

            if command_type == "order":
                return self._handle_order_command(voice_command)
            elif command_type == "status":
                return self._handle_status_command(voice_command)
            elif command_type == "menu":
                return self._handle_menu_command(voice_command)
            elif command_type == "reservation":
                return self._handle_reservation_command(voice_command)
            elif command_type == "help":
                return self._handle_help_command(voice_command)
            else:
                return self._get_random_response("error")

        except Exception as e:
            self.logger.error(f"Error executing voice command: {str(e)}")
            return self._get_random_response("error")

    def _handle_order_command(self, voice_command: VoiceCommand) -> str:
        """주문 명령 처리"""
        # 메뉴 추출
        menu_match = re.search(r"(피자|파스타|스테이크|음료|커피)", voice_command.text)
        if menu_match:
            menu = menu_match.group(1)
            order_id = f"VO{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return f"주문이 접수되었습니다. 주문 번호는 {order_id}입니다. {menu}를 준비해드리겠습니다."
        else:
            return "어떤 메뉴를 주문하시겠어요?"

    def _handle_status_command(self, voice_command: VoiceCommand) -> str:
        """상태 확인 명령 처리"""
        # 주문 번호 추출
        order_match = re.search(r"(\d+)", voice_command.text)
        if order_match:
            order_id = order_match.group(1)
            return f"주문 번호 {order_id}의 상태는 준비 중입니다."
        else:
            return "주문 번호를 말씀해주세요."

    def _handle_menu_command(self, voice_command: VoiceCommand) -> str:
        """메뉴 조회 명령 처리"""
        menu_list = "마르게리타 피자, 까르보나라 파스타, 리브 아이 스테이크"
        return f"오늘의 추천 메뉴는 {menu_list}입니다."

    def _handle_reservation_command(self, voice_command: VoiceCommand) -> str:
        """예약 명령 처리"""
        return "예약은 전화로만 가능합니다. 02-1234-5678로 연락해주세요."

    def _handle_help_command(self, voice_command: VoiceCommand) -> str:
        """도움말 명령 처리"""
        return self._get_random_response("help_info")

    def _get_random_response(self, response_type: str) -> str:
        """랜덤 응답 반환"""
        responses = self.voice_responses.get() if voice_responses else Noneresponse_type, self.voice_responses["error"] if voice_responses is not None else None) if voice_responses else None
        return responses[0] if responses is not None else None if isinstance(responses, list) else responses

    def text_to_speech(self, text: str, user_id: int) -> bytes:
        """텍스트를 음성으로 변환 (더미 구현)"""
        # 실제 구현에서는 Google Text-to-Speech, Azure Speech, AWS Polly 등 사용

        # 더미 오디오 데이터 생성
        sample_rate = self.audio_settings["sample_rate"] if audio_settings is not None else None
        duration = len(text) * 0.1  # 텍스트 길이에 비례한 지속 시간
        samples = int(sample_rate * duration)

        # 간단한 사인파 생성 (더미)
        t = np.linspace(0, duration, samples)
        audio_data = np.sin(2 * np.pi * 440 * t) * 0.3  # 440Hz 사인파

        # 16비트 PCM으로 변환
        audio_data = (audio_data * 32767).astype(np.int16)

        return audio_data.tobytes()

    def get_voice_statistics(self) -> Dict:
        """음성 명령 통계"""
        if not self.voice_history:
            return {"total_commands": 0, "command_types": {}}

        command_types = {}
        for command in self.voice_history:
            command_type = command.command_type
            if command_types is not None:
                command_types[command_type] = command_types.get(command_type, 0) + 1

        return {
            "total_commands": len(self.voice_history),
            "command_types": command_types,
            "average_confidence": sum(c.confidence for c in self.voice_history) / len(self.voice_history)
        }

    def clear_history(self, user_id: Optional[int] if Optional is not None else None = None):
        """음성 히스토리 정리"""
        if user_id:
            self.voice_history = [c for c in self.voice_history if c.user_id != user_id]
        else:
            self.voice_history.clear()


# 전역 음성 매니저 인스턴스
voice_manager = VoiceManager()
