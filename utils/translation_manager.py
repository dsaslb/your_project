import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class TranslationRequest:
    """번역 요청 데이터 클래스"""
    request_id: str
    source_text: str
    source_language: str
    target_language: str
    timestamp: datetime
    user_id: Optional[int] = None

@dataclass
class TranslationResult:
    """번역 결과 데이터 클래스"""
    request_id: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    timestamp: datetime
    processing_time: float

class TranslationManager:
    """실시간 번역 시스템"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 지원 언어
        self.supported_languages = {
            "ko": "한국어",
            "en": "English",
            "ja": "日本語",
            "zh": "中文",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "ru": "Русский"
        }
        
        # 언어 감지 패턴
        self.language_patterns = {
            "ko": r"[가-힣]",
            "ja": r"[あ-んア-ン]",
            "zh": r"[一-龯]",
            "en": r"[a-zA-Z]",
            "es": r"[áéíóúñü]",
            "fr": r"[àâäéèêëïîôöùûüÿç]",
            "de": r"[äöüß]",
            "ru": r"[а-яё]"
        }
        
        # 번역 캐시
        self.translation_cache = {}
        
        # 번역 히스토리
        self.translation_history = []
        
        # 메뉴 번역 데이터베이스
        self.menu_translations = {
            "ko": {
                "피자": "피자",
                "파스타": "파스타",
                "스테이크": "스테이크",
                "샐러드": "샐러드",
                "음료": "음료",
                "커피": "커피",
                "디저트": "디저트"
            },
            "en": {
                "피자": "Pizza",
                "파스타": "Pasta",
                "스테이크": "Steak",
                "샐러드": "Salad",
                "음료": "Beverage",
                "커피": "Coffee",
                "디저트": "Dessert"
            },
            "ja": {
                "피자": "ピザ",
                "파스타": "パスタ",
                "스테이크": "ステーキ",
                "샐러드": "サラダ",
                "음료": "飲み物",
                "커피": "コーヒー",
                "디저트": "デザート"
            },
            "zh": {
                "피자": "披萨",
                "파스타": "意大利面",
                "스테이크": "牛排",
                "샐러드": "沙拉",
                "음료": "饮料",
                "커피": "咖啡",
                "디저트": "甜点"
            }
        }
        
        # 일반적인 번역 데이터베이스
        self.common_translations = {
            "ko-en": {
                "주문": "Order",
                "예약": "Reservation",
                "메뉴": "Menu",
                "가격": "Price",
                "영업시간": "Business Hours",
                "위치": "Location",
                "전화번호": "Phone Number",
                "감사합니다": "Thank you",
                "죄송합니다": "Sorry",
                "환영합니다": "Welcome"
            },
            "en-ko": {
                "Order": "주문",
                "Reservation": "예약",
                "Menu": "메뉴",
                "Price": "가격",
                "Business Hours": "영업시간",
                "Location": "위치",
                "Phone Number": "전화번호",
                "Thank you": "감사합니다",
                "Sorry": "죄송합니다",
                "Welcome": "환영합니다"
            }
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """언어 감지"""
        if not text:
            return "ko", 0.0
        
        language_scores = {}
        
        for lang_code, pattern in self.language_patterns.items():
            matches = re.findall(pattern, text)
            score = len(matches) / len(text) if text else 0.0
            language_scores[lang_code] = score
        
        # 가장 높은 점수의 언어 반환
        if language_scores:
            try:
                detected_lang = max(language_scores.keys(), key=lambda k: language_scores[k])
                confidence = language_scores[detected_lang]
                return detected_lang, confidence
            except (ValueError, KeyError):
                return "ko", 0.0
        
        return "ko", 0.0
    
    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> TranslationResult:
        """텍스트 번역"""
        try:
            start_time = datetime.now()
            
            # 언어 감지 (소스 언어가 지정되지 않은 경우)
            if not source_language:
                source_language, confidence = self.detect_language(text)
            else:
                confidence = 0.9
            
            # 지원 언어 확인
            if target_language not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            # 캐시 확인
            cache_key = f"{text}_{source_language}_{target_language}"
            if cache_key in self.translation_cache:
                cached_result = self.translation_cache[cache_key]
                cached_result.timestamp = datetime.now()
                return cached_result
            
            # 번역 수행
            translated_text = self._perform_translation(text, source_language, target_language)
            
            # 처리 시간 계산
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 번역 결과 생성
            result = TranslationResult(
                request_id=self._generate_request_id(),
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                confidence=confidence,
                timestamp=datetime.now(),
                processing_time=processing_time
            )
            
            # 캐시에 저장
            self.translation_cache[cache_key] = result
            
            # 히스토리에 추가
            self.translation_history.append(result)
            
            self.logger.info(f"Translation completed - {source_language} -> {target_language}: {text[:50]}...")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in translation: {str(e)}")
            raise
    
    def _perform_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """실제 번역 수행 (더미 구현)"""
        # 실제 구현에서는 Google Translate, Azure Translator, AWS Translate 등 사용
        
        # 메뉴 번역 확인
        if source_lang in self.menu_translations and target_lang in self.menu_translations:
            for ko_word, target_word in self.menu_translations[target_lang].items():
                if ko_word in text:
                    text = text.replace(ko_word, target_word)
        
        # 일반 번역 확인
        translation_key = f"{source_lang}-{target_lang}"
        if translation_key in self.common_translations:
            for source_word, target_word in self.common_translations[translation_key].items():
                if source_word.lower() in text.lower():
                    text = text.replace(source_word, target_word)
        
        # 더미 번역 (실제로는 외부 API 사용)
        dummy_translations = {
            "ko-en": {
                "안녕하세요": "Hello",
                "주문하고 싶어요": "I would like to order",
                "메뉴를 보여주세요": "Please show me the menu",
                "가격이 얼마인가요": "How much is it?",
                "감사합니다": "Thank you"
            },
            "en-ko": {
                "Hello": "안녕하세요",
                "I would like to order": "주문하고 싶어요",
                "Please show me the menu": "메뉴를 보여주세요",
                "How much is it?": "가격이 얼마인가요",
                "Thank you": "감사합니다"
            }
        }
        
        translation_key = f"{source_lang}-{target_lang}"
        if translation_key in dummy_translations:
            for source_word, target_word in dummy_translations[translation_key].items():
                if source_word.lower() in text.lower():
                    text = text.replace(source_word, target_word)
        
        return text
    
    def translate_menu(self, menu_items: List[Dict], target_language: str) -> List[Dict]:
        """메뉴 번역"""
        try:
            translated_menu = []
            
            for item in menu_items:
                translated_item = item.copy()
                
                # 메뉴 이름 번역
                if "name" in item and target_language in self.menu_translations:
                    ko_name = item["name"]
                    if ko_name in self.menu_translations[target_language]:
                        translated_item["name"] = self.menu_translations[target_language][ko_name]
                
                # 설명 번역
                if "description" in item:
                    translated_item["description"] = self.translate_text(
                        item["description"], target_language, "ko"
                    ).translated_text
                
                translated_menu.append(translated_item)
            
            return translated_menu
            
        except Exception as e:
            self.logger.error(f"Error translating menu: {str(e)}")
            return menu_items
    
    def translate_notification(self, notification: Dict, target_language: str) -> Dict:
        """알림 번역"""
        try:
            translated_notification = notification.copy()
            
            # 제목 번역
            if "title" in notification:
                translated_notification["title"] = self.translate_text(
                    notification["title"], target_language, "ko"
                ).translated_text
            
            # 내용 번역
            if "content" in notification:
                translated_notification["content"] = self.translate_text(
                    notification["content"], target_language, "ko"
                ).translated_text
            
            return translated_notification
            
        except Exception as e:
            self.logger.error(f"Error translating notification: {str(e)}")
            return notification
    
    def batch_translate(self, texts: List[str], target_language: str, source_language: Optional[str] = None) -> List[TranslationResult]:
        """배치 번역"""
        results = []
        
        for text in texts:
            try:
                result = self.translate_text(text, target_language, source_language)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error in batch translation: {str(e)}")
                # 에러가 발생해도 계속 진행
                continue
        
        return results
    
    def _generate_request_id(self) -> str:
        """요청 ID 생성"""
        return f"TR{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
    
    def get_translation_statistics(self) -> Dict:
        """번역 통계"""
        if not self.translation_history:
            return {"total_translations": 0, "language_pairs": {}}
        
        language_pairs = {}
        for result in self.translation_history:
            pair = f"{result.source_language}-{result.target_language}"
            language_pairs[pair] = language_pairs.get(pair, 0) + 1
        
        return {
            "total_translations": len(self.translation_history),
            "language_pairs": language_pairs,
            "average_confidence": sum(r.confidence for r in self.translation_history) / len(self.translation_history),
            "average_processing_time": sum(r.processing_time for r in self.translation_history) / len(self.translation_history)
        }
    
    def clear_cache(self):
        """번역 캐시 정리"""
        self.translation_cache.clear()
    
    def clear_history(self):
        """번역 히스토리 정리"""
        self.translation_history.clear()

# 전역 번역 매니저 인스턴스
translation_manager = TranslationManager() 