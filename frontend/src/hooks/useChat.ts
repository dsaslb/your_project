import { useState, useEffect, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

interface ChatUser {
  id: number;
  name: string;
  role: string;
  avatar?: string;
}

interface ChatMessage {
  id: string;
  room_id: string;
  user: ChatUser;
  message: string;
  type: string;
  timestamp: string;
  is_own: boolean;
}

interface ChatRoom {
  id: string;
  name: string;
  type: string;
  creator_id: number;
  participant_count: number;
  last_message?: {
    message: string;
    timestamp: string;
    user_name: string;
  };
  unread_count: number;
}

interface ChatState {
  rooms: ChatRoom[];
  currentRoom: ChatRoom | null;
  messages: ChatMessage[];
  users: ChatUser[];
  isConnected: boolean;
  isTyping: boolean;
  typingUsers: string[];
}

export const useChat = () => {
  const [state, setState] = useState<ChatState>({
    rooms: [],
    currentRoom: null,
    messages: [],
    users: [],
    isConnected: false,
    isTyping: false,
    typingUsers: [],
  });

  const socketRef = useRef<Socket | null>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 소켓 연결
  const connectSocket = useCallback(() => {
    if (socketRef.current?.connected) return;

    socketRef.current = io('http://localhost:5000', {
      transports: ['websocket', 'polling'],
    });

    socketRef.current.on('connect', () => {
      setState(prev => ({ ...prev, isConnected: true }));
      console.log('채팅 소켓 연결됨');
    });

    socketRef.current.on('disconnect', () => {
      setState(prev => ({ ...prev, isConnected: false }));
      console.log('채팅 소켓 연결 해제됨');
    });

    socketRef.current.on('new_message', (message: ChatMessage) => {
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, message],
      }));
    });

    socketRef.current.on('user_joined', (data: any) => {
      console.log(`${data.user_name}님이 입장했습니다`);
    });

    socketRef.current.on('user_left', (data: any) => {
      console.log(`${data.user_name}님이 퇴장했습니다`);
    });

    socketRef.current.on('user_typing', (data: any) => {
      setState(prev => ({
        ...prev,
        typingUsers: data.is_typing 
          ? [...prev.typingUsers.filter(u => u !== data.user_name), data.user_name]
          : prev.typingUsers.filter(u => u !== data.user_name),
      }));
    });
  }, []);

  // 소켓 연결 해제
  const disconnectSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
  }, []);

  // 채팅방 목록 조회
  const fetchRooms = useCallback(async () => {
    try {
      const response = await fetch('/api/chat/rooms', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setState(prev => ({ ...prev, rooms: data.rooms }));
      }
    } catch (error) {
      console.error('채팅방 목록 조회 실패:', error);
    }
  }, []);

  // 채팅방 메시지 조회
  const fetchMessages = useCallback(async (roomId: string) => {
    try {
      const response = await fetch(`/api/chat/rooms/${roomId}/messages`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setState(prev => ({ ...prev, messages: data.messages }));
      }
    } catch (error) {
      console.error('메시지 조회 실패:', error);
    }
  }, []);

  // 채팅방 참가
  const joinRoom = useCallback((roomId: string) => {
    if (socketRef.current) {
      socketRef.current.emit('join_room', { room_id: roomId });
    }
  }, []);

  // 채팅방 나가기
  const leaveRoom = useCallback((roomId: string) => {
    if (socketRef.current) {
      socketRef.current.emit('leave_room', { room_id: roomId });
    }
  }, []);

  // 메시지 전송
  const sendMessage = useCallback(async (message: string, type: string = 'text') => {
    if (!state.currentRoom || !message.trim()) return;

    try {
      const response = await fetch(`/api/chat/rooms/${state.currentRoom.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ message, type }),
      });

      if (response.ok) {
        const messageData = await response.json();
        // 소켓으로 실시간 전송
        if (socketRef.current) {
          socketRef.current.emit('send_message', {
            room_id: state.currentRoom.id,
            message,
            type,
          });
        }
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
    }
  }, [state.currentRoom]);

  // 타이핑 상태 전송
  const sendTypingStatus = useCallback((isTyping: boolean) => {
    if (!state.currentRoom || !socketRef.current) return;

    socketRef.current.emit('typing', {
      room_id: state.currentRoom.id,
      is_typing: isTyping,
    });

    setState(prev => ({ ...prev, isTyping }));
  }, [state.currentRoom]);

  // 타이핑 상태 관리
  const handleTyping = useCallback(() => {
    sendTypingStatus(true);

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    typingTimeoutRef.current = setTimeout(() => {
      sendTypingStatus(false);
    }, 3000) as unknown as NodeJS.Timeout;
  }, [sendTypingStatus]);

  // 채팅방 선택
  const selectRoom = useCallback(async (room: ChatRoom) => {
    // 이전 방에서 나가기
    if (state.currentRoom) {
      leaveRoom(state.currentRoom.id);
    }

    setState(prev => ({ ...prev, currentRoom: room, messages: [] }));
    
    // 새 방 참가
    joinRoom(room.id);
    
    // 메시지 로드
    await fetchMessages(room.id);
  }, [state.currentRoom, leaveRoom, joinRoom, fetchMessages]);

  // 새 채팅방 생성
  const createRoom = useCallback(async (name: string, type: string = 'group', participants: number[] = []) => {
    try {
      const response = await fetch('/api/chat/rooms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ name, type, participants }),
      });

      if (response.ok) {
        const newRoom = await response.json();
        await fetchRooms(); // 방 목록 새로고침
        return newRoom;
      }
    } catch (error) {
      console.error('채팅방 생성 실패:', error);
    }
  }, [fetchRooms]);

  // 사용자 검색
  const searchUsers = useCallback(async (query: string) => {
    if (!query.trim()) {
      setState(prev => ({ ...prev, users: [] }));
      return;
    }

    try {
      const response = await fetch(`/api/chat/users/search?q=${encodeURIComponent(query)}`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setState(prev => ({ ...prev, users: data.users }));
      }
    } catch (error) {
      console.error('사용자 검색 실패:', error);
    }
  }, []);

  // 참가자 추가
  const addParticipant = useCallback(async (roomId: string, userId: number) => {
    try {
      const response = await fetch(`/api/chat/rooms/${roomId}/participants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ user_id: userId }),
      });

      if (response.ok) {
        await fetchRooms(); // 방 목록 새로고침
        return true;
      }
    } catch (error) {
      console.error('참가자 추가 실패:', error);
    }
    return false;
  }, [fetchRooms]);

  // 참가자 제거
  const removeParticipant = useCallback(async (roomId: string, userId: number) => {
    try {
      const response = await fetch(`/api/chat/rooms/${roomId}/participants/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (response.ok) {
        await fetchRooms(); // 방 목록 새로고침
        return true;
      }
    } catch (error) {
      console.error('참가자 제거 실패:', error);
    }
    return false;
  }, [fetchRooms]);

  // 초기화
  useEffect(() => {
    connectSocket();
    fetchRooms();

    return () => {
      disconnectSocket();
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [connectSocket, disconnectSocket, fetchRooms]);

  return {
    ...state,
    connectSocket,
    disconnectSocket,
    fetchRooms,
    fetchMessages,
    joinRoom,
    leaveRoom,
    sendMessage,
    sendTypingStatus,
    handleTyping,
    selectRoom,
    createRoom,
    searchUsers,
    addParticipant,
    removeParticipant,
  };
}; 