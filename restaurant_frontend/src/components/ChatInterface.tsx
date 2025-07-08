'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  Send, 
  Plus, 
  Search, 
  Users, 
  MessageCircle, 
  MoreVertical,
  Phone,
  Video,
  Paperclip,
  Smile
} from 'lucide-react';
import { useChat } from '@/hooks/useChat';
import { cn } from '@/lib/utils';

interface ChatInterfaceProps {
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ className }) => {
  const {
    rooms,
    currentRoom,
    messages,
    users,
    isConnected,
    typingUsers,
    selectRoom,
    sendMessage,
    handleTyping,
    createRoom,
    searchUsers,
    addParticipant,
  } = useChat();

  const [messageInput, setMessageInput] = useState('');
  const [showUserSearch, setShowUserSearch] = useState(false);
  const [newRoomName, setNewRoomName] = useState('');
  const [selectedUsers, setSelectedUsers] = useState<number[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 메시지 자동 스크롤
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 메시지 전송
  const handleSendMessage = () => {
    if (messageInput.trim() && currentRoom) {
      sendMessage(messageInput);
      setMessageInput('');
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  // Enter 키로 메시지 전송
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 새 채팅방 생성
  const handleCreateRoom = async () => {
    if (newRoomName.trim()) {
      await createRoom(newRoomName, 'group', selectedUsers);
      setNewRoomName('');
      setSelectedUsers([]);
      setShowUserSearch(false);
    }
  };

  // 사용자 선택/해제
  const toggleUserSelection = (userId: number) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  // 시간 포맷팅
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={cn("flex h-full", className)}>
      {/* 채팅방 목록 */}
      <div className="w-80 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">채팅</h2>
            <Button
              size="sm"
              onClick={() => setShowUserSearch(true)}
              className="flex items-center space-x-1"
            >
              <Plus className="w-4 h-4" />
              <span>새 방</span>
            </Button>
          </div>
          
          {/* 연결 상태 */}
          <div className="flex items-center space-x-2 mb-3">
            <div className={cn(
              "w-2 h-2 rounded-full",
              isConnected ? "bg-green-500" : "bg-red-500"
            )} />
            <span className="text-sm text-gray-500">
              {isConnected ? "연결됨" : "연결 안됨"}
            </span>
          </div>

          {/* 새 방 생성 */}
          {showUserSearch && (
            <div className="space-y-3 p-3 bg-gray-50 rounded-lg mb-3">
              <Input
                placeholder="채팅방 이름"
                value={newRoomName}
                onChange={(e) => setNewRoomName(e.target.value)}
              />
              <Button
                size="sm"
                onClick={handleCreateRoom}
                disabled={!newRoomName.trim()}
                className="w-full"
              >
                방 만들기
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowUserSearch(false)}
                className="w-full"
              >
                취소
              </Button>
            </div>
          )}
        </div>

        {/* 채팅방 목록 */}
        <div className="space-y-1 p-2">
          {rooms.map((room) => (
            <div
              key={room.id}
              onClick={() => selectRoom(room)}
              className={cn(
                "p-3 rounded-lg cursor-pointer transition-colors",
                currentRoom?.id === room.id
                  ? "bg-blue-100 border border-blue-200"
                  : "hover:bg-gray-50"
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <MessageCircle className="w-4 h-4 text-gray-500" />
                    <h3 className="font-medium text-sm truncate">{room.name}</h3>
                    {room.unread_count > 0 && (
                      <Badge variant="destructive" className="text-xs">
                        {room.unread_count}
                      </Badge>
                    )}
                  </div>
                  {room.last_message && (
                    <p className="text-xs text-gray-500 truncate mt-1">
                      {room.last_message.user_name}: {room.last_message.message}
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="w-3 h-3 text-gray-400" />
                  <span className="text-xs text-gray-400">{room.participant_count}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 채팅 메시지 영역 */}
      <div className="flex-1 flex flex-col">
        {currentRoom ? (
          <>
            {/* 채팅방 헤더 */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div>
                    <h3 className="font-semibold">{currentRoom.name}</h3>
                    <p className="text-sm text-gray-500">
                      {currentRoom.participant_count}명 참가 중
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button size="sm" variant="outline">
                    <Phone className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="outline">
                    <Video className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="outline">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* 메시지 목록 */}
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex space-x-3",
                    message.is_own ? "flex-row-reverse space-x-reverse" : ""
                  )}
                >
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={message.user.avatar} />
                    <AvatarFallback>
                      {message.user.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className={cn(
                    "flex-1 max-w-xs",
                    message.is_own ? "text-right" : ""
                  )}>
                    <div className={cn(
                      "inline-block p-3 rounded-lg",
                      message.is_own
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 text-gray-900"
                    )}>
                      <p className="text-sm">{message.message}</p>
                    </div>
                    <div className={cn(
                      "mt-1 text-xs text-gray-500",
                      message.is_own ? "text-right" : ""
                    )}>
                      {message.user.name} • {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              ))}
              
              {/* 타이핑 표시 */}
              {typingUsers.length > 0 && (
                <div className="flex space-x-3">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback>?</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="inline-block p-3 rounded-lg bg-gray-100">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {typingUsers.join(', ')}님이 입력 중...
                    </p>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* 메시지 입력 */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex items-center space-x-2">
                <Button size="sm" variant="outline">
                  <Paperclip className="w-4 h-4" />
                </Button>
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    placeholder="메시지를 입력하세요..."
                    value={messageInput}
                    onChange={(e) => {
                      setMessageInput(e.target.value);
                      handleTyping();
                    }}
                    onKeyPress={handleKeyPress}
                    className="pr-10"
                  />
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute right-1 top-1/2 transform -translate-y-1/2"
                  >
                    <Smile className="w-4 h-4" />
                  </Button>
                </div>
                <Button
                  onClick={handleSendMessage}
                  disabled={!messageInput.trim()}
                  size="sm"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </>
        ) : (
          /* 채팅방 선택 안내 */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                채팅방을 선택하세요
              </h3>
              <p className="text-gray-500">
                왼쪽에서 채팅방을 선택하여 대화를 시작하세요
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface; 