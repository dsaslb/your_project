from models.employee_models import Employee  # pyright: ignore
from models.store_models import Store  # pyright: ignore
from models.brand_models import Brand  # pyright: ignore
from models.database import db  # pyright: ignore
from sqlalchemy import or_, func
from difflib import SequenceMatcher
from functools import wraps
import time
import logging
import re
from flask_login import login_required
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
주소 유효성 검증 및 중복 체크 API - 개선된 버전
"""


address_validation_bp = Blueprint('address_validation', __name__)

# 로깅 설정
logger = logging.getLogger(__name__)

# 캐시 (간단한 메모리 캐시)
_address_cache = {}
_cache_ttl = 300  # 5분


def cache_result(ttl=300):
    """결과 캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args,  **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items() if kwargs is not None else [])))}"

            # 캐시에서 결과 확인
            if _address_cache is not None and cache_key in _address_cache:
                cached_result, timestamp = _address_cache[cache_key]
                if time.time() - timestamp < ttl:
                    logger.debug(f"캐시된 결과 사용: {cache_key}")
                    return cached_result

            # 함수 실행
            result = func(*args, **kwargs)

            # 결과 캐싱
            if _address_cache is not None:
                _address_cache[cache_key] = (result, time.time())
            logger.debug(f"결과 캐싱: {cache_key}")

            return result
        return wrapper
    return decorator


def performance_monitor(func):
    """성능 모니터링 데코레이터"""
    @wraps(func)
    def wrapper(*args,  **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 실행 시간: {execution_time:.3f}초")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 실행 실패 (시간: {execution_time:.3f}초): {str(e)}")
            raise
    return wrapper


def calculate_address_similarity(address1,  address2):
    """
    두 주소 간의 유사도를 계산합니다.
    """
    if not address1 or not address2:
        return 0.0

    # 주소 정규화 (공백 제거, 소문자 변환)
    addr1 = re.sub(r'\s+', '', address1.lower() if address1 is not None else '')
    addr2 = re.sub(r'\s+', '', address2.lower() if address2 is not None else '')

    # SequenceMatcher를 사용한 유사도 계산
    similarity = SequenceMatcher(None, addr1, addr2).ratio()

    return similarity


def extract_address_keywords(address):
    """
    주소에서 키워드를 추출합니다.
    """
    if not address:
        return []

    # 주소를 단어로 분리
    words = re.findall(r'[가-힣0-9]+', address)

    # 의미있는 키워드만 필터링 (길이가 2 이상인 단어)
    keywords = [word for word in words if len(word) >= 2]

    return keywords


def normalize_address(address):
    """
    주소를 정규화합니다.
    """
    if not address:
        return ""

    # 공백 정규화
    normalized = re.sub(r'\s+', ' ', address.strip() if address is not None else '')

    # 특수문자 정리
    normalized = re.sub(r'[^\w\s가-힣\-()]', '', normalized)

    return normalized


@address_validation_bp.route('/api/admin/check-address-duplicate', methods=['POST'])
@login_required
@performance_monitor
def check_address_duplicate():
    """
    주소 중복 체크 API
    """
    try:
        data = request.get_json()
        address = data.get('address', '').strip() if data else ''
        exclude_id = data.get('exclude_id') if data else None
        entity_type = data.get('entity_type', 'brand') if data else 'brand'  # brand, store, employee
        similarity_threshold = data.get('similarity_threshold', 0.8) if data else 0.8

        if not address:
            return jsonify({
                'success': False,
                'error': '주소를 입력해주세요.'
            }), 400

        # 주소 정규화
        normalized_address = normalize_address(address)

        # 주소 유효성 검증
        if not is_valid_address_format(normalized_address):
            return jsonify({
                'success': False,
                'error': '올바른 주소 형식이 아닙니다.'
            }), 400

        # 중복 체크
        duplicate_result = check_duplicate_address(normalized_address,  exclude_id,  entity_type,  similarity_threshold)

        logger.info(f"주소 중복 체크 완료: {address} -> {duplicate_result['duplicate'] if duplicate_result is not None else None}")

        return jsonify({
            'success': True,
            'duplicate': duplicate_result['duplicate'] if duplicate_result is not None else None,
            'similar_addresses': duplicate_result['similar_addresses'] if duplicate_result is not None else None,
            'message': duplicate_result['message'] if duplicate_result is not None else None,
            'normalized_address': normalized_address
        })

    except Exception as e:
        logger.error(f"주소 중복 체크 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'주소 중복 체크 중 오류가 발생했습니다: {str(e)}'
        }), 500


def is_valid_address_format(address):
    """
    주소 형식의 유효성을 검증합니다.
    """
    if not address or len(address) < 5:
        return False

    # 기본적인 주소 패턴 검증
    # 한글, 숫자, 공백, 특수문자(일부)만 허용
    address_pattern = re.compile(r'^[가-힣0-9\s\-()]+$')

    if not address_pattern.match(address):
        return False

    # 최소 2개의 한글 단어가 포함되어야 함
    korean_words = re.findall(r'[가-힣]+', address)
    if len(korean_words) < 2:
        return False

    return True


@cache_result(ttl=60)  # 1분 캐시
def check_duplicate_address(address, exclude_id=None, entity_type='brand', similarity_threshold=0.8):
    """
    주소 중복을 체크합니다.
    """
    similar_addresses = []

    # 엔티티 타입에 따른 모델 선택
    if entity_type == 'brand':
        model = Brand
        query = Brand.query
    elif entity_type == 'store':
        model = Store
        query = Store.query
    elif entity_type == 'employee':
        model = Employee
        query = Employee.query
    else:
        return {
            'duplicate': False,
            'similar_addresses': [],
            'message': '지원하지 않는 엔티티 타입입니다.'
        }

    # exclude_id가 있는 경우 해당 레코드 제외
    if exclude_id:
        query = query.filter(model.id != exclude_id)

    # 주소가 있는 레코드만 조회 (성능 최적화)
    all_addresses = query.with_entities(model.address).filter(model.address.isnot(None)).all()

    if all_addresses is not None:
        for addr_record in all_addresses:
            existing_address = addr_record[0] if addr_record is not None else None
            if existing_address:
                similarity = calculate_address_similarity(address, existing_address)

                if similarity >= similarity_threshold:
                    similar_addresses.append({
                        'address': existing_address,
                        'similarity': round(similarity * 100, 1)
                    })

    # 유사도 순으로 정렬
    similar_addresses.sort(key=lambda x: x['similarity'], reverse=True)

    # 중복 여부 판단
    is_duplicate = len(similar_addresses) > 0

    if is_duplicate:
        message = f"유사한 주소가 {len(similar_addresses)}개 발견되었습니다."
    else:
        message = "중복된 주소가 없습니다."

    return {
        'duplicate': is_duplicate,
        'similar_addresses': similar_addresses,
        'message': message
    }


@address_validation_bp.route('/api/admin/validate-address', methods=['POST'])
@login_required
@performance_monitor
def validate_address():
    """
    주소 유효성 검증 API
    """
    try:
        data = request.get_json()
        address = data.get('address', '').strip() if data else ''

        if not address:
            return jsonify({
                'success': False,
                'valid': False,
                'error': '주소를 입력해주세요.'
            }), 400

        # 주소 정규화
        normalized_address = normalize_address(address)

        # 주소 형식 검증
        is_valid = is_valid_address_format(normalized_address)

        # 추가 검증 (길이, 특수문자 등)
        validation_details = get_validation_details(normalized_address)

        if is_valid:
            return jsonify({
                'success': True,
                'valid': True,
                'message': '유효한 주소입니다.',
                'normalized_address': normalized_address,
                'validation_details': validation_details
            })
        else:
            return jsonify({
                'success': True,
                'valid': False,
                'error': '올바른 주소 형식이 아닙니다.',
                'validation_details': validation_details
            })

    except Exception as e:
        logger.error(f"주소 검증 오류: {str(e)}")
        return jsonify({
            'success': False,
            'valid': False,
            'error': f'주소 검증 중 오류가 발생했습니다: {str(e)}'
        }), 500


def get_validation_details(address):
    """
    주소 검증 상세 정보를 반환합니다.
    """
    details = {
        'length': len(address),
        'korean_words': len(re.findall(r'[가-힣]+', address)),
        'numbers': len(re.findall(r'[0-9]+', address)),
        'has_special_chars': bool(re.search(r'[^\w\s가-힣]', address)),
        'word_count': len(address.split())
    }

    return details


@address_validation_bp.route('/api/admin/geocode-address', methods=['POST'])
@login_required
@performance_monitor
@cache_result(ttl=3600)  # 1시간 캐시 (좌표는 자주 변경되지 않음)
def geocode_address():
    """
    주소를 위도/경도로 변환하는 API (카카오 Geocoding API 사용)
    """
    try:
        data = request.get_json()
        address = data.get('address', '').strip() if data else ''

        if not address:
            return jsonify({
                'success': False,
                'error': '주소를 입력해주세요.'
            }), 400

        # 주소 정규화
        normalized_address = normalize_address(address)

        # 카카오 Geocoding API 호출
        coordinates = get_coordinates_from_kakao(normalized_address)

        if coordinates:
            logger.info(f"주소 좌표 변환 성공: {address} -> ({coordinates['latitude'] if coordinates is not None else None}, {coordinates['longitude'] if coordinates is not None else None})")
            return jsonify({
                'success': True,
                'latitude': coordinates['latitude'] if coordinates is not None else None,
                'longitude': coordinates['longitude'] if coordinates is not None else None,
                'formatted_address': coordinates.get('formatted_address', normalized_address) if coordinates else None,
                'normalized_address': normalized_address
            })
        else:
            logger.warning(f"주소 좌표 변환 실패: {address}")
            return jsonify({
                'success': False,
                'error': '주소를 좌표로 변환할 수 없습니다.'
            }), 404

    except Exception as e:
        logger.error(f"좌표 변환 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'좌표 변환 중 오류가 발생했습니다: {str(e)}'
        }), 500


def get_coordinates_from_kakao(address):
    """
    카카오 Geocoding API를 사용하여 주소를 좌표로 변환합니다.
    """
    import requests
    import os

    # 카카오 API 키 (환경변수에서 가져오거나 설정에서 가져옴)
    kakao_api_key = os.getenv('KAKAO_API_KEY', 'YOUR_KAKAO_API_KEY')

    if kakao_api_key == 'YOUR_KAKAO_API_KEY':
        # API 키가 설정되지 않은 경우
        logger.warning("카카오 API 키가 설정되지 않았습니다.")
        return None

    try:
        url = 'https://dapi.kakao.com/v2/local/search/address.json'
        headers = {
            'Authorization': f'KakaoAK {kakao_api_key}'
        }
        params = {
            'query': address
        }

        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data.get('documents') and len(data['documents']) > 0:
                document = data['documents'][0]

                return {
                    'latitude': float(document['y']) if document and 'y' in document else None,
                    'longitude': float(document['x']) if document and 'x' in document else None,
                    'formatted_address': document.get('address_name', address) if document else None
                }
            else:
                logger.warning(f"카카오 API에서 주소를 찾을 수 없음: {address}")
        else:
            logger.error(f"카카오 API 오류 (상태 코드: {response.status_code}): {response.text}")

        return None

    except requests.exceptions.Timeout:
        logger.error("카카오 API 요청 시간 초과")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"카카오 API 요청 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"카카오 Geocoding API 오류: {e}")
        return None


@address_validation_bp.route('/api/admin/address-suggestions', methods=['POST'])
@login_required
@performance_monitor
@cache_result(ttl=300)  # 5분 캐시
def get_address_suggestions():
    """
    주소 자동완성 제안 API
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip() if data else ''
        limit = data.get('limit', 10) if data else 10
        entity_type = data.get('entity_type', 'all') if data else 'all'  # all, brand, store, employee

        if not query or len(query) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            })

        # 쿼리 정규화
        normalized_query = normalize_address(query)

        # 기존 주소에서 유사한 주소들을 찾아 제안
        suggestions = get_similar_addresses(normalized_query,  limit,  entity_type)

        logger.debug(f"주소 제안 조회: {query} -> {len(suggestions)}개 제안")

        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'query': normalized_query
        })

    except Exception as e:
        logger.error(f"주소 제안 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'주소 제안 중 오류가 발생했습니다: {str(e)}'
        }), 500


def get_similar_addresses(query, limit=10, entity_type='all'):
    """
    쿼리와 유사한 기존 주소들을 찾습니다.
    """
    suggestions = []

    # 모든 엔티티에서 주소 수집
    all_addresses = set()

    if entity_type in ['all', 'brand']:
        brand_addresses = Brand.query.with_entities(Brand.address).filter(Brand.address.isnot(None)).all()
        all_addresses.update([addr[0] for addr in brand_addresses if addr and addr[0]])

    if entity_type in ['all', 'store']:
        store_addresses = Store.query.with_entities(Store.address).filter(Store.address.isnot(None)).all()
        all_addresses.update([addr[0] for addr in store_addresses if addr and addr[0]])

    if entity_type in ['all', 'employee']:
        employee_addresses = Employee.query.with_entities(Employee.address).filter(Employee.address.isnot(None)).all()
        all_addresses.update([addr[0] for addr in employee_addresses if addr and addr[0]])

    # 유사도 계산 및 정렬
    address_scores = []
    if all_addresses is not None:
        for address in all_addresses:
            similarity = calculate_address_similarity(query,  address)
            if similarity > 0.3:  # 30% 이상 유사한 주소만 제안
                address_scores.append({
                    'address': address,
                    'similarity': similarity
                })

    # 유사도 순으로 정렬
    address_scores.sort(key=lambda x: x['similarity'], reverse=True)

    # 상위 결과 반환
    suggestions = [item['address'] for item in address_scores[:limit] if item and 'address' in item]

    return suggestions


@address_validation_bp.route('/api/admin/address-statistics', methods=['GET'])
@login_required
def get_address_statistics():
    """
    주소 통계 정보 API
    """
    try:
        # 브랜드 주소 통계
        brand_count = Brand.query.filter(Brand.address.isnot(None)).count()
        brand_with_coords = Brand.query.filter(
            Brand.address.isnot(None),
            Brand.latitude.isnot(None),
            Brand.longitude.isnot(None)
        ).count()

        # 매장 주소 통계
        store_count = Store.query.filter(Store.address.isnot(None)).count()
        store_with_coords = Store.query.filter(
            Store.address.isnot(None),
            Store.latitude.isnot(None),
            Store.longitude.isnot(None)
        ).count()

        # 직원 주소 통계
        employee_count = Employee.query.filter(Employee.address.isnot(None)).count()
        employee_with_coords = Employee.query.filter(
            Employee.address.isnot(None),
            Employee.latitude.isnot(None),
            Employee.longitude.isnot(None)
        ).count()

        return jsonify({
            'success': True,
            'statistics': {
                'brands': {
                    'total_with_address': brand_count,
                    'with_coordinates': brand_with_coords,
                    'coordinate_percentage': round((brand_with_coords / brand_count * 100) if brand_count > 0 else 0, 1)
                },
                'stores': {
                    'total_with_address': store_count,
                    'with_coordinates': store_with_coords,
                    'coordinate_percentage': round((store_with_coords / store_count * 100) if store_count > 0 else 0, 1)
                },
                'employees': {
                    'total_with_address': employee_count,
                    'with_coordinates': employee_with_coords,
                    'coordinate_percentage': round((employee_with_coords / employee_count * 100) if employee_count > 0 else 0, 1)
                }
            }
        })

    except Exception as e:
        logger.error(f"주소 통계 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'주소 통계 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@address_validation_bp.route('/api/admin/clear-address-cache', methods=['POST'])
@login_required
def clear_address_cache():
    """
    주소 캐시 초기화 API
    """
    try:
        global _address_cache
        cache_size = len(_address_cache)
        _address_cache.clear()

        logger.info(f"주소 캐시 초기화 완료: {cache_size}개 항목 제거")

        return jsonify({
            'success': True,
            'message': f'캐시가 초기화되었습니다. ({cache_size}개 항목 제거)'
        })

    except Exception as e:
        logger.error(f"캐시 초기화 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'캐시 초기화 중 오류가 발생했습니다: {str(e)}'
        }), 500

# 에러 핸들러


@address_validation_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '요청한 리소스를 찾을 수 없습니다.'
    }), 404


@address_validation_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"내부 서버 오류: {str(error)}")
    return jsonify({
        'success': False,
        'error': '내부 서버 오류가 발생했습니다.'
    }), 500
