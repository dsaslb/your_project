import base64
import cv2
import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from pyzbar import pyzbar
from PIL import Image
import io

@dataclass
class ImageAnalysisResult:
    """이미지 분석 결과 데이터 클래스"""
    image_id: str
    analysis_type: str
    confidence: float
    results: Dict
    timestamp: datetime
    processing_time: float

class ImageAnalyzer:
    """이미지 분석 시스템"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # QR 코드 감지기
        self.qr_detector = cv2.QRCodeDetector()
        
        # 텍스트 인식 설정 (OCR)
        self.ocr_config = {
            "lang": "kor+eng",
            "config": "--psm 6"
        }
        
        # 이미지 품질 검사 기준
        self.quality_thresholds = {
            "brightness": {"min": 0.3, "max": 0.8},
            "contrast": {"min": 0.4, "max": 0.9},
            "sharpness": {"min": 50.0},
            "noise": {"max": 0.1}
        }
        
        # 분석 결과 캐시
        self.analysis_cache = {}
        
        # 지원하는 이미지 형식
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def analyze_image(self, image_data: bytes, analysis_types: List[str]) -> List[ImageAnalysisResult]:
        """이미지 분석 수행"""
        try:
            # 이미지 데이터 검증
            if not self._validate_image(image_data):
                raise ValueError("Invalid image data")
            
            # 이미지 디코딩
            image = self._decode_image(image_data)
            if image is None:
                raise ValueError("Failed to decode image")
            
            results = []
            start_time = datetime.now()
            
            for analysis_type in analysis_types:
                try:
                    if analysis_type == "qr_code":
                        result = self._analyze_qr_code(image)
                    elif analysis_type == "ocr":
                        result = self._analyze_ocr(image)
                    elif analysis_type == "quality":
                        result = self._analyze_quality(image)
                    elif analysis_type == "object_detection":
                        result = self._analyze_objects(image)
                    elif analysis_type == "face_detection":
                        result = self._analyze_faces(image)
                    else:
                        self.logger.warning(f"Unsupported analysis type: {analysis_type}")
                        continue
                    
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    analysis_result = ImageAnalysisResult(
                        image_id=self._generate_image_id(image_data),
                        analysis_type=analysis_type,
                        confidence=result.get("confidence", 0.0),
                        results=result,
                        timestamp=datetime.now(),
                        processing_time=processing_time
                    )
                    
                    results.append(analysis_result)
                    
                except Exception as e:
                    self.logger.error(f"Error in {analysis_type} analysis: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing image: {str(e)}")
            raise
    
    def _validate_image(self, image_data: bytes) -> bool:
        """이미지 데이터 검증"""
        try:
            # 파일 시그니처 확인
            if len(image_data) < 8:
                return False
            
            # JPEG 시그니처
            if image_data[:2] == b'\xff\xd8':
                return True
            
            # PNG 시그니처
            if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                return True
            
            # BMP 시그니처
            if image_data[:2] == b'BM':
                return True
            
            return False
            
        except Exception:
            return False
    
    def _decode_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """이미지 디코딩"""
        try:
            # OpenCV로 이미지 디코딩
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            self.logger.error(f"Error decoding image: {str(e)}")
            return None
    
    def _generate_image_id(self, image_data: bytes) -> str:
        """이미지 ID 생성"""
        import hashlib
        return hashlib.md5(image_data).hexdigest()[:16]
    
    def _analyze_qr_code(self, image: np.ndarray) -> Dict:
        """QR 코드 분석"""
        try:
            # QR 코드 감지
            retval, decoded_info, points, straight_qrcode = self.qr_detector.detectAndDecodeMulti(image)
            
            if retval:
                qr_codes = []
                for i, (info, point) in enumerate(zip(decoded_info, points)):
                    if info:  # QR 코드 내용이 있는 경우
                        qr_codes.append({
                            "content": info,
                            "position": point.tolist(),
                            "confidence": 0.9
                        })
                
                return {
                    "qr_codes": qr_codes,
                    "count": len(qr_codes),
                    "confidence": 0.9 if qr_codes else 0.0
                }
            else:
                return {
                    "qr_codes": [],
                    "count": 0,
                    "confidence": 0.0
                }
                
        except Exception as e:
            self.logger.error(f"Error in QR code analysis: {str(e)}")
            return {"qr_codes": [], "count": 0, "confidence": 0.0}
    
    def _analyze_ocr(self, image: np.ndarray) -> Dict:
        """OCR 텍스트 인식"""
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 노이즈 제거
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 이진화
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 텍스트 영역 감지 (더미 구현)
            # 실제로는 Tesseract OCR 사용
            detected_text = self._dummy_ocr(binary)
            
            return {
                "text": detected_text,
                "confidence": 0.8 if detected_text else 0.0,
                "text_regions": []
            }
            
        except Exception as e:
            self.logger.error(f"Error in OCR analysis: {str(e)}")
            return {"text": "", "confidence": 0.0, "text_regions": []}
    
    def _dummy_ocr(self, image: np.ndarray) -> str:
        """더미 OCR 구현"""
        # 실제 구현에서는 Tesseract OCR 사용
        dummy_texts = [
            "주문 번호: 20241201001",
            "총 금액: 25,000원",
            "결제 완료",
            "영수증",
            "레스토랑 매니저"
        ]
        
        import random
        return random.choice(dummy_texts)
    
    def _analyze_quality(self, image: np.ndarray) -> Dict:
        """이미지 품질 분석"""
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 밝기 분석
            brightness = np.mean(gray) / 255.0
            
            # 대비 분석
            contrast = np.std(gray) / 255.0
            
            # 선명도 분석 (Laplacian 분산)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness = laplacian_var
            
            # 노이즈 분석
            noise = self._estimate_noise(gray)
            
            # 품질 점수 계산
            quality_score = self._calculate_quality_score(brightness, contrast, sharpness, noise)
            
            return {
                "brightness": brightness,
                "contrast": contrast,
                "sharpness": sharpness,
                "noise": noise,
                "quality_score": quality_score,
                "is_acceptable": quality_score > 0.6,
                "confidence": 0.9
            }
            
        except Exception as e:
            self.logger.error(f"Error in quality analysis: {str(e)}")
            return {"quality_score": 0.0, "is_acceptable": False, "confidence": 0.0}
    
    def _estimate_noise(self, image: np.ndarray) -> float:
        """노이즈 추정"""
        # 간단한 노이즈 추정 (더 정교한 방법 필요)
        kernel = np.ones((3, 3), np.float32) / 9
        smoothed = cv2.filter2D(image, -1, kernel)
        noise = np.mean(np.abs(image.astype(float) - smoothed.astype(float))) / 255.0
        return noise
    
    def _calculate_quality_score(self, brightness: float, contrast: float, sharpness: float, noise: float) -> float:
        """품질 점수 계산"""
        # 각 지표별 점수 계산
        brightness_score = 1.0 - abs(brightness - 0.5) * 2  # 0.5에 가까울수록 높은 점수
        contrast_score = min(contrast * 2, 1.0)  # 대비가 높을수록 높은 점수
        sharpness_score = min(sharpness / 100, 1.0)  # 선명도가 높을수록 높은 점수
        noise_score = 1.0 - min(noise * 10, 1.0)  # 노이즈가 낮을수록 높은 점수
        
        # 가중 평균
        quality_score = (
            brightness_score * 0.25 +
            contrast_score * 0.25 +
            sharpness_score * 0.3 +
            noise_score * 0.2
        )
        
        return max(0.0, min(1.0, quality_score))
    
    def _analyze_objects(self, image: np.ndarray) -> Dict:
        """객체 감지 (더미 구현)"""
        # 실제 구현에서는 YOLO, TensorFlow Object Detection 등 사용
        
        dummy_objects = [
            {"class": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
            {"class": "table", "confidence": 0.88, "bbox": [50, 50, 400, 250]},
            {"class": "chair", "confidence": 0.82, "bbox": [150, 200, 80, 80]}
        ]
        
        return {
            "objects": dummy_objects,
            "count": len(dummy_objects),
            "confidence": 0.85
        }
    
    def _analyze_faces(self, image: np.ndarray) -> Dict:
        """얼굴 감지 (더미 구현)"""
        # 실제 구현에서는 OpenCV Haar Cascade, Dlib, Face Recognition 등 사용
        
        dummy_faces = [
            {"confidence": 0.92, "bbox": [120, 110, 180, 280]},
            {"confidence": 0.87, "bbox": [300, 150, 160, 240]}
        ]
        
        return {
            "faces": dummy_faces,
            "count": len(dummy_faces),
            "confidence": 0.9
        }
    
    def process_receipt(self, image_data: bytes) -> Dict:
        """영수증 처리"""
        try:
            # OCR 분석
            ocr_result = self._analyze_ocr(self._decode_image(image_data))
            
            # QR 코드 분석
            qr_result = self._analyze_qr_code(self._decode_image(image_data))
            
            # 영수증 정보 추출
            receipt_info = self._extract_receipt_info(ocr_result["text"])
            
            return {
                "receipt_info": receipt_info,
                "ocr_text": ocr_result["text"],
                "qr_codes": qr_result["qr_codes"],
                "confidence": ocr_result["confidence"]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing receipt: {str(e)}")
            return {"receipt_info": {}, "ocr_text": "", "qr_codes": [], "confidence": 0.0}
    
    def _extract_receipt_info(self, text: str) -> Dict:
        """영수증 정보 추출"""
        receipt_info = {}
        
        # 주문 번호 추출
        order_match = re.search(r"주문\s*번호[:\s]*(\d+)", text)
        if order_match:
            receipt_info["order_id"] = order_match.group(1)
        
        # 총 금액 추출
        amount_match = re.search(r"총\s*금액[:\s]*([\d,]+)원", text)
        if amount_match:
            receipt_info["total_amount"] = int(amount_match.group(1).replace(",", ""))
        
        # 날짜 추출
        date_match = re.search(r"(\d{4})[년\-\/](\d{1,2})[월\-\/](\d{1,2})[일]", text)
        if date_match:
            receipt_info["date"] = f"{date_match.group(1)}-{date_match.group(2):0>2}-{date_match.group(3):0>2}"
        
        return receipt_info
    
    def get_analysis_statistics(self) -> Dict:
        """분석 통계"""
        if not self.analysis_cache:
            return {"total_analyses": 0, "analysis_types": {}}
        
        analysis_types = {}
        for result in self.analysis_cache.values():
            analysis_type = result.analysis_type
            analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
        
        return {
            "total_analyses": len(self.analysis_cache),
            "analysis_types": analysis_types,
            "average_confidence": sum(r.confidence for r in self.analysis_cache.values()) / len(self.analysis_cache)
        }
    
    def clear_cache(self):
        """분석 캐시 정리"""
        self.analysis_cache.clear()

# 전역 이미지 분석기 인스턴스
image_analyzer = ImageAnalyzer() 