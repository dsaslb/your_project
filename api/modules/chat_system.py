from flask import Blueprint, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import json
import uuid
from typing import Dict, List, Optional
from models import db, User, ChatRoom, ChatMessage, ChatParticipant
from utils.decorators import login_required, role_required
from utils.notify import send_notification

chat_bp = Blueprint('chat', __name__)

# 활성 채팅방 관리
active_rooms: Dict[str, Dict] = {}
user_sessions: Dict[str, str] = {}  # user_id -> session_id

class ChatSystem:
    def __init__(self):
        self.rooms = active_rooms
        self.user_sessions = user_sessions
    
    def create_room(self, name: str, room_type: str, creator_id: int, participants: List[int] = None) -> Dict:
        """새 채팅방 생성"""
        room_id = str(uuid.uuid4())
        
        # 데이터베이스에 채팅방 저장
        new_room = ChatRoom(
            id=room_id,
            name=name,
            room_type=room_type,  # 'direct', 'group', 'department'
            creator_id=creator_id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_room)
        
        # 참가자 추가
        if participants:
            for user_id in participants:
                participant = ChatParticipant(
                    room_id=room_id,
                    user_id=user_id,
                    joined_at=datetime.utcnow()
                )
                db.session.add(participant)
        
        # 생성자도 참가자로 추가
        creator_participant = ChatParticipant(
            room_id=room_id,
            user_id=creator_id,
            joined_at=datetime.utcnow()
        )
        db.session.add(creator_participant)
        
        db.session.commit()
        
        # 활성 채팅방에 추가
        self.rooms[room_id] = {
            'name': name,
            'type': room_type,
            'creator_id': creator_id,
            'participants': participants or [],
            'messages': [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        return {
            'room_id': room_id,
            'name': name,
            'type': room_type,
            'creator_id': creator_id,
            'participants': participants or []
        }
    
    def send_message(self, room_id: str, user_id: int, message: str, message_type: str = 'text') -> Dict:
        """메시지 전송"""
        if room_id not in self.rooms:
            return {'error': '채팅방을 찾을 수 없습니다'}
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # 데이터베이스에 메시지 저장
        new_message = ChatMessage(
            id=message_id,
            room_id=room_id,
            user_id=user_id,
            message=message,
            message_type=message_type,
            created_at=timestamp
        )
        db.session.add(new_message)
        db.session.commit()
        
        # 사용자 정보 가져오기
        user = User.query.get(user_id)
        user_info = {
            'id': user.id,
            'name': user.name,
            'role': user.role,
            'avatar': user.avatar or f"https://ui-avatars.com/api/?name={user.name}&background=random"
        }
        
        message_data = {
            'id': message_id,
            'room_id': room_id,
            'user': user_info,
            'message': message,
            'type': message_type,
            'timestamp': timestamp.isoformat(),
            'is_own': False
        }
        
        # 활성 채팅방에 메시지 추가
        self.rooms[room_id]['messages'].append(message_data)
        
        return message_data
    
    def get_room_messages(self, room_id: str, limit: int = 50) -> List[Dict]:
        """채팅방 메시지 조회"""
        if room_id not in self.rooms:
            return []
        
        # 데이터베이스에서 메시지 조회
        messages = ChatMessage.query.filter_by(room_id=room_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
        
        message_list = []
        for msg in reversed(messages):  # 최신순으로 정렬
            user = User.query.get(msg.user_id)
            message_list.append({
                'id': msg.id,
                'room_id': msg.room_id,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'role': user.role,
                    'avatar': user.avatar or f"https://ui-avatars.com/api/?name={user.name}&background=random"
                },
                'message': msg.message,
                'type': msg.message_type,
                'timestamp': msg.created_at.isoformat(),
                'is_own': False
            })
        
        return message_list
    
    def get_user_rooms(self, user_id: int) -> List[Dict]:
        """사용자의 채팅방 목록 조회"""
        # 사용자가 참가한 채팅방 조회
        participants = ChatParticipant.query.filter_by(user_id=user_id).all()
        
        rooms = []
        for participant in participants:
            room = ChatRoom.query.get(participant.room_id)
            if room:
                # 최근 메시지 조회
                last_message = ChatMessage.query.filter_by(room_id=room.id)\
                    .order_by(ChatMessage.created_at.desc())\
                    .first()
                
                # 참가자 수 조회
                participant_count = ChatParticipant.query.filter_by(room_id=room.id).count()
                
                rooms.append({
                    'id': room.id,
                    'name': room.name,
                    'type': room.room_type,
                    'creator_id': room.creator_id,
                    'participant_count': participant_count,
                    'last_message': {
                        'message': last_message.message if last_message else '',
                        'timestamp': last_message.created_at.isoformat() if last_message else '',
                        'user_name': User.query.get(last_message.user_id).name if last_message else ''
                    } if last_message else None,
                    'unread_count': 0  # TODO: 읽지 않은 메시지 수 구현
                })
        
        return rooms
    
    def add_participant(self, room_id: str, user_id: int) -> bool:
        """채팅방에 참가자 추가"""
        if room_id not in self.rooms:
            return False
        
        # 이미 참가자인지 확인
        existing = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if existing:
            return True
        
        # 참가자 추가
        participant = ChatParticipant(
            room_id=room_id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        db.session.add(participant)
        db.session.commit()
        
        # 활성 채팅방에 추가
        if user_id not in self.rooms[room_id]['participants']:
            self.rooms[room_id]['participants'].append(user_id)
        
        return True
    
    def remove_participant(self, room_id: str, user_id: int) -> bool:
        """채팅방에서 참가자 제거"""
        if room_id not in self.rooms:
            return False
        
        # 참가자 제거
        participant = ChatParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
        if participant:
            db.session.delete(participant)
            db.session.commit()
        
        # 활성 채팅방에서 제거
        if user_id in self.rooms[room_id]['participants']:
            self.rooms[room_id]['participants'].remove(user_id)
        
        return True

# 채팅 시스템 인스턴스
chat_system = ChatSystem()

# API 라우트
@chat_bp.route('/rooms', methods=['GET'])
@login_required
def get_rooms():
    """사용자의 채팅방 목록 조회"""
    user_id = session.get('user_id')
    rooms = chat_system.get_user_rooms(user_id)
    return jsonify({'rooms': rooms})

@chat_bp.route('/rooms', methods=['POST'])
@login_required
def create_room():
    """새 채팅방 생성"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    name = data.get('name')
    room_type = data.get('type', 'group')
    participants = data.get('participants', [])
    
    if not name:
        return jsonify({'error': '채팅방 이름이 필요합니다'}), 400
    
    room = chat_system.create_room(name, room_type, user_id, participants)
    return jsonify(room), 201

@chat_bp.route('/rooms/<room_id>/messages', methods=['GET'])
@login_required
def get_messages(room_id):
    """채팅방 메시지 조회"""
    limit = request.args.get('limit', 50, type=int)
    messages = chat_system.get_room_messages(room_id, limit)
    return jsonify({'messages': messages})

@chat_bp.route('/rooms/<room_id>/messages', methods=['POST'])
@login_required
def send_message(room_id):
    """메시지 전송"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    message = data.get('message')
    message_type = data.get('type', 'text')
    
    if not message:
        return jsonify({'error': '메시지 내용이 필요합니다'}), 400
    
    message_data = chat_system.send_message(room_id, user_id, message, message_type)
    return jsonify(message_data), 201

@chat_bp.route('/rooms/<room_id>/participants', methods=['POST'])
@login_required
def add_participant(room_id):
    """채팅방에 참가자 추가"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': '사용자 ID가 필요합니다'}), 400
    
    success = chat_system.add_participant(room_id, user_id)
    if success:
        return jsonify({'message': '참가자가 추가되었습니다'})
    else:
        return jsonify({'error': '채팅방을 찾을 수 없습니다'}), 404

@chat_bp.route('/rooms/<room_id>/participants/<int:user_id>', methods=['DELETE'])
@login_required
def remove_participant(room_id, user_id):
    """채팅방에서 참가자 제거"""
    success = chat_system.remove_participant(room_id, user_id)
    if success:
        return jsonify({'message': '참가자가 제거되었습니다'})
    else:
        return jsonify({'error': '채팅방을 찾을 수 없습니다'}), 404

@chat_bp.route('/users/search', methods=['GET'])
@login_required
def search_users():
    """사용자 검색"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'users': []})
    
    users = User.query.filter(User.name.contains(query)).limit(10).all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'name': user.name,
            'role': user.role,
            'avatar': user.avatar or f"https://ui-avatars.com/api/?name={user.name}&background=random"
        })
    
    return jsonify({'users': user_list})

# WebSocket 이벤트 핸들러
def handle_connect(socketio):
    """클라이언트 연결"""
    user_id = session.get('user_id')
    if user_id:
        user_sessions[user_id] = request.sid
        emit('user_connected', {'user_id': user_id})

def handle_disconnect(socketio):
    """클라이언트 연결 해제"""
    user_id = session.get('user_id')
    if user_id and user_id in user_sessions:
        del user_sessions[user_id]

def handle_join_room(socketio, data):
    """채팅방 참가"""
    room_id = data.get('room_id')
    user_id = session.get('user_id')
    
    if room_id and user_id:
        join_room(room_id)
        emit('user_joined', {
            'room_id': room_id,
            'user_id': user_id,
            'user_name': User.query.get(user_id).name
        }, room=room_id)

def handle_leave_room(socketio, data):
    """채팅방 나가기"""
    room_id = data.get('room_id')
    user_id = session.get('user_id')
    
    if room_id and user_id:
        leave_room(room_id)
        emit('user_left', {
            'room_id': room_id,
            'user_id': user_id,
            'user_name': User.query.get(user_id).name
        }, room=room_id)

def handle_send_message(socketio, data):
    """실시간 메시지 전송"""
    room_id = data.get('room_id')
    message = data.get('message')
    message_type = data.get('type', 'text')
    user_id = session.get('user_id')
    
    if room_id and message and user_id:
        message_data = chat_system.send_message(room_id, user_id, message, message_type)
        emit('new_message', message_data, room=room_id)
        
        # 참가자들에게 알림 전송
        room = chat_system.rooms.get(room_id)
        if room:
            for participant_id in room['participants']:
                if participant_id != user_id:
                    send_notification(
                        user_id=participant_id,
                        title=f"새 메시지 - {room['name']}",
                        message=f"{User.query.get(user_id).name}: {message[:50]}...",
                        type="chat",
                        data={'room_id': room_id}
                    )

def handle_typing(socketio, data):
    """타이핑 상태 전송"""
    room_id = data.get('room_id')
    user_id = session.get('user_id')
    is_typing = data.get('is_typing', False)
    
    if room_id and user_id:
        user = User.query.get(user_id)
        emit('user_typing', {
            'room_id': room_id,
            'user_id': user_id,
            'user_name': user.name,
            'is_typing': is_typing
        }, room=room_id)

# WebSocket 이벤트 등록 함수
def register_chat_events(socketio):
    """채팅 WebSocket 이벤트 등록"""
    @socketio.on('connect')
    def on_connect():
        handle_connect(socketio)
    
    @socketio.on('disconnect')
    def on_disconnect():
        handle_disconnect(socketio)
    
    @socketio.on('join_room')
    def on_join_room(data):
        handle_join_room(socketio, data)
    
    @socketio.on('leave_room')
    def on_leave_room(data):
        handle_leave_room(socketio, data)
    
    @socketio.on('send_message')
    def on_send_message(data):
        handle_send_message(socketio, data)
    
    @socketio.on('typing')
    def on_typing(data):
        handle_typing(socketio, data) 