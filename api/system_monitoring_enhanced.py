# -*- coding: utf-8 -*-
"""
향상된 시스템/서버 운영·보안 모니터링 API
시스템 상태/자원(메모리, CPU, 네트워크) 실시간 수집
보안 정책/로그/접근제어/샌드박스 현황
장애/이슈/실시간 이벤트/알림 자동 감지·기록
Prometheus/ELK/Sentry 등 연동 가능 구조
"""

import logging
import psutil
import platform
import os
import json
import time
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, func, desc
import threading
import queue
import requests
from collections import defaultdict

from extensions import db, csrf
from models_main import (
    SystemLog, Notification, ActionLog, User, 
    PluginActivation, PluginTestResult, IndustryAdmin
)

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
system_monitoring_bp = Blueprint('system_monitoring_enhanced', __name__)

class SystemMonitor:
    """시스템 모니터링 클래스"""
    
    def __init__(self):
        self.metrics_queue = queue.Queue()
        self.alert_thresholds = {
            'cpu_usage': 80.0,  # CPU 사용률 임계값
            'memory_usage': 85.0,  # 메모리 사용률 임계값
            'disk_usage': 90.0,  # 디스크 사용률 임계값
            'response_time': 2.0,  # 응답 시간 임계값 (초)
            'error_rate': 5.0,  # 에러율 임계값 (%)
            'active_connections': 1000,  # 활성 연결 수 임계값
        }
        self.monitoring_active = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """모니터링 시작"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("시스템 모니터링이 시작되었습니다.")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("시스템 모니터링이 중지되었습니다.")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 시스템 메트릭 수집
                metrics = self._collect_system_metrics()
                
                # 임계값 체크 및 알림 생성
                self._check_thresholds(metrics)
                
                # 메트릭 저장
                self._save_metrics(metrics)
                
                # 30초 대기
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 정보
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # 메모리 정보
            memory = psutil.virtual_memory()
            
            # 디스크 정보
            disk = psutil.disk_usage('/')
            
            # 네트워크 정보
            network = psutil.net_io_counters()
            
            # 시스템 정보
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # 프로세스 정보
            process_count = len(psutil.pids())
            
            # 로드 평균 (Linux/Mac)
            load_avg = None
            if hasattr(psutil, 'getloadavg'):
                try:
                    load_avg = psutil.getloadavg()
                except:
                    pass
            
            metrics = {
                'timestamp': datetime.utcnow(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None,
                    'load_average': load_avg
                },
                'memory': {
                    'total_bytes': memory.total,
                    'available_bytes': memory.available,
                    'used_bytes': memory.used,
                    'usage_percent': memory.percent,
                    'free_bytes': memory.free
                },
                'disk': {
                    'total_bytes': disk.total,
                    'used_bytes': disk.used,
                    'free_bytes': disk.free,
                    'usage_percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'system': {
                    'boot_time': boot_time,
                    'uptime_seconds': uptime.total_seconds(),
                    'process_count': process_count,
                    'platform': platform.platform(),
                    'python_version': platform.python_version()
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return None
    
    def _check_thresholds(self, metrics):
        """임계값 체크 및 알림 생성"""
        if not metrics:
            return
        
        alerts = []
        
        # CPU 사용률 체크
        if metrics['cpu']['usage_percent'] > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f"CPU 사용률이 높습니다: {metrics['cpu']['usage_percent']:.1f}%",
                'value': metrics['cpu']['usage_percent'],
                'threshold': self.alert_thresholds['cpu_usage']
            })
        
        # 메모리 사용률 체크
        if metrics['memory']['usage_percent'] > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': f"메모리 사용률이 높습니다: {metrics['memory']['usage_percent']:.1f}%",
                'value': metrics['memory']['usage_percent'],
                'threshold': self.alert_thresholds['memory_usage']
            })
        
        # 디스크 사용률 체크
        if metrics['disk']['usage_percent'] > self.alert_thresholds['disk_usage']:
            alerts.append({
                'type': 'disk_high',
                'severity': 'critical',
                'message': f"디스크 사용률이 높습니다: {metrics['disk']['usage_percent']:.1f}%",
                'value': metrics['disk']['usage_percent'],
                'threshold': self.alert_thresholds['disk_usage']
            })
        
        # 알림 생성
        for alert in alerts:
            self._create_alert(alert)
    
    def _create_alert(self, alert_data):
        """알림 생성"""
        try:
            # 시스템 로그에 기록
            system_log = SystemLog(
                level=alert_data['severity'],
                message=alert_data['message'],
                category='system_monitoring',
                metadata=json.dumps(alert_data),
                created_at=datetime.utcnow()
            )
            db.session.add(system_log)
            
            # 알림 생성
            notification = Notification(
                title=f"시스템 알림: {alert_data['type']}",
                content=alert_data['message'],
                type='system_alert',
                severity=alert_data['severity'],
                metadata=json.dumps(alert_data),
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            
            db.session.commit()
            
            logger.warning(f"시스템 알림 생성: {alert_data['message']}")
            
        except Exception as e:
            logger.error(f"알림 생성 실패: {e}")
            db.session.rollback()
    
    def _save_metrics(self, metrics):
        """메트릭 저장"""
        try:
            # 메트릭을 JSON으로 직렬화하여 시스템 로그에 저장
            system_log = SystemLog(
                level='info',
                message='System metrics collected',
                category='system_metrics',
                metadata=json.dumps(metrics, default=str),
                created_at=datetime.utcnow()
            )
            db.session.add(system_log)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"메트릭 저장 실패: {e}")
            db.session.rollback()

class SecurityMonitor:
    """보안 모니터링 클래스"""
    
    def __init__(self):
        self.security_events = []
        self.suspicious_ips = set()
        self.failed_login_attempts = defaultdict(int)
        self.rate_limit_threshold = 10  # 1분당 최대 시도 횟수
    
    def log_security_event(self, event_type, details, severity='info', ip_address=None):
        """보안 이벤트 로깅"""
        try:
            event = {
                'type': event_type,
                'details': details,
                'severity': severity,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow(),
                'user_id': current_user.id if current_user.is_authenticated else None
            }
            
            # 시스템 로그에 기록
            system_log = SystemLog(
                level=severity,
                message=f"Security event: {event_type}",
                category='security',
                metadata=json.dumps(event, default=str),
                created_at=datetime.utcnow()
            )
            db.session.add(system_log)
            
            # 의심스러운 IP 체크
            if ip_address:
                self._check_suspicious_ip(ip_address, event_type)
            
            # 보안 알림 생성 (심각한 이벤트의 경우)
            if severity in ['warning', 'error', 'critical']:
                self._create_security_alert(event)
            
            db.session.commit()
            
            logger.info(f"보안 이벤트 로깅: {event_type} - {details}")
            
        except Exception as e:
            logger.error(f"보안 이벤트 로깅 실패: {e}")
            db.session.rollback()
    
    def _check_suspicious_ip(self, ip_address, event_type):
        """의심스러운 IP 체크"""
        # 로그인 실패 횟수 체크
        if event_type == 'login_failed':
            self.failed_login_attempts[ip_address] += 1
            
            if self.failed_login_attempts[ip_address] >= self.rate_limit_threshold:
                self.suspicious_ips.add(ip_address)
                self.log_security_event(
                    'suspicious_ip_detected',
                    f'IP {ip_address}에서 과도한 로그인 시도 감지',
                    'warning',
                    ip_address
                )
    
    def _create_security_alert(self, event):
        """보안 알림 생성"""
        try:
            notification = Notification(
                title=f"보안 알림: {event['type']}",
                content=event['details'],
                type='security_alert',
                severity=event['severity'],
                metadata=json.dumps(event, default=str),
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            
        except Exception as e:
            logger.error(f"보안 알림 생성 실패: {e}")

# 모니터링 인스턴스
system_monitor = SystemMonitor()
security_monitor = SecurityMonitor()

@system_monitoring_bp.route('/api/system/metrics', methods=['GET'])
@login_required
def get_system_metrics():
    """시스템 메트릭 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        # 실시간 메트릭 수집
        metrics = system_monitor._collect_system_metrics()
        
        if not metrics:
            return jsonify({'error': '시스템 메트릭 수집에 실패했습니다.'}), 500
        
        # 응답 데이터 구성
        response_data = {
            'timestamp': metrics['timestamp'].isoformat(),
            'cpu': {
                'usage_percent': round(metrics['cpu']['usage_percent'], 2),
                'count': metrics['cpu']['count'],
                'frequency_mhz': round(metrics['cpu']['frequency_mhz'], 2) if metrics['cpu']['frequency_mhz'] else None,
                'load_average': metrics['cpu']['load_average']
            },
            'memory': {
                'total_gb': round(metrics['memory']['total_bytes'] / (1024**3), 2),
                'used_gb': round(metrics['memory']['used_bytes'] / (1024**3), 2),
                'available_gb': round(metrics['memory']['available_bytes'] / (1024**3), 2),
                'usage_percent': round(metrics['memory']['usage_percent'], 2)
            },
            'disk': {
                'total_gb': round(metrics['disk']['total_bytes'] / (1024**3), 2),
                'used_gb': round(metrics['disk']['used_bytes'] / (1024**3), 2),
                'free_gb': round(metrics['disk']['free_bytes'] / (1024**3), 2),
                'usage_percent': round(metrics['disk']['usage_percent'], 2)
            },
            'network': {
                'bytes_sent_mb': round(metrics['network']['bytes_sent'] / (1024**2), 2),
                'bytes_recv_mb': round(metrics['network']['bytes_recv'] / (1024**2), 2),
                'packets_sent': metrics['network']['packets_sent'],
                'packets_recv': metrics['network']['packets_recv']
            },
            'system': {
                'uptime_hours': round(metrics['system']['uptime_seconds'] / 3600, 2),
                'process_count': metrics['system']['process_count'],
                'platform': metrics['system']['platform'],
                'python_version': metrics['system']['python_version']
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"시스템 메트릭 조회 실패: {e}")
        return jsonify({'error': '시스템 메트릭 조회에 실패했습니다.'}), 500

@system_monitoring_bp.route('/api/system/status', methods=['GET'])
@login_required
def get_system_status():
    """시스템 상태 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        # 시스템 메트릭 수집
        metrics = system_monitor._collect_system_metrics()
        
        if not metrics:
            return jsonify({'error': '시스템 메트릭 수집에 실패했습니다.'}), 500
        
        # 상태 판단
        status = 'healthy'
        issues = []
        
        # CPU 체크
        if metrics['cpu']['usage_percent'] > 80:
            status = 'warning'
            issues.append(f"CPU 사용률 높음: {metrics['cpu']['usage_percent']:.1f}%")
        
        # 메모리 체크
        if metrics['memory']['usage_percent'] > 85:
            status = 'warning'
            issues.append(f"메모리 사용률 높음: {metrics['memory']['usage_percent']:.1f}%")
        
        # 디스크 체크
        if metrics['disk']['usage_percent'] > 90:
            status = 'critical'
            issues.append(f"디스크 사용률 높음: {metrics['disk']['usage_percent']:.1f}%")
        
        # 최근 에러 로그 체크
        recent_errors = SystemLog.query.filter(
            and_(
                SystemLog.level.in_(['error', 'critical']),
                SystemLog.created_at >= datetime.utcnow() - timedelta(hours=1)
            )
        ).count()
        
        if recent_errors > 10:
            status = 'warning'
            issues.append(f"최근 1시간 내 에러 로그: {recent_errors}개")
        
        # 응답 데이터 구성
        response_data = {
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'issues': issues,
            'metrics': {
                'cpu_usage': round(metrics['cpu']['usage_percent'], 2),
                'memory_usage': round(metrics['memory']['usage_percent'], 2),
                'disk_usage': round(metrics['disk']['usage_percent'], 2),
                'uptime_hours': round(metrics['system']['uptime_seconds'] / 3600, 2),
                'process_count': metrics['system']['process_count']
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"시스템 상태 조회 실패: {e}")
        return jsonify({'error': '시스템 상태 조회에 실패했습니다.'}), 500

@system_monitoring_bp.route('/api/system/alerts', methods=['GET'])
@login_required
def get_system_alerts():
    """시스템 알림 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        severity = request.args.get('severity')
        category = request.args.get('category')
        
        # 기본 쿼리
        query = SystemLog.query.filter(
            SystemLog.level.in_(['warning', 'error', 'critical'])
        )
        
        # 필터링
        if severity:
            query = query.filter(SystemLog.level == severity)
        if category:
            query = query.filter(SystemLog.category == category)
        
        # 정렬 (최신순)
        query = query.order_by(SystemLog.created_at.desc())
        
        # 페이징
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 결과 데이터 구성
        alerts = []
        for alert in pagination.items:
            alert_data = {
                'id': alert.id,
                'level': alert.level,
                'message': alert.message,
                'category': alert.category,
                'metadata': json.loads(alert.metadata) if alert.metadata else None,
                'created_at': alert.created_at.isoformat()
            }
            alerts.append(alert_data)
        
        return jsonify({
            'alerts': alerts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"시스템 알림 조회 실패: {e}")
        return jsonify({'error': '시스템 알림 조회에 실패했습니다.'}), 500

@system_monitoring_bp.route('/api/system/security/logs', methods=['GET'])
@login_required
def get_security_logs():
    """보안 로그 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        
        # 기본 쿼리
        query = SystemLog.query.filter(SystemLog.category == 'security')
        
        # 필터링
        if event_type:
            query = query.filter(SystemLog.message.contains(f"Security event: {event_type}"))
        if severity:
            query = query.filter(SystemLog.level == severity)
        
        # 정렬 (최신순)
        query = query.order_by(SystemLog.created_at.desc())
        
        # 페이징
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 결과 데이터 구성
        security_logs = []
        for log in pagination.items:
            log_data = {
                'id': log.id,
                'level': log.level,
                'message': log.message,
                'metadata': json.loads(log.metadata) if log.metadata else None,
                'created_at': log.created_at.isoformat()
            }
            security_logs.append(log_data)
        
        return jsonify({
            'security_logs': security_logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"보안 로그 조회 실패: {e}")
        return jsonify({'error': '보안 로그 조회에 실패했습니다.'}), 500

@system_monitoring_bp.route('/api/system/monitoring/start', methods=['POST'])
@login_required
@csrf.exempt
def start_system_monitoring():
    """시스템 모니터링 시작"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        system_monitor.start_monitoring()
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='start_system_monitoring',
            message='시스템 모니터링 시작',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        db.session.commit()
        
        return jsonify({'message': '시스템 모니터링이 시작되었습니다.'})
        
    except Exception as e:
        logger.error(f"시스템 모니터링 시작 실패: {e}")
        return jsonify({'error': '시스템 모니터링 시작에 실패했습니다.'}), 500

@system_monitoring_bp.route('/api/system/monitoring/stop', methods=['POST'])
@login_required
@csrf.exempt
def stop_system_monitoring():
    """시스템 모니터링 중지"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        system_monitor.stop_monitoring()
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='stop_system_monitoring',
            message='시스템 모니터링 중지',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        db.session.commit()
        
        return jsonify({'message': '시스템 모니터링이 중지되었습니다.'})
        
    except Exception as e:
        logger.error(f"시스템 모니터링 중지 실패: {e}")
        return jsonify({'error': '시스템 모니터링 중지에 실패했습니다.'}), 500

@system_monitoring_bp.route('/api/system/security/event', methods=['POST'])
@login_required
@csrf.exempt
def log_security_event():
    """보안 이벤트 로깅"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        data = request.get_json()
        event_type = data.get('event_type')
        details = data.get('details')
        severity = data.get('severity', 'info')
        ip_address = data.get('ip_address', request.remote_addr)
        
        if not event_type or not details:
            return jsonify({'error': '이벤트 타입과 상세 정보는 필수입니다.'}), 400
        
        security_monitor.log_security_event(event_type, details, severity, ip_address)
        
        return jsonify({'message': '보안 이벤트가 로깅되었습니다.'})
        
    except Exception as e:
        logger.error(f"보안 이벤트 로깅 실패: {e}")
        return jsonify({'error': '보안 이벤트 로깅에 실패했습니다.'}), 500

@system_monitoring_bp.route('/api/system/stats', methods=['GET'])
@login_required
def get_system_stats():
    """시스템 통계 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'monitoring'):
            return jsonify({'error': '시스템 모니터링 권한이 없습니다.'}), 403
        
        # 최근 24시간 통계
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        
        # 로그 통계
        total_logs = SystemLog.query.count()
        error_logs = SystemLog.query.filter(SystemLog.level.in_(['error', 'critical'])).count()
        security_logs = SystemLog.query.filter(SystemLog.category == 'security').count()
        
        # 최근 24시간 로그
        recent_logs = SystemLog.query.filter(SystemLog.created_at >= yesterday).count()
        recent_errors = SystemLog.query.filter(
            and_(
                SystemLog.level.in_(['error', 'critical']),
                SystemLog.created_at >= yesterday
            )
        ).count()
        
        # 사용자 활동 통계
        active_users = User.query.filter(User.last_login >= yesterday).count()
        total_users = User.query.count()
        
        # 플러그인 통계
        active_plugins = PluginActivation.query.filter_by(is_active=True).count()
        total_plugins = PluginActivation.query.count()
        
        # 업종별 관리자 통계
        pending_admins = IndustryAdmin.query.filter_by(status='pending').count()
        approved_admins = IndustryAdmin.query.filter_by(status='approved').count()
        
        stats = {
            'logs': {
                'total': total_logs,
                'errors': error_logs,
                'security': security_logs,
                'recent_24h': recent_logs,
                'recent_errors_24h': recent_errors
            },
            'users': {
                'total': total_users,
                'active_24h': active_users,
                'active_percentage': round((active_users / total_users * 100), 2) if total_users > 0 else 0
            },
            'plugins': {
                'total': total_plugins,
                'active': active_plugins,
                'active_percentage': round((active_plugins / total_plugins * 100), 2) if total_plugins > 0 else 0
            },
            'industry_admins': {
                'pending': pending_admins,
                'approved': approved_admins
            },
            'system_health': {
                'status': 'healthy',  # 기본값, 실제로는 메트릭 기반으로 계산
                'last_check': now.isoformat()
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"시스템 통계 조회 실패: {e}")
        return jsonify({'error': '시스템 통계 조회에 실패했습니다.'}), 500 