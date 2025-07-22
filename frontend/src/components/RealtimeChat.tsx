import React, { useEffect, useState, useRef } from 'react';
import { useChatWebSocket } from '../hooks/useWebSocket';

interface ChatMessage {
  id: string;
  sender: string;
  message: string;
  timestamp: string;
  type: 'message' | 'system' | 'notification';
}

interface RealtimeChatProps {
  room: string;
  user_id: string;
}

export const RealtimeChat: React.FC<RealtimeChatProps> = ({ room, user_id }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    isConnected, 
    lastMessage, 
    joinRoom, 
    leaveRoom, 
    sendChatMessage 
  } = useChatWebSocket(user_id, room);

  useEffect(() => {
    joinRoom();
    return () => leaveRoom();
  }, [joinRoom, leaveRoom]);

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'new_message') {
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        sender: lastMessage.sender || 'Unknown',
        message: lastMessage.message,
        timestamp: lastMessage.timestamp,
        type: 'message'
      };
      setMessages(prev => [...prev, newMessage]);
    }
  }, [lastMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && isConnected) {
      sendChatMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <div className="flex flex-col h-96 bg-white border border-gray-200 rounded-lg">
      {/* 채팅 헤더 */}
      <div className="p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">채팅방: {room}</h3>
            <p className="text-sm text-gray-500">
              {isConnected ? '연결됨' : '연결 중...'}
            </p>
          </div>
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            메시지가 없습니다. 대화를 시작해보세요!
          </div>
        ) : (
          messages.map(message => (
            <div
              key={message.id}
              className={`flex ${message.sender === user_id ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === user_id
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                {message.sender !== user_id && (
                  <p className="text-xs opacity-75 mb-1">{message.sender}</p>
                )}
                <p className="text-sm">{message.message}</p>
                <p className="text-xs opacity-75 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={!isConnected}
          />
          <button
            type="submit"
            disabled={!isConnected || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            전송
          </button>
        </form>
        {isTyping && (
          <p className="text-xs text-gray-500 mt-2">누군가 입력 중...</p>
        )}
      </div>
    </div>
  );
}; 