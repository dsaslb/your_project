import aiohttp
import asyncio
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
import hashlib
import hmac

@dataclass
class APIEndpoint:
    """API 엔드포인트 정보"""
    name: str
    url: str
    method: str = 'GET'
    headers: Dict = None
    timeout: int = 30
    retry_count: int = 3
    rate_limit: int = 100  # 분당 요청 수
    last_request: float = 0

class ExternalAPIManager:
    """외부 API 연동 관리자"""
    
    def __init__(self):
        self.endpoints = {}
        self.api_keys = {}
        self.request_history = []
        self.rate_limit_windows = {}
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 기본 API 설정
        self._setup_default_apis()
    
    def _setup_default_apis(self):
        """기본 API 엔드포인트 설정"""
        # 날씨 API
        self.add_endpoint(
            'weather',
            'https://api.openweathermap.org/data/2.5/weather',
            'GET',
            {'Content-Type': 'application/json'}
        )
        
        # 지도 API
        self.add_endpoint(
            'maps',
            'https://maps.googleapis.com/maps/api/geocode/json',
            'GET',
            {'Content-Type': 'application/json'}
        )
        
        # 결제 API (예시)
        self.add_endpoint(
            'payment',
            'https://api.payment-gateway.com/v1/transactions',
            'POST',
            {'Content-Type': 'application/json', 'Authorization': 'Bearer {api_key}'}
        )
        
        # 배달 API (예시)
        self.add_endpoint(
            'delivery',
            'https://api.delivery-service.com/v1/orders',
            'POST',
            {'Content-Type': 'application/json', 'X-API-Key': '{api_key}'}
        )
    
    def add_endpoint(self, name: str, url: str, method: str = 'GET', 
                    headers: Dict = None, timeout: int = 30, retry_count: int = 3):
        """API 엔드포인트 추가"""
        self.endpoints[name] = APIEndpoint(
            name=name,
            url=url,
            method=method,
            headers=headers or {},
            timeout=timeout,
            retry_count=retry_count
        )
        self.logger.info(f"API 엔드포인트 추가됨: {name}")
    
    def set_api_key(self, service: str, api_key: str):
        """API 키 설정"""
        self.api_keys[service] = api_key
        self.logger.info(f"API 키 설정됨: {service}")
    
    def _check_rate_limit(self, endpoint_name: str) -> bool:
        """요청 제한 확인"""
        current_time = time.time()
        window_key = f"{endpoint_name}_{int(current_time / 60)}"
        
        if window_key not in self.rate_limit_windows:
            self.rate_limit_windows[window_key] = 0
        
        endpoint = self.endpoints.get(endpoint_name)
        if not endpoint:
            return False
        
        if self.rate_limit_windows[window_key] >= endpoint.rate_limit:
            return False
        
        self.rate_limit_windows[window_key] += 1
        return True
    
    def _prepare_headers(self, endpoint: APIEndpoint, service: str = None) -> Dict:
        """헤더 준비"""
        headers = endpoint.headers.copy()
        
        # API 키 치환
        if service and service in self.api_keys:
            for key, value in headers.items():
                if '{api_key}' in str(value):
                    headers[key] = value.replace('{api_key}', self.api_keys[service])
        
        return headers
    
    async def async_request(self, endpoint_name: str, params: Dict = None, 
                          data: Dict = None, service: str = None) -> Dict:
        """비동기 API 요청"""
        endpoint = self.endpoints.get(endpoint_name)
        if not endpoint:
            return {"error": f"엔드포인트를 찾을 수 없습니다: {endpoint_name}"}
        
        if not self._check_rate_limit(endpoint_name):
            return {"error": "요청 제한에 도달했습니다."}
        
        headers = self._prepare_headers(endpoint, service)
        
        try:
            async with aiohttp.ClientSession() as session:
                for attempt in range(endpoint.retry_count):
                    try:
                        if endpoint.method == 'GET':
                            async with session.get(
                                endpoint.url, 
                                params=params, 
                                headers=headers, 
                                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
                            ) as response:
                                result = await response.json()
                        else:
                            async with session.post(
                                endpoint.url, 
                                json=data, 
                                headers=headers, 
                                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
                            ) as response:
                                result = await response.json()
                        
                        # 성공 시 기록
                        self._log_request(endpoint_name, True, response.status)
                        return {"success": True, "data": result, "status": response.status}
                        
                    except asyncio.TimeoutError:
                        self.logger.warning(f"API 요청 타임아웃: {endpoint_name} (시도 {attempt + 1})")
                        if attempt == endpoint.retry_count - 1:
                            return {"error": "요청 타임아웃"}
                    except Exception as e:
                        self.logger.error(f"API 요청 실패: {endpoint_name} - {str(e)}")
                        if attempt == endpoint.retry_count - 1:
                            return {"error": f"요청 실패: {str(e)}"}
                
        except Exception as e:
            self._log_request(endpoint_name, False, 0, str(e))
            return {"error": f"연결 실패: {str(e)}"}
    
    def sync_request(self, endpoint_name: str, params: Dict = None, 
                    data: Dict = None, service: str = None) -> Dict:
        """동기 API 요청"""
        endpoint = self.endpoints.get(endpoint_name)
        if not endpoint:
            return {"error": f"엔드포인트를 찾을 수 없습니다: {endpoint_name}"}
        
        if not self._check_rate_limit(endpoint_name):
            return {"error": "요청 제한에 도달했습니다."}
        
        headers = self._prepare_headers(endpoint, service)
        
        try:
            for attempt in range(endpoint.retry_count):
                try:
                    if endpoint.method == 'GET':
                        response = requests.get(
                            endpoint.url, 
                            params=params, 
                            headers=headers, 
                            timeout=endpoint.timeout
                        )
                    else:
                        response = requests.post(
                            endpoint.url, 
                            json=data, 
                            headers=headers, 
                            timeout=endpoint.timeout
                        )
                    
                    result = response.json()
                    self._log_request(endpoint_name, True, response.status_code)
                    return {"success": True, "data": result, "status": response.status_code}
                    
                except requests.Timeout:
                    self.logger.warning(f"API 요청 타임아웃: {endpoint_name} (시도 {attempt + 1})")
                    if attempt == endpoint.retry_count - 1:
                        return {"error": "요청 타임아웃"}
                except Exception as e:
                    self.logger.error(f"API 요청 실패: {endpoint_name} - {str(e)}")
                    if attempt == endpoint.retry_count - 1:
                        return {"error": f"요청 실패: {str(e)}"}
        
        except Exception as e:
            self._log_request(endpoint_name, False, 0, str(e))
            return {"error": f"연결 실패: {str(e)}"}
    
    def get_weather(self, city: str, country_code: str = 'KR') -> Dict:
        """날씨 정보 조회"""
        if 'weather' not in self.api_keys:
            return {"error": "날씨 API 키가 설정되지 않았습니다."}
        
        params = {
            'q': f"{city},{country_code}",
            'appid': self.api_keys['weather'],
            'units': 'metric',
            'lang': 'kr'
        }
        
        return self.sync_request('weather', params=params)
    
    def get_location_info(self, address: str) -> Dict:
        """주소 정보 조회"""
        if 'maps' not in self.api_keys:
            return {"error": "지도 API 키가 설정되지 않았습니다."}
        
        params = {
            'address': address,
            'key': self.api_keys['maps']
        }
        
        return self.sync_request('maps', params=params)
    
    def process_payment(self, amount: float, currency: str = 'KRW', 
                       payment_method: str = 'card') -> Dict:
        """결제 처리"""
        if 'payment' not in self.api_keys:
            return {"error": "결제 API 키가 설정되지 않았습니다."}
        
        data = {
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.sync_request('payment', data=data, service='payment')
    
    def create_delivery_order(self, order_data: Dict) -> Dict:
        """배달 주문 생성"""
        if 'delivery' not in self.api_keys:
            return {"error": "배달 API 키가 설정되지 않았습니다."}
        
        return self.sync_request('delivery', data=order_data, service='delivery')
    
    def _log_request(self, endpoint_name: str, success: bool, status_code: int, 
                    error_message: str = None):
        """요청 로그 기록"""
        log_entry = {
            'timestamp': datetime.utcnow(),
            'endpoint': endpoint_name,
            'success': success,
            'status_code': status_code,
            'error_message': error_message
        }
        
        self.request_history.append(log_entry)
        
        # 로그 크기 제한 (최근 1000개만 유지)
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
    
    def get_request_history(self, limit: int = 100) -> List[Dict]:
        """요청 히스토리 조회"""
        return self.request_history[-limit:]
    
    def get_api_status(self) -> Dict:
        """API 상태 정보"""
        status = {
            'total_endpoints': len(self.endpoints),
            'configured_apis': list(self.api_keys.keys()),
            'recent_requests': len(self.request_history),
            'rate_limits': {}
        }
        
        for endpoint_name, endpoint in self.endpoints.items():
            current_window = f"{endpoint_name}_{int(time.time() / 60)}"
            status['rate_limits'][endpoint_name] = {
                'current_requests': self.rate_limit_windows.get(current_window, 0),
                'max_requests': endpoint.rate_limit
            }
        
        return status
    
    def cleanup_old_windows(self):
        """오래된 윈도우 정리"""
        current_time = time.time()
        current_minute = int(current_time / 60)
        
        windows_to_remove = []
        for window_key in self.rate_limit_windows.keys():
            window_minute = int(window_key.split('_')[-1])
            if window_minute < current_minute - 1:  # 1분 이상 지난 윈도우
                windows_to_remove.append(window_key)
        
        for window_key in windows_to_remove:
            del self.rate_limit_windows[window_key]

# 전역 외부 API 매니저 인스턴스
external_api_manager = ExternalAPIManager() 