"""
플러그인 마켓/설치/관리 API (관리자 전용)
- /api/admin/plugins/market [GET]
- /api/admin/plugins/installed [GET]
- /api/admin/plugins/install [POST]
- /api/admin/plugins/update [POST]
- /api/admin/plugins/uninstall [POST]
"""
from flask import Blueprint, request, jsonify, abort
from middleware.security import admin_required
import json
import os

bp = Blueprint('admin_plugins_api', __name__, url_prefix='/api/admin/plugins')

MARKET_FILE = 'marketplace/configs.json'  # 예시: 마켓 플러그인 목록
INSTALLED_FILE = 'marketplace/installed.json'  # 예시: 설치된 플러그인 목록

# 유틸: 파일 읽기/쓰기

def read_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@bp.route('/market', methods=['GET'])
@admin_required
def list_market_plugins():
    """마켓 플러그인 목록/검색"""
    q = request.args.get('q', '')
    plugins = read_json(MARKET_FILE)
    if q:
        plugins = [p for p in plugins if q.lower() in p.get('name','').lower() or q.lower() in p.get('description','').lower()]
    return jsonify({'plugins': plugins})

@bp.route('/installed', methods=['GET'])
@admin_required
def list_installed_plugins():
    """설치된 플러그인 목록"""
    plugins = read_json(INSTALLED_FILE)
    return jsonify({'plugins': plugins})

@bp.route('/install', methods=['POST'])
@admin_required
def install_plugin():
    """플러그인 설치"""
    data = request.json
    plugin_id = data.get('plugin_id')
    if not plugin_id:
        abort(400, 'plugin_id는 필수입니다.')
    market_plugins = read_json(MARKET_FILE)
    plugin = next((p for p in market_plugins if p['id'] == plugin_id), None)
    if not plugin:
        abort(404, '플러그인을 찾을 수 없습니다.')
    installed = read_json(INSTALLED_FILE)
    if any(p['id'] == plugin_id for p in installed):
        abort(400, '이미 설치된 플러그인입니다.')
    installed.append(plugin)
    write_json(INSTALLED_FILE, installed)
    # 실제 설치 로직(예: pip install, 파일 복사 등) 필요
    return jsonify({'result': 'ok', 'plugin': plugin})

@bp.route('/update', methods=['POST'])
@admin_required
def update_plugin():
    """플러그인 업데이트"""
    data = request.json
    plugin_id = data.get('plugin_id')
    if not plugin_id:
        abort(400, 'plugin_id는 필수입니다.')
    # 실제 업데이트 로직 필요 (예: 버전 비교, 파일 교체 등)
    return jsonify({'result': 'ok', 'plugin_id': plugin_id})

@bp.route('/uninstall', methods=['POST'])
@admin_required
def uninstall_plugin():
    """플러그인 삭제"""
    data = request.json
    plugin_id = data.get('plugin_id')
    if not plugin_id:
        abort(400, 'plugin_id는 필수입니다.')
    installed = read_json(INSTALLED_FILE)
    installed = [p for p in installed if p['id'] != plugin_id]
    write_json(INSTALLED_FILE, installed)
    # 실제 삭제 로직(예: 파일 삭제, pip uninstall 등) 필요
    return jsonify({'result': 'ok', 'plugin_id': plugin_id}) 