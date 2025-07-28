"""
보안 강화 시스템
- 입력 검증 및 정제
- 인증 및 권한 관리
- XSS/CSRF 방지
- SQL Injection 방지
- Rate Limiting
- 보안 로깅
"""

import re
import hashlib
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from functools import wraps
from flask import request, jsonify, current_app, g, session
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """보안 관리 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        self.security_logger = logging.getLogger('security')
        self.rate_limit_store = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱 초기화"""
        self.app = app
        
        # 보안 헤더 설정
        app.after_request(self.add_security_headers)
        
        # 요청 전 보안 검사
        app.before_request(self.security_check)
    
    def add_security_headers(self, response):
        """보안 헤더 추가"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:;"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
    
    def security_check(self):
        """요청 전 보안 검사"""
        # IP 화이트리스트/블랙리스트 검사
        if not self._check_ip_allowed(request.remote_addr):
            self.security_logger.warning(f"Blocked request from IP: {request.remote_addr}")
            return jsonify({'error': '접근이 차단되었습니다.'}), 403
        
        # User-Agent 검사
        if not self._check_user_agent(request.headers.get('User-Agent', '')):
            self.security_logger.warning(f"Suspicious User-Agent: {request.headers.get('User-Agent')}")
            return jsonify({'error': '잘못된 요청입니다.'}), 400
        
        # Rate Limiting 검사
        if not self._check_rate_limit(request.remote_addr):
            self.security_logger.warning(f"Rate limit exceeded for IP: {request.remote_addr}")
            return jsonify({'error': '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.'}), 429
    
    def _check_ip_allowed(self, ip: str) -> bool:
        """IP 허용 여부 검사"""
        # 블랙리스트 IP (실제로는 DB나 설정에서 관리)
        blacklist_ips = [
            '192.168.1.100',  # 예시
            '10.0.0.50'       # 예시
        ]
        
        return ip not in blacklist_ips
    
    def _check_user_agent(self, user_agent: str) -> bool:
        """User-Agent 검사"""
        if not user_agent:
            return False

        # 의심스러운 User-Agent 패턴
        suspicious_patterns = [
            r'bot',
            r'crawler',
            r'spider',
            r'scanner',
            r'curl',
            r'wget',
            r'python-requests'
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent_lower):
                return False
        
        return True
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Rate Limiting 검사"""
        now = datetime.now()
        window = timedelta(minutes=1)
        
        if ip not in self.rate_limit_store:
            self.rate_limit_store[ip] = []

        # 오래된 요청 제거
        self.rate_limit_store[ip] = [
            req_time for req_time in self.rate_limit_store[ip]
            if now - req_time < window
        ]
        
        # 요청 수 제한 (분당 100회)
        if len(self.rate_limit_store[ip]) >= 100:
            return False

        self.rate_limit_store[ip].append(now)
        return True

    def sanitize_input(self, data: Any) -> Any:
        """입력 데이터 정제"""
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data
    
    def _sanitize_string(self, text: str) -> str:
        """문자열 정제"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수 문자 이스케이프
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        # SQL Injection 패턴 제거
        sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
            r'(\b(exec|execute|script)\b)',
            r'(\b(xp_|sp_)\w+)',
            r'(\b(declare|cast|convert)\b)'
        ]
        
        for pattern in sql_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def validate_email(self, email: str) -> bool:
        """이메일 유효성 검사"""
        if not email:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """비밀번호 유효성 검사"""
        if not password:
            return {'valid': False, 'message': '비밀번호를 입력해주세요.'}
        
        # 최소 길이
        if len(password) < 8:
            return {'valid': False, 'message': '비밀번호는 최소 8자 이상이어야 합니다.'}
        
        # 최대 길이
        if len(password) > 128:
            return {'valid': False, 'message': '비밀번호는 최대 128자까지 가능합니다.'}
        
        # 복잡성 검사
        has_upper = re.search(r'[A-Z]', password)
        has_lower = re.search(r'[a-z]', password)
        has_digit = re.search(r'\d', password)
        has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            return {
                'valid': False, 
                'message': '비밀번호는 대문자, 소문자, 숫자, 특수문자를 모두 포함해야 합니다.'
            }
        
        # 연속된 문자 검사
        if re.search(r'(.)\1{2,}', password):
            return {'valid': False, 'message': '연속된 같은 문자는 3개 이상 사용할 수 없습니다.'}
        
        # 일반적인 비밀번호 검사
        common_passwords = [
            'password', '123456', 'qwerty', 'admin', 'user',
            'password123', '123456789', 'qwerty123', 'admin123'
        ]
        
        if password.lower() in common_passwords:
            return {'valid': False, 'message': '너무 일반적인 비밀번호입니다.'}
        
        return {'valid': True, 'message': '유효한 비밀번호입니다.'}
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: int, expires_in: int = 3600) -> str:
        """JWT 토큰 생성"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(32)
        }
        
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def log_security_event(self, event_type: str, details: Dict, severity: str = 'info'):
        """보안 이벤트 로깅"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'user_id': getattr(current_user, 'id', None),
            'details': details
        }
        
        if severity == 'warning':
            self.security_logger.warning(f"Security event: {event_type}", extra=log_data)
        elif severity == 'error':
            self.security_logger.error(f"Security event: {event_type}", extra=log_data)
        else:
            self.security_logger.info(f"Security event: {event_type}", extra=log_data)


# 전역 보안 매니저 인스턴스
security_manager = SecurityManager()


# 데코레이터들
def require_authentication(func):
    """인증 필요 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            security_manager.log_security_event(
                'authentication_required',
                {'endpoint': request.path},
                'warning'
            )
            return jsonify({'error': '로그인이 필요합니다.'}), 401
        return func(*args, **kwargs)
    return wrapper


def require_permission(permission: str, resource: str = None):
    """권한 필요 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': '로그인이 필요합니다.'}), 401
            
            if not current_user.has_permission(permission, resource):
                security_manager.log_security_event(
                    'permission_denied',
                    {
                        'endpoint': request.path,
                        'permission': permission,
                        'resource': resource,
                        'user_id': current_user.id
                    },
                    'warning'
                )
                return jsonify({'error': '권한이 없습니다.'}), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_input(required_fields: list = None, optional_fields: list = None):
    """입력 검증 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if request.is_json:
                    data = request.get_json()
                    
                    # 데이터 정제
                    sanitized_data = security_manager.sanitize_input(data)
                    
                    # 필수 필드 검증
                    if required_fields:
                        missing_fields = [field for field in required_fields if field not in sanitized_data]
                        if missing_fields:
                            return jsonify({
                                'error': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'
                            }), 400
                    
                    # 허용된 필드만 추출
                    allowed_fields = (required_fields or []) + (optional_fields or [])
                    if allowed_fields:
                        filtered_data = {k: v for k, v in sanitized_data.items() if k in allowed_fields}
                        request._json = filtered_data
                    else:
                        request._json = sanitized_data
                
                return func(*args, **kwargs)
            except Exception as e:
                security_manager.log_security_event(
                    'input_validation_error',
                    {
                        'endpoint': request.path,
                        'error': str(e)
                    },
                    'error'
                )
                raise
        return wrapper
    return decorator


def rate_limit(max_requests: int = 100, window: int = 60):
    """Rate Limiting 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            
            if not security_manager._check_rate_limit(ip):
                security_manager.log_security_event(
                    'rate_limit_exceeded',
                    {
                        'ip': ip,
                        'endpoint': request.path,
                        'max_requests': max_requests,
                        'window': window
                    },
                    'warning'
                )
                return jsonify({'error': '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.'}), 429
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def prevent_xss(func):
    """XSS 방지 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 요청 데이터 정제
        if request.is_json:
            request._json = security_manager.sanitize_input(request.get_json())
        
        return func(*args, **kwargs)
    return wrapper


def log_security_event(event_type: str, severity: str = 'info'):
    """보안 이벤트 로깅 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # 성공 이벤트 로깅
                security_manager.log_security_event(
                    event_type,
                    {
                        'endpoint': request.path,
                        'method': request.method,
                        'status': 'success'
                    },
                    severity
                )
                
                return result
            except Exception as e:
                # 실패 이벤트 로깅
                security_manager.log_security_event(
                    event_type,
                    {
                        'endpoint': request.path,
                        'method': request.method,
                        'status': 'failed',
                        'error': str(e)
                    },
                    'error'
                )
                raise
        return wrapper
    return decorator


# 유틸리티 함수들
def generate_secure_token(length: int = 32) -> str:
    """보안 토큰 생성"""
    return secrets.token_urlsafe(length)


def hash_data(data: str) -> str:
    """데이터 해싱"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def validate_file_upload(filename: str, allowed_extensions: List[str], max_size: int = 10 * 1024 * 1024) -> Dict[str, Any]:
    """파일 업로드 검증"""
    if not filename:
        return {'valid': False, 'message': '파일명이 없습니다.'}
    
    # 확장자 검사
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if file_ext not in allowed_extensions:
        return {
            'valid': False, 
            'message': f'허용되지 않는 파일 형식입니다. 허용된 형식: {", ".join(allowed_extensions)}'
        }
    
    # 파일 크기 검사 (실제 파일 크기는 request.files에서 확인)
    return {'valid': True, 'message': '유효한 파일입니다.'}


def sanitize_filename(filename: str) -> str:
    """파일명 정제"""
    # 위험한 문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # 점으로 시작하거나 끝나는 파일명 방지
    filename = filename.strip('.')
    
    # 길이 제한
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1)
        filename = name[:255-len(ext)-1] + '.' + ext
    
    return filename


def check_sql_injection(text: str) -> bool:
    """SQL Injection 패턴 검사"""
    sql_patterns = [
        r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
        r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
        r'(\b(exec|execute|script)\b)',
        r'(\b(xp_|sp_)\w+)',
        r'(\b(declare|cast|convert)\b)',
        r'(\b(union|select)\b.*\bfrom\b)',
        r'(\b(insert|update)\b.*\binto\b)',
        r'(\b(delete|drop)\b.*\bfrom\b)'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def check_xss_pattern(text: str) -> bool:
    """XSS 패턴 검사"""
    xss_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<form[^>]*>.*?</form>',
        r'<input[^>]*>',
        r'<textarea[^>]*>.*?</textarea>',
        r'<select[^>]*>.*?</select>',
        r'<button[^>]*>.*?</button>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'<style[^>]*>.*?</style>',
        r'<link[^>]*>',
        r'<base[^>]*>',
        r'<bgsound[^>]*>',
        r'<marquee[^>]*>.*?</marquee>',
        r'<applet[^>]*>.*?</applet>',
        r'<frameset[^>]*>.*?</frameset>',
        r'<frame[^>]*>',
        r'<noframes[^>]*>.*?</noframes>',
        r'<noscript[^>]*>.*?</noscript>',
        r'<xmp[^>]*>.*?</xmp>',
        r'<listing[^>]*>.*?</listing>',
        r'<plaintext[^>]*>.*?</plaintext>',
        r'<isindex[^>]*>',
        r'<dir[^>]*>.*?</dir>',
        r'<menu[^>]*>.*?</menu>',
        r'<command[^>]*>',
        r'<keygen[^>]*>',
        r'<source[^>]*>',
        r'<track[^>]*>',
        r'<map[^>]*>.*?</map>',
        r'<area[^>]*>',
        r'<svg[^>]*>.*?</svg>',
        r'<math[^>]*>.*?</math>',
        r'<canvas[^>]*>.*?</canvas>',
        r'<video[^>]*>.*?</video>',
        r'<audio[^>]*>.*?</audio>',
        r'<picture[^>]*>.*?</picture>',
        r'<figure[^>]*>.*?</figure>',
        r'<figcaption[^>]*>.*?</figcaption>',
        r'<main[^>]*>.*?</main>',
        r'<section[^>]*>.*?</section>',
        r'<article[^>]*>.*?</article>',
        r'<aside[^>]*>.*?</aside>',
        r'<header[^>]*>.*?</header>',
        r'<footer[^>]*>.*?</footer>',
        r'<nav[^>]*>.*?</nav>',
        r'<dialog[^>]*>.*?</dialog>',
        r'<details[^>]*>.*?</details>',
        r'<summary[^>]*>.*?</summary>',
        r'<menu[^>]*>.*?</menu>',
        r'<menuitem[^>]*>',
        r'<meter[^>]*>.*?</meter>',
        r'<progress[^>]*>.*?</progress>',
        r'<ruby[^>]*>.*?</ruby>',
        r'<rt[^>]*>.*?</rt>',
        r'<rp[^>]*>.*?</rp>',
        r'<bdi[^>]*>.*?</bdi>',
        r'<bdo[^>]*>.*?</bdo>',
        r'<wbr[^>]*>',
        r'<time[^>]*>.*?</time>',
        r'<mark[^>]*>.*?</mark>',
        r'<small[^>]*>.*?</small>',
        r'<sub[^>]*>.*?</sub>',
        r'<sup[^>]*>.*?</sup>',
        r'<s[^>]*>.*?</s>',
        r'<u[^>]*>.*?</u>',
        r'<del[^>]*>.*?</del>',
        r'<ins[^>]*>.*?</ins>',
        r'<kbd[^>]*>.*?</kbd>',
        r'<samp[^>]*>.*?</samp>',
        r'<var[^>]*>.*?</var>',
        r'<code[^>]*>.*?</code>',
        r'<pre[^>]*>.*?</pre>',
        r'<blockquote[^>]*>.*?</blockquote>',
        r'<q[^>]*>.*?</q>',
        r'<cite[^>]*>.*?</cite>',
        r'<dfn[^>]*>.*?</dfn>',
        r'<abbr[^>]*>.*?</abbr>',
        r'<acronym[^>]*>.*?</acronym>',
        r'<address[^>]*>.*?</address>',
        r'<article[^>]*>.*?</article>',
        r'<aside[^>]*>.*?</aside>',
        r'<footer[^>]*>.*?</footer>',
        r'<header[^>]*>.*?</header>',
        r'<hgroup[^>]*>.*?</hgroup>',
        r'<nav[^>]*>.*?</nav>',
        r'<section[^>]*>.*?</section>',
        r'<dd[^>]*>.*?</dd>',
        r'<dt[^>]*>.*?</dt>',
        r'<dl[^>]*>.*?</dl>',
        r'<li[^>]*>.*?</li>',
        r'<ol[^>]*>.*?</ol>',
        r'<ul[^>]*>.*?</ul>',
        r'<caption[^>]*>.*?</caption>',
        r'<col[^>]*>',
        r'<colgroup[^>]*>.*?</colgroup>',
        r'<table[^>]*>.*?</table>',
        r'<tbody[^>]*>.*?</tbody>',
        r'<td[^>]*>.*?</td>',
        r'<tfoot[^>]*>.*?</tfoot>',
        r'<th[^>]*>.*?</th>',
        r'<thead[^>]*>.*?</thead>',
        r'<tr[^>]*>.*?</tr>'
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False
