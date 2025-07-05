"use client";
import { useState, useEffect } from "react";
import { Sparkles, X } from "lucide-react";

interface NotificationPopupProps {
  message: string;
  delay?: number;
  position?: "bottom-right" | "bottom-left" | "top-right" | "top-left";
}

export default function NotificationPopup({ 
  message, 
  delay = 3000, 
  position = "bottom-right" 
}: NotificationPopupProps) {
  const [showPopup, setShowPopup] = useState(false);
  const [typedText, setTypedText] = useState("");
  const [isTypingComplete, setIsTypingComplete] = useState(false);

  // message가 유효하지 않으면 컴포넌트를 렌더링하지 않음
  if (!message || typeof message !== 'string') {
    return null;
  }

  useEffect(() => {
    const popupTimer = setTimeout(() => {
      setShowPopup(true);
    }, delay);
    return () => clearTimeout(popupTimer);
  }, [delay]);

  useEffect(() => {
    if (showPopup && message) {
      setTypedText(""); // 타이핑 시작 전 텍스트 초기화
      let i = 0;
      const typingInterval = setInterval(() => {
        if (i < message.length) {
          setTypedText(message.substring(0, i + 1)); // substring으로 정확한 텍스트 설정
          i++;
        } else {
          clearInterval(typingInterval);
          setIsTypingComplete(true);
        }
      }, 50);
      return () => clearInterval(typingInterval);
    }
  }, [showPopup, message]);

  const handleConfirm = () => {
    setShowPopup(false);
    setTypedText("");
    setIsTypingComplete(false);
  };

  const handleClose = () => {
    setShowPopup(false);
    setTypedText("");
    setIsTypingComplete(false);
  };

  const positionClasses = {
    "bottom-right": "bottom-6 right-6",
    "bottom-left": "bottom-6 left-6",
    "top-right": "top-6 right-6",
    "top-left": "top-6 left-6",
  };

  if (!showPopup) return null;

  return (
    <div className={`fixed ${positionClasses[position]} w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 z-50`}>
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-900 dark:text-white mb-2 min-h-[1.25rem]">
            {typedText}
            {!isTypingComplete && <span className="animate-pulse">|</span>}
          </p>
          <div className="flex gap-2">
            <button 
              onClick={handleConfirm}
              className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors"
            >
              확인
            </button>
            <button
              onClick={handleClose}
              className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              닫기
            </button>
          </div>
        </div>
        <button
          onClick={handleClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
} 