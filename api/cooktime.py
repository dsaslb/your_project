"""
조리 예상시간 혁신 기능용 API
- 실시간 조리 예상시간, 권한 분기, 통계/상태 반환 등 구현
"""
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from models import db, User, Branch, ActionLog
from utils.decorators import admin_required, manager_required

logger = logging.getLogger(__name__)
cooktime_api = Blueprint('cooktime_api', __name__)

# 조리 예상시간 모델 (임시로 딕셔너리로 구현, 실제로는 데이터베이스 모델로 구현)
cooktime_records = {}
menu_cooktimes = {
    'hamburger': {
        'name': '햄버거',
        'base_time': 8,  # 기본 조리시간 (분)
        'category': 'main',
        'difficulty': 'medium',
        'ingredients': ['패티', '빵', '야채', '소스'],
        'steps': [
            {'step': 1, 'description': '패티 굽기', 'time': 5},
            {'step': 2, 'description': '빵 토스트', 'time': 2},
            {'step': 3, 'description': '야채 준비', 'time': 1},
            {'step': 4, 'description': '조립', 'time': 1}
        ]
    },
    'pizza': {
        'name': '피자',
        'base_time': 15,
        'category': 'main',
        'difficulty': 'high',
        'ingredients': ['도우', '토마토소스', '치즈', '토핑'],
        'steps': [
            {'step': 1, 'description': '도우 펴기', 'time': 3},
            {'step': 2, 'description': '소스 바르기', 'time': 1},
            {'step': 3, 'description': '치즈 올리기', 'time': 1},
            {'step': 4, 'description': '토핑 올리기', 'time': 2},
            {'step': 5, 'description': '오븐 굽기', 'time': 8}
        ]
    },
    'fries': {
        'name': '감자튀김',
        'base_time': 6,
        'category': 'side',
        'difficulty': 'low',
        'ingredients': ['감자', '튀김옷'],
        'steps': [
            {'step': 1, 'description': '감자 손질', 'time': 2},
            {'step': 2, 'description': '튀김옷 입히기', 'time': 1},
            {'step': 3, 'description': '튀기기', 'time': 3}
        ]
    },
    'chicken': {
        'name': '치킨',
        'base_time': 20,
        'category': 'main',
        'difficulty': 'high',
        'ingredients': ['닭고기', '튀김옷', '양념'],
        'steps': [
            {'step': 1, 'description': '닭고기 손질', 'time': 5},
            {'step': 2, 'description': '양념 발라두기', 'time': 3},
            {'step': 3, 'description': '튀김옷 입히기', 'time': 2},
            {'step': 4, 'description': '튀기기', 'time': 10}
        ]
    }
}

def log_cooktime_action(action: str, details: Dict[str, Any]):
    """조리시간 액션 로깅"""
    try:
        log = ActionLog(  # type: ignore
            user_id=current_user.id,
            action=f"cooktime_{action}",
            message=f"조리시간 {action}: {details.get('menu_name', 'N/A')}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"조리시간 액션 로깅 실패: {e}")

@cooktime_api.route('/api/cooktime/menus', methods=['GET'])
@login_required
def get_menu_cooktimes():
    """메뉴별 조리시간 정보 조회"""
    try:
        # 권한에 따른 메뉴 필터링
        if current_user.role in ['admin', 'brand_admin']:
            available_menus = list(menu_cooktimes.keys())
        elif current_user.role == 'store_admin':
            available_menus = ['hamburger', 'pizza', 'fries', 'chicken']
        else:
            available_menus = ['hamburger', 'fries']  # 일반 직원은 기본 메뉴만
        
        menus = {}
        for menu_id in available_menus:
            menus[menu_id] = menu_cooktimes[menu_id]
        
        return jsonify({
            'success': True,
            'menus': menus
        })
    except Exception as e:
        logger.error(f"메뉴 조리시간 조회 실패: {e}")
        return jsonify({'error': '메뉴 조리시간 조회에 실패했습니다.'}), 500

@cooktime_api.route('/api/cooktime/menus/<menu_id>', methods=['GET'])
@login_required
def get_menu_cooktime_detail(menu_id: str):
    """메뉴별 조리시간 상세 조회"""
    try:
        if menu_id not in menu_cooktimes:
            return jsonify({'error': '메뉴를 찾을 수 없습니다.'}), 404
        
        # 권한 확인
        if current_user.role not in ['admin', 'brand_admin'] and menu_id == 'chicken':
            return jsonify({'error': '접근 권한이 없습니다.'}), 403
        
        return jsonify({
            'success': True,
            'menu': menu_cooktimes[menu_id]
        })
    except Exception as e:
        logger.error(f"메뉴 조리시간 상세 조회 실패: {e}")
        return jsonify({'error': '메뉴 조리시간 상세 조회에 실패했습니다.'}), 500

@cooktime_api.route('/api/cooktime/calculate', methods=['POST'])
@login_required
def calculate_cooktime():
    """조리 예상시간 계산"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        menu_id = data.get('menu_id')
        quantity = data.get('quantity', 1)
        customizations = data.get('customizations', [])
        chef_experience = data.get('chef_experience', 'medium')  # low, medium, high
        
        if not menu_id or menu_id not in menu_cooktimes:
            return jsonify({'error': '유효하지 않은 메뉴입니다.'}), 400
        
        menu = menu_cooktimes[menu_id]
        base_time = float(menu['base_time'])  # 명시적으로 float로 변환
        
        # 수량에 따른 시간 계산 (수량이 많을수록 효율성 증가)
        if quantity == 1:
            quantity_multiplier = 1.0
        elif quantity <= 3:
            quantity_multiplier = 0.9
        elif quantity <= 5:
            quantity_multiplier = 0.8
        else:
            quantity_multiplier = 0.7
        
        # 요리사 경험에 따른 시간 조정
        experience_multiplier = {
            'low': 1.3,      # 초보자: 30% 더 오래 걸림
            'medium': 1.0,   # 중급자: 기본 시간
            'high': 0.8      # 고급자: 20% 빨라짐
        }.get(chef_experience, 1.0)
        
        # 커스터마이징에 따른 추가 시간
        customization_time = 0
        for customization in customizations:
            if customization.get('type') == 'extra_topping':
                customization_time += 1
            elif customization.get('type') == 'special_cooking':
                customization_time += 2
            elif customization.get('type') == 'dietary_restriction':
                customization_time += 1.5
        
        # 최종 조리시간 계산
        total_time = (base_time * quantity_multiplier * experience_multiplier) + customization_time
        
        # 조리시간 기록
        record_id = f"cooktime_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"
        cooktime_record = {
            'id': record_id,
            'menu_id': menu_id,
            'menu_name': menu['name'],
            'quantity': quantity,
            'customizations': customizations,
            'chef_experience': chef_experience,
            'calculated_time': round(total_time, 1),
            'base_time': base_time,
            'quantity_multiplier': quantity_multiplier,
            'experience_multiplier': experience_multiplier,
            'customization_time': customization_time,
            'created_by': current_user.id,
            'created_at': datetime.now().isoformat()
        }
        
        cooktime_records[record_id] = cooktime_record
        
        # 액션 로깅
        log_cooktime_action('calculate', {
            'menu_name': menu['name'],
            'calculated_time': total_time,
            'quantity': quantity
        })
        
        return jsonify({
            'success': True,
            'cooktime': {
                'menu_name': menu['name'],
                'quantity': quantity,
                'estimated_time': round(total_time, 1),
                'unit': '분',
                'breakdown': {
                    'base_time': base_time,
                    'quantity_adjustment': quantity_multiplier,
                    'experience_adjustment': experience_multiplier,
                    'customization_time': customization_time
                }
            }
        })
        
    except Exception as e:
        logger.error(f"조리시간 계산 실패: {e}")
        return jsonify({'error': '조리시간 계산에 실패했습니다.'}), 500

@cooktime_api.route('/api/cooktime/actual', methods=['POST'])
@login_required
def record_actual_cooktime():
    """실제 조리시간 기록"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        menu_id = data.get('menu_id')
        actual_time = data.get('actual_time')
        order_id = data.get('order_id')
        notes = data.get('notes', '')
        
        if not menu_id or menu_id not in menu_cooktimes:
            return jsonify({'error': '유효하지 않은 메뉴입니다.'}), 400
        
        if not actual_time or actual_time <= 0:
            return jsonify({'error': '유효하지 않은 조리시간입니다.'}), 400
        
        menu = menu_cooktimes[menu_id]
        base_time = float(menu['base_time'])  # 명시적으로 float로 변환
        
        # 시간 차이 계산
        time_difference = actual_time - base_time
        efficiency_ratio = base_time / actual_time if actual_time > 0 else 0
        
        # 실제 조리시간 기록
        record_id = f"actual_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"
        actual_record = {
            'id': record_id,
            'menu_id': menu_id,
            'menu_name': menu['name'],
            'base_time': base_time,
            'actual_time': actual_time,
            'time_difference': round(time_difference, 1),
            'efficiency_ratio': round(efficiency_ratio, 2),
            'order_id': order_id,
            'notes': notes,
            'recorded_by': current_user.id,
            'recorded_at': datetime.now().isoformat()
        }
        
        cooktime_records[record_id] = actual_record
        
        # 액션 로깅
        log_cooktime_action('record_actual', {
            'menu_name': menu['name'],
            'actual_time': actual_time,
            'efficiency_ratio': efficiency_ratio
        })
        
        return jsonify({
            'success': True,
            'record': actual_record
        }), 201
        
    except Exception as e:
        logger.error(f"실제 조리시간 기록 실패: {e}")
        return jsonify({'error': '실제 조리시간 기록에 실패했습니다.'}), 500

@cooktime_api.route('/api/cooktime/records', methods=['GET'])
@login_required
def get_cooktime_records():
    """조리시간 기록 목록 조회"""
    try:
        # 권한에 따른 필터링
        if current_user.role in ['admin', 'brand_admin']:
            user_records = list(cooktime_records.values())
        else:
            # 일반 사용자는 본인이 기록한 것만 조회
            user_records = [
                record for record in cooktime_records.values()
                if record.get('created_by') == current_user.id or 
                   record.get('recorded_by') == current_user.id
            ]
        
        # 필터링 옵션
        menu_filter = request.args.get('menu_id')
        date_filter = request.args.get('date')
        record_type = request.args.get('type')  # calculated, actual
        
        if menu_filter:
            user_records = [r for r in user_records if r.get('menu_id') == menu_filter]
        
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            user_records = [
                r for r in user_records 
                if datetime.fromisoformat(r.get('created_at', r.get('recorded_at', ''))).date() == filter_date
            ]
        
        if record_type:
            if record_type == 'calculated':
                user_records = [r for r in user_records if 'calculated_time' in r]
            elif record_type == 'actual':
                user_records = [r for r in user_records if 'actual_time' in r]
        
        # 정렬 (최신순)
        user_records.sort(key=lambda x: x.get('created_at', x.get('recorded_at', '')), reverse=True)
        
        # 페이지네이션
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = user_records[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'records': paginated_records,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(user_records),
                'pages': (len(user_records) + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"조리시간 기록 목록 조회 실패: {e}")
        return jsonify({'error': '조리시간 기록 목록 조회에 실패했습니다.'}), 500

@cooktime_api.route('/api/cooktime/statistics', methods=['GET'])
@login_required
@manager_required
def get_cooktime_statistics():
    """조리시간 통계"""
    try:
        # 권한에 따른 데이터 필터링
        if current_user.role in ['admin', 'brand_admin']:
            user_records = list(cooktime_records.values())
        else:
            # 매장 관리자는 해당 매장의 기록만
            user_records = [
                record for record in cooktime_records.values()
                if record.get('branch_id') == current_user.branch_id
            ]
        
        if not user_records:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_records': 0,
                    'average_efficiency': 0,
                    'menu_performance': {},
                    'recent_trend': []
                }
            })
        
        # 실제 조리시간 기록만 필터링
        actual_records = [r for r in user_records if 'actual_time' in r]
        
        if not actual_records:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_records': len(user_records),
                    'average_efficiency': 0,
                    'menu_performance': {},
                    'recent_trend': []
                }
            })
        
        # 평균 효율성 계산
        total_efficiency = sum(r.get('efficiency_ratio', 0) for r in actual_records)
        average_efficiency = total_efficiency / len(actual_records)
        
        # 메뉴별 성능 분석
        menu_performance = {}
        for record in actual_records:
            menu_id = record.get('menu_id')
            if menu_id not in menu_performance:
                menu_performance[menu_id] = {
                    'menu_name': record.get('menu_name'),
                    'total_orders': 0,
                    'average_time': 0,
                    'average_efficiency': 0,
                    'times': []
                }
            
            menu_performance[menu_id]['total_orders'] += 1
            menu_performance[menu_id]['times'].append(record.get('actual_time', 0))
        
        # 메뉴별 평균 계산
        for menu_id, performance in menu_performance.items():
            times = performance['times']
            performance['average_time'] = sum(times) / len(times)
            
            # 해당 메뉴의 효율성 평균 계산
            menu_efficiencies = [
                r.get('efficiency_ratio', 0) for r in actual_records 
                if r.get('menu_id') == menu_id
            ]
            if menu_efficiencies:
                performance['average_efficiency'] = sum(menu_efficiencies) / len(menu_efficiencies)
        
        # 최근 트렌드 (최근 7일)
        recent_date = datetime.now() - timedelta(days=7)
        recent_records = [
            r for r in actual_records 
            if datetime.fromisoformat(r.get('recorded_at', '')) >= recent_date
        ]
        
        recent_trend = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            day_records = [
                r for r in recent_records
                if datetime.fromisoformat(r.get('recorded_at', '')).strftime('%Y-%m-%d') == date_str
            ]
            
            if day_records:
                day_efficiency = sum(r.get('efficiency_ratio', 0) for r in day_records) / len(day_records)
                recent_trend.append({
                    'date': date_str,
                    'orders': len(day_records),
                    'average_efficiency': round(day_efficiency, 2)
                })
            else:
                recent_trend.append({
                    'date': date_str,
                    'orders': 0,
                    'average_efficiency': 0
                })
        
        recent_trend.reverse()  # 날짜순으로 정렬
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_records': len(actual_records),
                'average_efficiency': round(average_efficiency, 2),
                'menu_performance': menu_performance,
                'recent_trend': recent_trend
            }
        })
        
    except Exception as e:
        logger.error(f"조리시간 통계 조회 실패: {e}")
        return jsonify({'error': '통계 조회에 실패했습니다.'}), 500

@cooktime_api.route('/api/cooktime/optimization', methods=['GET'])
@login_required
@manager_required
def get_cooktime_optimization():
    """조리시간 최적화 권장사항"""
    try:
        # 최근 30일 데이터 분석
        recent_date = datetime.now() - timedelta(days=30)
        recent_records = [
            r for r in cooktime_records.values()
            if 'actual_time' in r and 
            datetime.fromisoformat(r.get('recorded_at', '')) >= recent_date
        ]
        
        if not recent_records:
            return jsonify({
                'success': True,
                'optimization': {
                    'recommendations': [],
                    'slow_menus': [],
                    'efficiency_issues': []
                }
            })
        
        # 느린 메뉴 식별 (기본 시간보다 20% 이상 오래 걸리는 메뉴)
        slow_menus = []
        for record in recent_records:
            base_time = record.get('base_time', 0)
            actual_time = record.get('actual_time', 0)
            if actual_time > base_time * 1.2:  # 20% 이상 오래 걸림
                slow_menus.append({
                    'menu_name': record.get('menu_name'),
                    'base_time': base_time,
                    'actual_time': actual_time,
                    'difference': round(actual_time - base_time, 1)
                })
        
        # 효율성 문제 분석
        efficiency_issues = []
        menu_efficiencies = {}
        
        for record in recent_records:
            menu_id = record.get('menu_id')
            efficiency = record.get('efficiency_ratio', 0)
            
            if menu_id not in menu_efficiencies:
                menu_efficiencies[menu_id] = []
            menu_efficiencies[menu_id].append(efficiency)
        
        # 평균 효율성이 0.8 미만인 메뉴 식별
        for menu_id, efficiencies in menu_efficiencies.items():
            avg_efficiency = sum(efficiencies) / len(efficiencies)
            if avg_efficiency < 0.8:
                menu_name = next((r.get('menu_name') for r in recent_records if r.get('menu_id') == menu_id), 'Unknown')
                efficiency_issues.append({
                    'menu_name': menu_name,
                    'average_efficiency': round(avg_efficiency, 2),
                    'recommendation': '조리 과정 최적화가 필요합니다.'
                })
        
        # 권장사항 생성
        recommendations = []
        
        if slow_menus:
            recommendations.append({
                'type': 'slow_cooking',
                'title': '조리시간 단축 필요',
                'description': f'{len(slow_menus)}개 메뉴의 조리시간이 기준보다 오래 걸리고 있습니다.',
                'priority': 'high'
            })
        
        if efficiency_issues:
            recommendations.append({
                'type': 'efficiency_improvement',
                'title': '효율성 개선 필요',
                'description': f'{len(efficiency_issues)}개 메뉴의 효율성이 낮습니다.',
                'priority': 'medium'
            })
        
        if not slow_menus and not efficiency_issues:
            recommendations.append({
                'type': 'good_performance',
                'title': '양호한 성능',
                'description': '조리시간이 기준에 맞게 잘 지켜지고 있습니다.',
                'priority': 'low'
            })
        
        return jsonify({
            'success': True,
            'optimization': {
                'recommendations': recommendations,
                'slow_menus': slow_menus[:5],  # 상위 5개만
                'efficiency_issues': efficiency_issues
            }
        })
        
    except Exception as e:
        logger.error(f"조리시간 최적화 분석 실패: {e}")
        return jsonify({'error': '최적화 분석에 실패했습니다.'}), 500

@cooktime_api.route('/api/cooktime/records/<record_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_cooktime_record(record_id: str):
    """조리시간 기록 삭제 (관리자만)"""
    try:
        if record_id not in cooktime_records:
            return jsonify({'error': '기록을 찾을 수 없습니다.'}), 404
        
        # 기록 삭제
        deleted_record = cooktime_records.pop(record_id)
        
        # 액션 로깅
        log_cooktime_action('delete', {'record_id': record_id})
        
        return jsonify({
            'success': True,
            'message': '조리시간 기록이 삭제되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"조리시간 기록 삭제 실패: {e}")
        return jsonify({'error': '조리시간 기록 삭제에 실패했습니다.'}), 500 