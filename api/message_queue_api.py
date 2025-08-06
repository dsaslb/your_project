from flask import Blueprint, request, jsonify
from message_queue.queue_manager import QueueManager, QueueConfig, QueueType, MessagePriority
import os
from datetime import datetime

# 메시지 큐 관리자 초기화
queue_config = QueueConfig(
    data_dir="data/message_queue",
    max_queue_size=10000,
    message_ttl=3600,
    retry_attempts=3,
    retry_delay=60
)
queue_manager = QueueManager(queue_config)

message_queue_bp = Blueprint('message_queue', __name__, url_prefix='/api/message-queue')

@message_queue_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'success', 'message': '메시지 큐 시스템이 정상적으로 작동합니다'}), 200

@message_queue_bp.route('/stats', methods=['GET'])
def get_queue_stats():
    stats = queue_manager.get_queue_stats()
    return jsonify({'status': 'success', 'data': stats}), 200

@message_queue_bp.route('/queues', methods=['GET'])
def get_queues():
    queues = [
        {
            'queue_id': q.queue_id,
            'name': q.name,
            'type': q.queue_type.value,
            'max_size': q.max_size,
            'current_size': q.current_size,
            'is_active': q.is_active,
            'created_at': q.created_at.isoformat(),
            'updated_at': q.updated_at.isoformat()
        }
        for q in queue_manager.queues.values()
    ]
    return jsonify({'status': 'success', 'data': queues}), 200

@message_queue_bp.route('/queues', methods=['POST'])
def create_queue():
    data = request.get_json()
    name = data.get('name')
    queue_type = data.get('queue_type', 'standard')
    max_size = data.get('max_size', 1000)
    try:
        queue_type_enum = QueueType(queue_type)
    except ValueError:
        return jsonify({'status': 'error', 'message': '유효하지 않은 큐 타입'}), 400
    queue_id = queue_manager.create_queue(name, queue_type_enum, max_size)
    return jsonify({'status': 'success', 'queue_id': queue_id}), 201

@message_queue_bp.route('/queues/<queue_id>', methods=['DELETE'])
def delete_queue(queue_id):
    if queue_id not in queue_manager.queues:
        return jsonify({'status': 'error', 'message': '큐를 찾을 수 없습니다'}), 404
    queue_manager.purge_queue(queue_id)
    del queue_manager.queues[queue_id]
    return jsonify({'status': 'success', 'message': '큐가 삭제되었습니다'}), 200

@message_queue_bp.route('/messages', methods=['POST'])
def publish_message():
    data = request.get_json()
    queue_id = data.get('queue_id')
    topic = data.get('topic')
    payload = data.get('payload')
    priority = data.get('priority', 'normal')
    try:
        priority_enum = MessagePriority[priority.upper()]
    except KeyError:
        priority_enum = MessagePriority.NORMAL
    message_id = queue_manager.publish_message(queue_id, topic, payload, priority_enum)
    return jsonify({'status': 'success', 'message_id': message_id}), 201

@message_queue_bp.route('/messages/consume', methods=['POST'])
def consume_message():
    data = request.get_json()
    queue_id = data.get('queue_id')
    message = queue_manager.consume_message(queue_id)
    if not message:
        return jsonify({'status': 'empty', 'message': '대기 중인 메시지가 없습니다'}), 200
    return jsonify({
        'status': 'success',
        'data': {
            'message_id': message.message_id,
            'topic': message.topic,
            'payload': message.payload,
            'priority': message.priority.value,
            'status': message.status.value,
            'created_at': message.created_at.isoformat()
        }
    }), 200

@message_queue_bp.route('/messages/<message_id>/complete', methods=['POST'])
def complete_message(message_id):
    data = request.get_json() or {}
    success = data.get('success', True)
    queue_manager.complete_message(message_id, success)
    return jsonify({'status': 'success', 'message': '메시지 완료 처리됨'}), 200

@message_queue_bp.route('/subscriptions', methods=['POST'])
def subscribe():
    data = request.get_json()
    queue_id = data.get('queue_id')
    topic = data.get('topic')
    callback_url = data.get('callback_url')
    subscription_id = queue_manager.subscribe(queue_id, topic, callback_url)
    return jsonify({'status': 'success', 'subscription_id': subscription_id}), 201

@message_queue_bp.route('/subscriptions/<subscription_id>/cancel', methods=['POST'])
def unsubscribe(subscription_id):
    queue_manager.subscriptions[subscription_id].is_active = False
    queue_manager._save_subscription(queue_manager.subscriptions[subscription_id])
    return jsonify({'status': 'success', 'message': '구독이 해제되었습니다'}), 200