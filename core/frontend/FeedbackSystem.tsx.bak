/**
 * 피드백 시스템 UI
 * 사용자 피드백을 수집하고 관리하는 React 컴포넌트
 */

import React, { useState, useEffect } from 'react';

// 피드백 타입
export enum FeedbackType {
  BUG_REPORT = 'bug_report',
  FEATURE_REQUEST = 'feature_request',
  IMPROVEMENT = 'improvement',
  QUESTION = 'question',
  COMPLIMENT = 'compliment',
  OTHER = 'other'
}

// 피드백 상태
export enum FeedbackStatus {
  PENDING = 'pending',
  IN_REVIEW = 'in_review',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  REJECTED = 'rejected'
}

// 피드백 데이터 인터페이스
export interface FeedbackData {
  id: string;
  user_id: string;
  type: FeedbackType;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: FeedbackStatus;
  created_at: string;
  updated_at: string;
  tags: string[];
  attachments: string[];
  metadata: Record<string, any>;
}

// 피드백 제출 데이터 인터페이스
export interface FeedbackSubmitData {
  type: FeedbackType;
  title: string;
  description: string;
  category: string;
  priority: string;
  tags: string[];
  attachments: string[];
  metadata?: Record<string, any>;
}

// 피드백 시스템 Props
interface FeedbackSystemProps {
  userId: string;
  isAdmin?: boolean;
  onFeedbackSubmit?: (feedbackId: string) => void;
  onFeedbackUpdate?: (feedbackId: string, status: FeedbackStatus) => void;
  onFeedbackClick?: (feedback: FeedbackData) => void; // 상세 모달 콜백
}

// 플로팅 피드백 버튼 Props
interface FloatingFeedbackButtonProps {
  onClick: () => void;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
}

// 플로팅 피드백 버튼
export const FloatingFeedbackButton: React.FC<FloatingFeedbackButtonProps> = ({
  onClick,
  position = 'bottom-right'
}) => {
  const positionClasses: Record<'bottom-right' | 'bottom-left' | 'top-right' | 'top-left', string> = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4'
  };

  return (
    <button
      onClick={onClick}
      className={`fixed ${positionClasses[position]} z-50 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 transform hover:scale-110`}
      aria-label="피드백 제출"
    >
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
    </button>
  );
};

// 피드백 제출 모달 Props
interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: FeedbackSubmitData) => Promise<void>;
  categories?: string[];
  tags?: string[];
}

// 피드백 제출 모달
export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  categories = ['일반', '기능', 'UI/UX', '성능', '보안', '기타'],
  tags = []
}) => {
  const [formData, setFormData] = useState<FeedbackSubmitData>({
    type: FeedbackType.OTHER,
    title: '',
    description: '',
    category: '일반',
    priority: 'medium',
    tags: [],
    attachments: []
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customTag, setCustomTag] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.description.trim()) {
      alert('제목과 설명을 입력해주세요.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      setFormData({
        type: FeedbackType.OTHER,
        title: '',
        description: '',
        category: '일반',
        priority: 'medium',
        tags: [],
        attachments: []
      });
      onClose();
    } catch (error) {
      console.error('피드백 제출 실패:', error);
      alert('피드백 제출에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const addTag = () => {
    if (customTag.trim() && !formData.tags.includes(customTag.trim())) {
      setFormData((prev: FeedbackSubmitData) => ({
        ...prev,
        tags: [...prev.tags, customTag.trim()]
      }));
      setCustomTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData((prev: FeedbackSubmitData) => ({
      ...prev,
      tags: prev.tags.filter((tag: string) => tag !== tagToRemove)
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">피드백 제출</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 피드백 타입 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              피드백 타입 *
            </label>
            <select
              value={formData.type}
              onChange={(e) => setFormData((prev: FeedbackSubmitData) => ({ ...prev, type: e.target.value as FeedbackType }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value={FeedbackType.BUG_REPORT}>버그 신고</option>
              <option value={FeedbackType.FEATURE_REQUEST}>기능 요청</option>
              <option value={FeedbackType.IMPROVEMENT}>개선 제안</option>
              <option value={FeedbackType.QUESTION}>질문</option>
              <option value={FeedbackType.COMPLIMENT}>칭찬</option>
              <option value={FeedbackType.OTHER}>기타</option>
            </select>
          </div>

          {/* 제목 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              제목 *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData((prev: FeedbackSubmitData) => ({ ...prev, title: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="피드백 제목을 입력하세요"
              required
            />
          </div>

          {/* 설명 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              상세 설명 *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData((prev: FeedbackSubmitData) => ({ ...prev, description: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={4}
              placeholder="자세한 내용을 입력하세요"
              required
            />
          </div>

          {/* 카테고리 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              카테고리
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData((prev: FeedbackSubmitData) => ({ ...prev, category: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {categories.map((category: string) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          {/* 우선순위 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              우선순위
            </label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData((prev: FeedbackSubmitData) => ({ ...prev, priority: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="low">낮음</option>
              <option value="medium">보통</option>
              <option value="high">높음</option>
              <option value="critical">긴급</option>
            </select>
          </div>

          {/* 태그 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              태그
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={customTag}
                onChange={(e) => setCustomTag(e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="태그를 입력하세요"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              />
              <button
                type="button"
                onClick={addTag}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                추가
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => removeTag(tag)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* 제출 버튼 */}
          <div className="flex justify-end gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              disabled={isSubmitting}
            >
              취소
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? '제출 중...' : '피드백 제출'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// 피드백 목록 Props
interface FeedbackListProps {
  feedbacks: FeedbackData[];
  onStatusUpdate?: (feedbackId: string, status: FeedbackStatus) => void;
  onCommentAdd?: (feedbackId: string, comment: string) => void;
  isAdmin?: boolean;
  onFeedbackClick?: (feedback: FeedbackData) => void; // 상세 모달 콜백
}

// 피드백 목록
export const FeedbackList: React.FC<FeedbackListProps> = ({
  feedbacks,
  onStatusUpdate,
  onCommentAdd,
  isAdmin = false,
  onFeedbackClick
}) => {
  const [expandedFeedback, setExpandedFeedback] = useState<string | null>(null);
  const [commentText, setCommentText] = useState<Record<string, string>>({});

  const getStatusColor = (status: FeedbackStatus) => {
    switch (status) {
      case FeedbackStatus.PENDING: return 'bg-yellow-100 text-yellow-800';
      case FeedbackStatus.IN_REVIEW: return 'bg-blue-100 text-blue-800';
      case FeedbackStatus.IN_PROGRESS: return 'bg-orange-100 text-orange-800';
      case FeedbackStatus.RESOLVED: return 'bg-green-100 text-green-800';
      case FeedbackStatus.REJECTED: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeLabel = (type: FeedbackType) => {
    switch (type) {
      case FeedbackType.BUG_REPORT: return '버그 신고';
      case FeedbackType.FEATURE_REQUEST: return '기능 요청';
      case FeedbackType.IMPROVEMENT: return '개선 제안';
      case FeedbackType.QUESTION: return '질문';
      case FeedbackType.COMPLIMENT: return '칭찬';
      case FeedbackType.OTHER: return '기타';
      default: return '기타';
    }
  };

  const handleCommentSubmit = (feedbackId: string) => {
    const comment = commentText[feedbackId];
    if (comment?.trim() && onCommentAdd) {
      onCommentAdd(feedbackId, comment);
      setCommentText((prev: Record<string, string>) => ({ ...prev, [feedbackId]: '' }));
    }
  };

  return (
    <div className="space-y-4">
      {feedbacks.map((feedback: FeedbackData) => (
        <div
          key={feedback.id}
          className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => onFeedbackClick && onFeedbackClick(feedback)}
          aria-label="피드백 상세 보기"
        >
          <div className="flex justify-between items-start mb-2">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">{feedback.title}</h3>
              <p className="text-sm text-gray-600 mt-1">{feedback.description}</p>
            </div>
            <div className="flex items-center gap-2 ml-4">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(feedback.status)}`}>
                {feedback.status}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(feedback.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
            <span>타입: {getTypeLabel(feedback.type)}</span>
            <span>카테고리: {feedback.category}</span>
            <span>우선순위: {feedback.priority}</span>
          </div>

          {feedback.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {feedback.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          <div className="flex justify-between items-center">
            <button
              onClick={() => setExpandedFeedback(expandedFeedback === feedback.id ? null : feedback.id)}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              {expandedFeedback === feedback.id ? '접기' : '자세히 보기'}
            </button>

            {isAdmin && onStatusUpdate && (
              <select
                value={feedback.status}
                onChange={(e) => onStatusUpdate(feedback.id, e.target.value as FeedbackStatus)}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                {Object.values(FeedbackStatus).map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            )}
          </div>

          {expandedFeedback === feedback.id && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              {/* 댓글 목록 */}
              {feedback.metadata.comments && feedback.metadata.comments.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">댓글</h4>
                  <div className="space-y-2">
                    {feedback.metadata.comments.map((comment: any, index: number) => (
                      <div key={index} className="bg-gray-50 p-3 rounded">
                        <div className="flex justify-between items-start">
                          <span className="text-sm font-medium text-gray-900">
                            {comment.is_admin ? '관리자' : '사용자'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(comment.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mt-1">{comment.comment}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 댓글 입력 */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={commentText[feedback.id] || ''}
                  onChange={(e) => setCommentText((prev: Record<string, string>) => ({ ...prev, [feedback.id]: e.target.value }))}
                  placeholder="댓글을 입력하세요..."
                  className="flex-1 p-2 border border-gray-300 rounded-md text-sm"
                  onKeyPress={(e) => e.key === 'Enter' && handleCommentSubmit(feedback.id)}
                />
                <button
                  onClick={() => handleCommentSubmit(feedback.id)}
                  className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                >
                  댓글
                </button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// 메인 피드백 시스템 컴포넌트
export const FeedbackSystem: React.FC<FeedbackSystemProps> = ({
  userId,
  isAdmin = false,
  onFeedbackSubmit,
  onFeedbackUpdate,
  onFeedbackClick
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [feedbacks, setFeedbacks] = useState<FeedbackData[]>([]);
  const [loading, setLoading] = useState(false);

  // 피드백 목록 로드
  const loadFeedbacks = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/feedback');
      if (response.ok) {
        const data = await response.json();
        setFeedbacks(data.feedbacks || []);
      }
    } catch (error) {
      console.error('피드백 목록 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 피드백 제출
  const handleFeedbackSubmit = async (data: FeedbackSubmitData) => {
    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...data,
          user_id: userId
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (onFeedbackSubmit) {
          onFeedbackSubmit(result.feedback_id);
        }
        await loadFeedbacks(); // 목록 새로고침
      } else {
        throw new Error('피드백 제출 실패');
      }
    } catch (error) {
      console.error('피드백 제출 오류:', error);
      throw error;
    }
  };

  // 피드백 상태 업데이트
  const handleStatusUpdate = async (feedbackId: string, status: FeedbackStatus) => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });

      if (response.ok) {
        if (onFeedbackUpdate) {
          onFeedbackUpdate(feedbackId, status);
        }
        await loadFeedbacks(); // 목록 새로고침
      }
    } catch (error) {
      console.error('상태 업데이트 오류:', error);
    }
  };

  // 댓글 추가
  const handleCommentAdd = async (feedbackId: string, comment: string) => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/comment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment, is_admin: isAdmin }),
      });

      if (response.ok) {
        await loadFeedbacks(); // 목록 새로고침
      }
    } catch (error) {
      console.error('댓글 추가 오류:', error);
    }
  };

  useEffect(() => {
    loadFeedbacks();
  }, []);

  return (
    <>
      <FloatingFeedbackButton onClick={() => setIsModalOpen(true)} />
      
      <FeedbackModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleFeedbackSubmit}
      />

      {isAdmin && (
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">피드백 관리</h2>
          {loading ? (
            <div className="text-center py-8">로딩 중...</div>
          ) : (
            <FeedbackList
              feedbacks={feedbacks}
              onStatusUpdate={handleStatusUpdate}
              onCommentAdd={handleCommentAdd}
              isAdmin={isAdmin}
              onFeedbackClick={onFeedbackClick}
            />
          )}
        </div>
      )}
    </>
  );
};

export default FeedbackSystem; 