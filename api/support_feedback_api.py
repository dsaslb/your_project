"""
피드백/문의/FAQ API
- /api/support/feedback [GET, POST]
- /api/support/faq [GET, POST, PUT, DELETE]
"""
from flask import Blueprint, request, jsonify, abort
import os
import json
from datetime import datetime
from middleware.security import admin_required

bp = Blueprint('support_feedback_api', __name__, url_prefix='/api/support')

FEEDBACK_FILE = 'feedback/feedback.json'
FAQ_FILE = 'feedback/faq.json'

# 유틸: 파일 읽기/쓰기

def read_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """피드백/문의 등록 (고객/직원)"""
    data = request.json
    entry = {
        'id': int(datetime.now().timestamp() * 1000),
        'user': data.get('user', '익명'),
        'message': data.get('message'),
        'type': data.get('type', 'feedback'),
        'created_at': datetime.now().isoformat()
    }
    feedbacks = read_json(FEEDBACK_FILE)
    feedbacks.append(entry)
    write_json(FEEDBACK_FILE, feedbacks[-200:])
    return jsonify({'result': 'ok', 'feedback': entry})

@bp.route('/feedback', methods=['GET'])
@admin_required
def list_feedback():
    """피드백/문의 목록 조회 (관리자/운영자)"""
    feedbacks = read_json(FEEDBACK_FILE)
    return jsonify({'feedbacks': feedbacks[::-1]})

@bp.route('/faq', methods=['GET'])
def list_faq():
    """FAQ 목록 조회"""
    faqs = read_json(FAQ_FILE)
    return jsonify({'faqs': faqs[::-1]})

@bp.route('/faq', methods=['POST'])
@admin_required
def add_faq():
    """FAQ 등록 (관리자)"""
    data = request.json
    entry = {
        'id': int(datetime.now().timestamp() * 1000),
        'question': data.get('question'),
        'answer': data.get('answer'),
        'created_at': datetime.now().isoformat()
    }
    faqs = read_json(FAQ_FILE)
    faqs.append(entry)
    write_json(FAQ_FILE, faqs[-100:])
    return jsonify({'result': 'ok', 'faq': entry})

@bp.route('/faq/<int:faq_id>', methods=['PUT'])
@admin_required
def update_faq(faq_id):
    """FAQ 수정 (관리자)"""
    data = request.json
    faqs = read_json(FAQ_FILE)
    for faq in faqs:
        if faq['id'] == faq_id:
            faq['question'] = data.get('question', faq['question'])
            faq['answer'] = data.get('answer', faq['answer'])
    write_json(FAQ_FILE, faqs)
    return jsonify({'result': 'ok'})

@bp.route('/faq/<int:faq_id>', methods=['DELETE'])
@admin_required
def delete_faq(faq_id):
    """FAQ 삭제 (관리자)"""
    faqs = read_json(FAQ_FILE)
    faqs = [faq for faq in faqs if faq['id'] != faq_id]
    write_json(FAQ_FILE, faqs)
    return jsonify({'result': 'ok'}) 