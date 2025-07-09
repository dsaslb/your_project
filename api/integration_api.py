from flask import Blueprint, jsonify, request, current_app
from functools import wraps
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

integration_bp = Blueprint('integration', __name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 외부 시스템 설정 (실제 환경에서는 환경변수로 관리)
EXTERNAL_SYSTEMS = {
    'erp': {
        'base_url': 'https://erp.example.com/api',
        'api_key': 'erp_api_key_here',
        'timeout': 30
    },
    'pos': {
        'base_url': 'https://pos.example.com/api', 
        'api_key': 'pos_api_key_here',
        'timeout': 15
    },
    'accounting': {
        'base_url': 'https://accounting.example.com/api',
        'api_key': 'accounting_api_key_here', 
        'timeout': 30
    }
}

def external_api_call(system: str, endpoint: str, method='GET', data=None):
    """외부 시스템 API 호출"""
    if system not in EXTERNAL_SYSTEMS:
        raise ValueError(f"지원하지 않는 시스템: {system}")
    
    config = EXTERNAL_SYSTEMS[system]
    url = f"{config['base_url']}/{endpoint}"
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=config['timeout'])
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=config['timeout'])
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=config['timeout'])
        else:
            raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"외부 API 호출 실패 - {system}: {e}")
        raise

@integration_bp.route('/api/integration/erp/sync', methods=['POST'])
def sync_with_erp():
    """ERP 시스템과 데이터 동기화"""
    try:
        data = request.get_json()
        sync_type = data.get('type', 'all')
        
        if sync_type == 'inventory':
            # 재고 데이터 동기화
            inventory_data = get_local_inventory_data()
            result = external_api_call('erp', 'inventory/sync', 'POST', inventory_data)
            
        elif sync_type == 'orders':
            # 주문 데이터 동기화
            orders_data = get_local_orders_data()
            result = external_api_call('erp', 'orders/sync', 'POST', orders_data)
            
        elif sync_type == 'all':
            # 전체 데이터 동기화
            all_data = {
                'inventory': get_local_inventory_data(),
                'orders': get_local_orders_data(),
                'staff': get_local_staff_data(),
                'timestamp': datetime.now().isoformat()
            }
            result = external_api_call('erp', 'sync/all', 'POST', all_data)
        
        logger.info(f"ERP 동기화 완료: {sync_type}")
        return jsonify({
            'message': 'ERP 동기화 완료',
            'sync_type': sync_type,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"ERP 동기화 실패: {e}")
        return jsonify({'error': 'ERP 동기화 실패', 'details': str(e)}), 500

@integration_bp.route('/api/integration/pos/transactions', methods=['GET'])
def get_pos_transactions():
    """POS 시스템에서 거래 내역 조회"""
    try:
        # 날짜 범위 파라미터
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        # POS API 호출
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'limit': request.args.get('limit', 100)
        }
        
        transactions = external_api_call('pos', 'transactions', 'GET', params)
        
        return jsonify({
            'transactions': transactions,
            'period': {'start_date': start_date, 'end_date': end_date}
        })
        
    except Exception as e:
        logger.error(f"POS 거래 내역 조회 실패: {e}")
        return jsonify({'error': '거래 내역 조회 실패', 'details': str(e)}), 500

@integration_bp.route('/api/integration/accounting/reports', methods=['GET'])
def get_accounting_reports():
    """회계 시스템에서 보고서 조회"""
    try:
        report_type = request.args.get('type', 'monthly')
        year = request.args.get('year', datetime.now().year)
        month = request.args.get('month', datetime.now().month)
        
        # 회계 API 호출
        params = {
            'report_type': report_type,
            'year': year,
            'month': month
        }
        
        reports = external_api_call('accounting', 'reports', 'GET', params)
        
        return jsonify({
            'reports': reports,
            'period': {'year': year, 'month': month, 'type': report_type}
        })
        
    except Exception as e:
        logger.error(f"회계 보고서 조회 실패: {e}")
        return jsonify({'error': '보고서 조회 실패', 'details': str(e)}), 500

@integration_bp.route('/api/integration/sync/all', methods=['POST'])
def sync_all_systems():
    """모든 외부 시스템과 동기화"""
    try:
        sync_results = {}
        
        # ERP 동기화
        try:
            erp_result = external_api_call('erp', 'sync/all', 'POST', get_all_local_data())
            sync_results['erp'] = {'status': 'success', 'data': erp_result}
        except Exception as e:
            sync_results['erp'] = {'status': 'error', 'error': str(e)}
        
        # POS 동기화
        try:
            pos_result = external_api_call('pos', 'sync', 'POST', get_pos_sync_data())
            sync_results['pos'] = {'status': 'success', 'data': pos_result}
        except Exception as e:
            sync_results['pos'] = {'status': 'error', 'error': str(e)}
        
        # 회계 동기화
        try:
            accounting_result = external_api_call('accounting', 'sync', 'POST', get_accounting_sync_data())
            sync_results['accounting'] = {'status': 'success', 'data': accounting_result}
        except Exception as e:
            sync_results['accounting'] = {'status': 'error', 'error': str(e)}
        
        # 동기화 결과 요약
        successful_syncs = sum(1 for result in sync_results.values() if result['status'] == 'success')
        total_syncs = len(sync_results)
        
        return jsonify({
            'message': f'동기화 완료 ({successful_syncs}/{total_syncs})',
            'results': sync_results,
            'summary': {
                'total_systems': total_syncs,
                'successful': successful_syncs,
                'failed': total_syncs - successful_syncs
            }
        })
        
    except Exception as e:
        logger.error(f"전체 시스템 동기화 실패: {e}")
        return jsonify({'error': '동기화 실패', 'details': str(e)}), 500

@integration_bp.route('/api/integration/status', methods=['GET'])
def get_integration_status():
    """통합 시스템 상태 확인"""
    try:
        status = {}
        
        for system_name, config in EXTERNAL_SYSTEMS.items():
            try:
                # 각 시스템의 상태 확인
                health_check = external_api_call(system_name, 'health', 'GET')
                status[system_name] = {
                    'status': 'connected',
                    'response_time': health_check.get('response_time', 'unknown'),
                    'last_sync': health_check.get('last_sync', 'unknown')
                }
            except Exception as e:
                status[system_name] = {
                    'status': 'disconnected',
                    'error': str(e)
                }
        
        return jsonify({
            'integration_status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"통합 상태 확인 실패: {e}")
        return jsonify({'error': '상태 확인 실패', 'details': str(e)}), 500

# 헬퍼 함수들 (실제 환경에서는 데이터베이스에서 조회)
def get_local_inventory_data():
    """로컬 재고 데이터 조회"""
    return {
        'items': [
            {'id': 1, 'name': '상품A', 'quantity': 100, 'price': 10000},
            {'id': 2, 'name': '상품B', 'quantity': 50, 'price': 15000}
        ],
        'last_updated': datetime.now().isoformat()
    }

def get_local_orders_data():
    """로컬 주문 데이터 조회"""
    return {
        'orders': [
            {'id': 1, 'customer': '고객A', 'total': 25000, 'status': 'completed'},
            {'id': 2, 'customer': '고객B', 'total': 30000, 'status': 'pending'}
        ],
        'last_updated': datetime.now().isoformat()
    }

def get_local_staff_data():
    """로컬 직원 데이터 조회"""
    return {
        'staff': [
            {'id': 1, 'name': '직원A', 'role': 'manager', 'status': 'active'},
            {'id': 2, 'name': '직원B', 'role': 'staff', 'status': 'active'}
        ],
        'last_updated': datetime.now().isoformat()
    }

def get_all_local_data():
    """모든 로컬 데이터 조회"""
    return {
        'inventory': get_local_inventory_data(),
        'orders': get_local_orders_data(),
        'staff': get_local_staff_data(),
        'sync_timestamp': datetime.now().isoformat()
    }

def get_pos_sync_data():
    """POS 동기화 데이터"""
    return {
        'transactions': get_local_orders_data()['orders'],
        'sync_timestamp': datetime.now().isoformat()
    }

def get_accounting_sync_data():
    """회계 동기화 데이터"""
    return {
        'revenue': sum(order['total'] for order in get_local_orders_data()['orders']),
        'transactions': get_local_orders_data()['orders'],
        'sync_timestamp': datetime.now().isoformat()
    } 