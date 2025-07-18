#!/usr/bin/env python3
"""
카카오 API 설정 관리
"""

import os
import json
from pathlib import Path


class KakaoAPIConfig:
    """카카오 API 설정 관리 클래스"""

    def __init__(self, config_file="config/kakao_api.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self):
        """설정 파일 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"카카오 API 설정 파일 로드 실패: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()

    def _get_default_config(self):
        """기본 설정 반환"""
        return {
            "api_key": "",
            "rest_api_key": "",
            "javascript_key": "",
            "admin_key": "",
            "enabled": False,
            "rate_limit": 300,  # 분당 요청 제한
            "timeout": 10,  # 초
            "cache_ttl": 3600,  # 캐시 유효 시간 (초)
            "search_url": "https://dapi.kakao.com/v2/local/search/address.json",
            "keyword_url": "https://dapi.kakao.com/v2/local/search/keyword.json",
        }

    def save_config(self):
        """설정 파일 저장"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"카카오 API 설정 파일 저장 실패: {e}")
            return False

    def get_api_key(self):
        """API 키 반환"""
        return self.config.get("api_key", "")

    def get_rest_api_key(self):
        """REST API 키 반환"""
        return self.config.get("rest_api_key", "")

    def is_enabled(self):
        """API 활성화 여부 확인"""
        return self.config.get("enabled", False) and bool(self.get_api_key())

    def update_config(self, **kwargs):
        """설정 업데이트"""
        self.config.update(kwargs)
        return self.save_config()

    def test_connection(self):
        """API 연결 테스트"""
        import requests

        api_key = self.get_api_key()
        if not api_key:
            return False, "API 키가 설정되지 않았습니다."

        try:
            headers = {"Authorization": f"KakaoAK {api_key}"}

            # 간단한 주소 검색 테스트
            params = {"query": "서울특별시 강남구"}

            response = requests.get(
                self.config["search_url"],
                headers=headers,
                params=params,
                timeout=self.config["timeout"],
            )

            if response.status_code == 200:
                return True, "API 연결 성공"
            else:
                return False, f"API 오류: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"연결 실패: {str(e)}"


# 전역 설정 인스턴스
kakao_config = KakaoAPIConfig()


def get_kakao_config():
    """전역 카카오 설정 반환"""
    return kakao_config


def init_kakao_api():
    """카카오 API 초기화"""
    if kakao_config.is_enabled():
        print("카카오 API 활성화됨")
        return True
    else:
        print("카카오 API 비활성화됨 - API 키 설정 필요")
        return False
