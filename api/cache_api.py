from flask import Blueprint, request, jsonify
from cache.cache_manager import CacheManager, CacheConfig, CacheType
import os
from datetime import datetime

# 캐시 관리자 초기화
cache_config = CacheConfig(
    data_dir="data/cache",
    max_memory_size=100 * 1024 * 1024,  # 100MB
    max_disk_size=1024 * 1024 * 1024,   # 1GB
    default_ttl=3600,
    cleanup_interval=300,
    enable_compression=True,
    enable_encryption=False
)

cache_manager = CacheManager(cache_config)

# Blueprint 생성
cache_bp = Blueprint('cache', __name__, url_prefix='/api/cache')

@cache_bp.route('/health', methods=['GET'])
def health_check():
    """캐시 시스템 상태 확인"""
    try:
        stats = cache_manager.get_stats()
        return jsonify({
            'status': 'success',
            'message': '캐시 시스템이 정상적으로 작동합니다',
            'data': {
                'total_items': stats.total_items,
                'memory_items': stats.memory_items,
                'disk_items': stats.disk_items,
                'hit_rate': round(stats.hit_rate, 2)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 시스템 상태 확인 실패: {str(e)}'
        }), 500

@cache_bp.route('/stats', methods=['GET'])
def get_cache_stats():
    """캐시 통계 조회"""
    try:
        stats = cache_manager.get_stats()
        return jsonify({
            'status': 'success',
            'data': {
                'total_items': stats.total_items,
                'memory_items': stats.memory_items,
                'disk_items': stats.disk_items,
                'total_size': stats.total_size,
                'memory_size': stats.memory_size,
                'disk_size': stats.disk_size,
                'hit_count': stats.hit_count,
                'miss_count': stats.miss_count,
                'hit_rate': round(stats.hit_rate, 2),
                'eviction_count': stats.eviction_count
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 통계 조회 실패: {str(e)}'
        }), 500

@cache_bp.route('/set', methods=['POST'])
def set_cache():
    """캐시 항목 설정"""
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        ttl = data.get('ttl')
        cache_type = data.get('cache_type', 'memory')
        tags = data.get('tags', [])
        metadata = data.get('metadata', {})
        
        if not key or value is None:
            return jsonify({
                'status': 'error',
                'message': '키와 값은 필수입니다'
            }), 400
        
        try:
            cache_type_enum = CacheType(cache_type)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': '유효하지 않은 캐시 타입입니다'
            }), 400
        
        success = cache_manager.set(key, value, ttl, cache_type_enum, tags, metadata)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '캐시 항목이 설정되었습니다',
                'data': {'key': key}
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': '캐시 항목 설정에 실패했습니다'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 항목 설정 실패: {str(e)}'
        }), 500

@cache_bp.route('/get/<key>', methods=['GET'])
def get_cache(key):
    """캐시 항목 조회"""
    try:
        value = cache_manager.get(key)
        
        if value is not None:
            return jsonify({
                'status': 'success',
                'data': {
                    'key': key,
                    'value': value
                }
            }), 200
        else:
            return jsonify({
                'status': 'not_found',
                'message': '캐시 항목을 찾을 수 없습니다'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 항목 조회 실패: {str(e)}'
        }), 500

@cache_bp.route('/delete/<key>', methods=['DELETE'])
def delete_cache(key):
    """캐시 항목 삭제"""
    try:
        success = cache_manager.delete(key)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '캐시 항목이 삭제되었습니다'
            }), 200
        else:
            return jsonify({
                'status': 'not_found',
                'message': '캐시 항목을 찾을 수 없습니다'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 항목 삭제 실패: {str(e)}'
        }), 500

@cache_bp.route('/clear', methods=['POST'])
def clear_cache():
    """캐시 전체 삭제"""
    try:
        data = request.get_json() or {}
        cache_type = data.get('cache_type')
        
        if cache_type:
            try:
                cache_type_enum = CacheType(cache_type)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': '유효하지 않은 캐시 타입입니다'
                }), 400
        else:
            cache_type_enum = None
        
        success = cache_manager.clear(cache_type_enum)
        
        if success:
            cache_type_str = cache_type if cache_type else 'all'
            return jsonify({
                'status': 'success',
                'message': f'{cache_type_str} 캐시가 삭제되었습니다'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '캐시 삭제에 실패했습니다'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 삭제 실패: {str(e)}'
        }), 500

@cache_bp.route('/tags', methods=['POST'])
def get_by_tags():
    """태그로 캐시 항목 조회"""
    try:
        data = request.get_json()
        tags = data.get('tags', [])
        
        if not tags:
            return jsonify({
                'status': 'error',
                'message': '태그는 필수입니다'
            }), 400
        
        items = cache_manager.get_by_tags(tags)
        
        return jsonify({
            'status': 'success',
            'data': {
                'tags': tags,
                'items': items,
                'count': len(items)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'태그 조회 실패: {str(e)}'
        }), 500

@cache_bp.route('/invalidate', methods=['POST'])
def invalidate_by_tags():
    """태그로 캐시 항목 무효화"""
    try:
        data = request.get_json()
        tags = data.get('tags', [])
        
        if not tags:
            return jsonify({
                'status': 'error',
                'message': '태그는 필수입니다'
            }), 400
        
        count = cache_manager.invalidate_by_tags(tags)
        
        return jsonify({
            'status': 'success',
            'message': f'{count}개의 캐시 항목이 무효화되었습니다',
            'data': {
                'tags': tags,
                'invalidated_count': count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 무효화 실패: {str(e)}'
        }), 500

@cache_bp.route('/config', methods=['GET'])
def get_config():
    """캐시 설정 조회"""
    try:
        config = cache_manager.config
        return jsonify({
            'status': 'success',
            'data': {
                'max_memory_size': config.max_memory_size,
                'max_disk_size': config.max_disk_size,
                'default_ttl': config.default_ttl,
                'cleanup_interval': config.cleanup_interval,
                'enable_compression': config.enable_compression,
                'enable_encryption': config.enable_encryption
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 조회 실패: {str(e)}'
        }), 500

@cache_bp.route('/config', methods=['PUT'])
def update_config():
    """캐시 설정 업데이트"""
    try:
        data = request.get_json()
        
        # 설정 업데이트 (실제로는 재시작이 필요할 수 있음)
        if 'max_memory_size' in data:
            cache_manager.config.max_memory_size = data['max_memory_size']
        if 'max_disk_size' in data:
            cache_manager.config.max_disk_size = data['max_disk_size']
        if 'default_ttl' in data:
            cache_manager.config.default_ttl = data['default_ttl']
        if 'cleanup_interval' in data:
            cache_manager.config.cleanup_interval = data['cleanup_interval']
        if 'enable_compression' in data:
            cache_manager.config.enable_compression = data['enable_compression']
        if 'enable_encryption' in data:
            cache_manager.config.enable_encryption = data['enable_encryption']
        
        return jsonify({
            'status': 'success',
            'message': '캐시 설정이 업데이트되었습니다'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 업데이트 실패: {str(e)}'
        }), 500

@cache_bp.route('/keys', methods=['GET'])
def list_keys():
    """캐시 키 목록 조회"""
    try:
        memory_keys = list(cache_manager.memory_cache.keys())
        disk_keys = list(cache_manager.disk_cache.keys())
        
        return jsonify({
            'status': 'success',
            'data': {
                'memory_keys': memory_keys,
                'disk_keys': disk_keys,
                'total_keys': len(memory_keys) + len(disk_keys)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'키 목록 조회 실패: {str(e)}'
        }), 500 