"""
OAuth2 인증 시스템
소셜 로그인, 토큰 관리, 권한 부여 기능 제공
"""

import requests
import logging
import json
from typing import Dict, Optional, Any
from urllib.parse import urlencode, parse_qs, urlparse
from flask import current_app, request, redirect, url_for, session
from models_main import User, db
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OAuth2Provider:
    """OAuth2 제공자 기본 클래스"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: str = None) -> str:
        """인증 URL 생성"""
        raise NotImplementedError
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        """액세스 토큰 획득"""
        raise NotImplementedError
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """사용자 정보 조회"""
        raise NotImplementedError

class GoogleOAuth2Provider(OAuth2Provider):
    """Google OAuth2 제공자"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: str = None) -> str:
        """Google 인증 URL 생성"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        """Google 액세스 토큰 획득"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Google 사용자 정보 조회"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.userinfo_url, headers=headers)
        response.raise_for_status()
        
        return response.json()

class KakaoOAuth2Provider(OAuth2Provider):
    """Kakao OAuth2 제공자"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.auth_url = "https://kauth.kakao.com/oauth/authorize"
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.userinfo_url = "https://kapi.kakao.com/v2/user/me"
    
    def get_authorization_url(self, state: str = None) -> str:
        """Kakao 인증 URL 생성"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code'
        }
        
        if state:
            params['state'] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        """Kakao 액세스 토큰 획득"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Kakao 사용자 정보 조회"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.userinfo_url, headers=headers)
        response.raise_for_status()
        
        return response.json()

class OAuth2Manager:
    """OAuth2 인증 관리자"""
    
    def __init__(self, app=None):
        self.app = app
        self.providers = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 OAuth2 초기화"""
        self.app = app
        
        # Google OAuth2 설정
        google_client_id = app.config.get('GOOGLE_CLIENT_ID')
        google_client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
        google_redirect_uri = app.config.get('GOOGLE_REDIRECT_URI')
        
        if google_client_id and google_client_secret and google_redirect_uri:
            self.providers['google'] = GoogleOAuth2Provider(
                google_client_id, google_client_secret, google_redirect_uri
            )
        
        # Kakao OAuth2 설정
        kakao_client_id = app.config.get('KAKAO_CLIENT_ID')
        kakao_client_secret = app.config.get('KAKAO_CLIENT_SECRET')
        kakao_redirect_uri = app.config.get('KAKAO_REDIRECT_URI')
        
        if kakao_client_id and kakao_client_secret and kakao_redirect_uri:
            self.providers['kakao'] = KakaoOAuth2Provider(
                kakao_client_id, kakao_client_secret, kakao_redirect_uri
            )
        
        logger.info(f"OAuth2 인증 시스템 초기화 완료: {list(self.providers.keys())}")
    
    def get_provider(self, provider_name: str) -> Optional[OAuth2Provider]:
        """OAuth2 제공자 조회"""
        return self.providers.get(provider_name)
    
    def start_oauth_flow(self, provider_name: str, state: str = None) -> Optional[str]:
        """OAuth 인증 플로우 시작"""
        provider = self.get_provider(provider_name)
        if not provider:
            logger.error(f"지원하지 않는 OAuth 제공자: {provider_name}")
            return None
        
        try:
            auth_url = provider.get_authorization_url(state)
            return auth_url
        except Exception as e:
            logger.error(f"OAuth 인증 URL 생성 실패: {e}")
            return None
    
    def handle_oauth_callback(self, provider_name: str, code: str, state: str = None) -> Optional[Dict[str, Any]]:
        """OAuth 콜백 처리"""
        provider = self.get_provider(provider_name)
        if not provider:
            logger.error(f"지원하지 않는 OAuth 제공자: {provider_name}")
            return None
        
        try:
            # 액세스 토큰 획득
            token_data = provider.get_access_token(code)
            access_token = token_data.get('access_token')
            
            if not access_token:
                logger.error("액세스 토큰을 획득할 수 없습니다")
                return None
            
            # 사용자 정보 조회
            user_info = provider.get_user_info(access_token)
            
            # 사용자 정보 정규화
            normalized_user_info = self._normalize_user_info(provider_name, user_info)
            
            return {
                'provider': provider_name,
                'access_token': access_token,
                'refresh_token': token_data.get('refresh_token'),
                'user_info': normalized_user_info,
                'state': state
            }
            
        except Exception as e:
            logger.error(f"OAuth 콜백 처리 실패: {e}")
            return None
    
    def _normalize_user_info(self, provider_name: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 정보 정규화"""
        if provider_name == 'google':
            return {
                'id': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'provider': 'google'
            }
        elif provider_name == 'kakao':
            return {
                'id': user_info.get('id'),
                'email': user_info.get('kakao_account', {}).get('email'),
                'name': user_info.get('properties', {}).get('nickname'),
                'picture': user_info.get('properties', {}).get('profile_image'),
                'provider': 'kakao'
            }
        else:
            return user_info
    
    def find_or_create_user(self, oauth_data: Dict[str, Any]) -> Optional[User]:
        """OAuth 사용자 찾기 또는 생성"""
        try:
            user_info = oauth_data['user_info']
            provider = oauth_data['provider']
            
            # 기존 사용자 찾기
            user = User.query.filter_by(
                email=user_info['email'],
                oauth_provider=provider
            ).first()
            
            if user:
                # 기존 사용자 정보 업데이트
                user.last_login = datetime.utcnow()
                user.oauth_id = user_info['id']
                db.session.commit()
                return user
            
            # 새 사용자 생성
            user = User(
                username=user_info['name'] or user_info['email'],
                email=user_info['email'],
                oauth_provider=provider,
                oauth_id=user_info['id'],
                role='employee',  # 기본 역할
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"새 OAuth 사용자 생성: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"OAuth 사용자 처리 실패: {e}")
            db.session.rollback()
            return None

# 전역 OAuth2 관리자 인스턴스
oauth2_manager = OAuth2Manager() 