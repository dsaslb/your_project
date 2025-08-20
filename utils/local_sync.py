#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로컬 데이터 동기화 유틸리티
프론트엔드에서 업로드 시 동기화 처리를 담당합니다.
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class LocalSyncManager:
    """로컬 데이터 동기화 관리자"""
    
    def __init__(self, api_base_url: str = None):
        self.api_base_url = api_base_url or "http://localhost:5000"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def sync_schedule_data(self, schedule_data: Dict[str, Any], auth_token: str = None) -> Dict[str, Any]:
        """
        스케줄 데이터 동기화
        
        Args:
            schedule_data: 동기화할 스케줄 데이터
            auth_token: 인증 토큰 (선택사항)
        
        Returns:
            동기화 결과
        """
        try:
            if auth_token:
                self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
            
            # 스케줄 데이터 검증
            if not self._validate_schedule_data(schedule_data):
                return {
                    'success': False,
                    'error': '스케줄 데이터 형식이 올바르지 않습니다.'
                }
            
            # 서버에 스케줄 데이터 전송
            response = self.session.post(
                f"{self.api_base_url}/api/schedule/sync",
                json=schedule_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("스케줄 데이터 동기화 성공")
                return {
                    'success': True,
                    'message': '스케줄 데이터가 성공적으로 동기화되었습니다.',
                    'data': result.get('data', {})
                }
            else:
                logger.error(f"스케줄 데이터 동기화 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'서버 오류: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return {
                'success': False,
                'error': f'네트워크 오류: {str(e)}'
            }
        except Exception as e:
            logger.error(f"동기화 중 오류 발생: {e}")
            return {
                'success': False,
                'error': f'동기화 오류: {str(e)}'
            }
    
    def sync_attendance_data(self, attendance_data: Dict[str, Any], auth_token: str = None) -> Dict[str, Any]:
        """
        출퇴근 데이터 동기화
        
        Args:
            attendance_data: 동기화할 출퇴근 데이터
            auth_token: 인증 토큰 (선택사항)
        
        Returns:
            동기화 결과
        """
        try:
            if auth_token:
                self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
            
            # 출퇴근 데이터 검증
            if not self._validate_attendance_data(attendance_data):
                return {
                    'success': False,
                    'error': '출퇴근 데이터 형식이 올바르지 않습니다.'
                }
            
            # 서버에 출퇴근 데이터 전송
            response = self.session.post(
                f"{self.api_base_url}/api/attendance/sync",
                json=attendance_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("출퇴근 데이터 동기화 성공")
                return {
                    'success': True,
                    'message': '출퇴근 데이터가 성공적으로 동기화되었습니다.',
                    'data': result.get('data', {})
                }
            else:
                logger.error(f"출퇴근 데이터 동기화 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'서버 오류: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return {
                'success': False,
                'error': f'네트워크 오류: {str(e)}'
            }
        except Exception as e:
            logger.error(f"동기화 중 오류 발생: {e}")
            return {
                'success': False,
                'error': f'동기화 오류: {str(e)}'
            }
    
    def sync_analysis_report(self, report_data: Dict[str, Any], auth_token: str = None) -> Dict[str, Any]:
        """
        분석 리포트 동기화
        
        Args:
            report_data: 동기화할 분석 리포트 데이터
            auth_token: 인증 토큰 (선택사항)
        
        Returns:
            동기화 결과
        """
        try:
            if auth_token:
                self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
            
            # 리포트 데이터 검증
            if not self._validate_report_data(report_data):
                return {
                    'success': False,
                    'error': '리포트 데이터 형식이 올바르지 않습니다.'
                }
            
            # 서버에 리포트 데이터 전송
            response = self.session.post(
                f"{self.api_base_url}/api/reports/sync",
                json=report_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("분석 리포트 동기화 성공")
                return {
                    'success': True,
                    'message': '분석 리포트가 성공적으로 동기화되었습니다.',
                    'data': result.get('data', {})
                }
            else:
                logger.error(f"분석 리포트 동기화 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'서버 오류: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return {
                'success': False,
                'error': f'네트워크 오류: {str(e)}'
            }
        except Exception as e:
            logger.error(f"동기화 중 오류 발생: {e}")
            return {
                'success': False,
                'error': f'동기화 오류: {str(e)}'
            }
    
    def batch_sync(self, sync_data: Dict[str, Any], auth_token: str = None) -> Dict[str, Any]:
        """
        배치 동기화 (여러 데이터를 한 번에 동기화)
        
        Args:
            sync_data: 동기화할 데이터 (스케줄, 출퇴근, 리포트 포함)
            auth_token: 인증 토큰 (선택사항)
        
        Returns:
            동기화 결과
        """
        try:
            if auth_token:
                self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
            
            # 배치 데이터 검증
            if not self._validate_batch_data(sync_data):
                return {
                    'success': False,
                    'error': '배치 데이터 형식이 올바르지 않습니다.'
                }
            
            # 서버에 배치 데이터 전송
            response = self.session.post(
                f"{self.api_base_url}/api/batch/sync",
                json=sync_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("배치 동기화 성공")
                return {
                    'success': True,
                    'message': '모든 데이터가 성공적으로 동기화되었습니다.',
                    'data': result.get('data', {}),
                    'summary': result.get('summary', {})
                }
            else:
                logger.error(f"배치 동기화 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'서버 오류: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return {
                'success': False,
                'error': f'네트워크 오류: {str(e)}'
            }
        except Exception as e:
            logger.error(f"동기화 중 오류 발생: {e}")
            return {
                'success': False,
                'error': f'동기화 오류: {str(e)}'
            }
    
    def _validate_schedule_data(self, data: Dict[str, Any]) -> bool:
        """스케줄 데이터 검증"""
        required_fields = ['employees', 'period']
        
        if not all(field in data for field in required_fields):
            return False
        
        if not isinstance(data.get('employees'), list):
            return False
        
        if not isinstance(data.get('period'), dict):
            return False
        
        return True
    
    def _validate_attendance_data(self, data: Dict[str, Any]) -> bool:
        """출퇴근 데이터 검증"""
        required_fields = ['employee_id', 'date', 'check_in', 'check_out']
        
        if not all(field in data for field in required_fields):
            return False
        
        return True
    
    def _validate_report_data(self, data: Dict[str, Any]) -> bool:
        """리포트 데이터 검증"""
        required_fields = ['analysis_date', 'summary', 'recommendations']
        
        if not all(field in data for field in required_fields):
            return False
        
        return True
    
    def _validate_batch_data(self, data: Dict[str, Any]) -> bool:
        """배치 데이터 검증"""
        if not isinstance(data, dict):
            return False
        
        # 최소한 하나의 데이터 타입이 있어야 함
        data_types = ['schedules', 'attendance', 'reports']
        if not any(data_type in data for data_type in data_types):
            return False
        
        return True
    
    def get_sync_status(self, sync_id: str, auth_token: str = None) -> Dict[str, Any]:
        """
        동기화 상태 조회
        
        Args:
            sync_id: 동기화 ID
            auth_token: 인증 토큰 (선택사항)
        
        Returns:
            동기화 상태
        """
        try:
            if auth_token:
                self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
            
            response = self.session.get(
                f"{self.api_base_url}/api/sync/status/{sync_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'상태 조회 실패: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"상태 조회 중 오류: {e}")
            return {
                'success': False,
                'error': f'상태 조회 오류: {str(e)}'
            }

# 사용 예시
if __name__ == "__main__":
    # 동기화 매니저 초기화
    sync_manager = LocalSyncManager("http://localhost:5000")
    
    # 샘플 스케줄 데이터
    sample_schedule_data = {
        "employees": [
            {
                "id": 1,
                "name": "김철수",
                "work_hours": 8.0,
                "attendance_rate": 95.0
            }
        ],
        "period": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
    }
    
    # 동기화 실행
    result = sync_manager.sync_schedule_data(sample_schedule_data)
    print("동기화 결과:", json.dumps(result, indent=2, ensure_ascii=False))
