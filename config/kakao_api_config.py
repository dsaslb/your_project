#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Optional

class KakaoAPIConfig:
    """카카오 API 설정"""
    
    def __init__(self):
        self.api_key = os.getenv('KAKAO_API_KEY', '')
        self.rest_api_key = os.getenv('KAKAO_REST_API_KEY', '')
        self.admin_key = os.getenv('KAKAO_ADMIN_KEY', '')
        self.redirect_uri = os.getenv('KAKAO_REDIRECT_URI', 'http://localhost:5000/auth/kakao/callback')
        
    def is_configured(self) -> bool:
        """API 키가 설정되어 있는지 확인"""
        return bool(self.api_key and self.rest_api_key)
    
    def get_api_key(self) -> str:
        """API 키 반환"""
        return self.api_key
    
    def get_rest_api_key(self) -> str:
        """REST API 키 반환"""
        return self.rest_api_key
    
    def get_admin_key(self) -> str:
        """관리자 키 반환"""
        return self.admin_key
    
    def get_redirect_uri(self) -> str:
        """리다이렉트 URI 반환"""
        return self.redirect_uri

# 전역 인스턴스
kakao_config = KakaoAPIConfig() 