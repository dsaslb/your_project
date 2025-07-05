"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Calendar, Clock, User, MapPin, FileText, Save, X } from "lucide-react";

interface Staff {
  id: number;
  name: string;
  position: string;
  phone: string;
}

interface ScheduleForm {
  staff_id: number;
  date: string;
  start_time: string;
  end_time: string;
  type: string;
  location: string;
  memo: string;
}

export default function ScheduleAddPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [formData, setFormData] = useState<ScheduleForm>({
    staff_id: 0,
    date: new Date().toISOString().split('T')[0],
    start_time: "09:00",
    end_time: "17:00",
    type: "근무",
    location: "홀",
    memo: ""
  });

  // 더미 직원 데이터
  const dummyStaff = [
    { id: 1, name: "김철수", position: "주방장", phone: "010-1234-5678" },
    { id: 2, name: "이영희", position: "서빙", phone: "010-2345-6789" },
    { id: 3, name: "박민수", position: "카운터", phone: "010-3456-7890" },
    { id: 4, name: "최지영", position: "서빙", phone: "010-4567-8901" },
    { id: 5, name: "정현우", position: "부주방장", phone: "010-5678-9012" },
    { id: 6, name: "한소영", position: "서빙", phone: "010-6789-0123" },
    { id: 7, name: "강동현", position: "카운터", phone: "010-7890-1234" },
    { id: 8, name: "윤미영", position: "서빙", phone: "010-8901-2345" },
    { id: 9, name: "임태호", position: "주방보조", phone: "010-9012-3456" },
    { id: 10, name: "송은지", position: "서빙", phone: "010-0123-4567" }
  ];

  useEffect(() => {
    setStaffList(dummyStaff);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('/api/schedule', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_id: formData.staff_id,
          date: formData.date,
          start_time: formData.start_time,
          end_time: formData.end_time,
          type: "work",
          category: formData.type,
          memo: formData.memo,
          team: formData.location,
          branch_id: 1, // 기본값
          manager_id: 1 // 기본값
        })
      });

      const result = await response.json();

      if (result.success) {
        alert("스케줄이 성공적으로 추가되었습니다.");
        router.push('/schedule');
      } else {
        alert(result.message || "스케줄 추가 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error('Error adding schedule:', error);
      alert("스케줄 추가 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  const selectedStaff = staffList.find(staff => staff.id === formData.staff_id);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </button>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">스케줄 추가</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            새로운 근무 스케줄을 추가합니다.
          </p>
        </div>

        {/* Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 직원 선택 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <User className="inline h-4 w-4 mr-2" />
                직원 선택
              </label>
              <select
                name="staff_id"
                value={formData.staff_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              >
                <option value={0}>직원을 선택하세요</option>
                {staffList.map(staff => (
                  <option key={staff.id} value={staff.id}>
                    {staff.name} ({staff.position})
                  </option>
                ))}
              </select>
              {selectedStaff && (
                <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    <strong>{selectedStaff.name}</strong> - {selectedStaff.position}
                  </p>
                  <p className="text-xs text-blue-600 dark:text-blue-400">
                    연락처: {selectedStaff.phone}
                  </p>
                </div>
              )}
            </div>

            {/* 날짜 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Calendar className="inline h-4 w-4 mr-2" />
                근무 날짜
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>

            {/* 시간 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Clock className="inline h-4 w-4 mr-2" />
                  시작 시간
                </label>
                <input
                  type="time"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Clock className="inline h-4 w-4 mr-2" />
                  종료 시간
                </label>
                <input
                  type="time"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
            </div>

            {/* 근무 유형 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                근무 유형
              </label>
              <select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              >
                <option value="근무">일반 근무</option>
                <option value="오픈">오픈</option>
                <option value="마감">마감</option>
                <option value="청소">청소</option>
                <option value="특별근무">특별근무</option>
              </select>
            </div>

            {/* 근무 위치 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <MapPin className="inline h-4 w-4 mr-2" />
                근무 위치
              </label>
              <select
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              >
                <option value="홀">홀</option>
                <option value="주방">주방</option>
                <option value="카운터">카운터</option>
                <option value="창고">창고</option>
                <option value="전체">전체</option>
              </select>
            </div>

            {/* 메모 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <FileText className="inline h-4 w-4 mr-2" />
                메모
              </label>
              <textarea
                name="memo"
                value={formData.memo}
                onChange={handleInputChange}
                rows={4}
                placeholder="스케줄에 대한 추가 정보나 특이사항을 입력하세요..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
              />
            </div>

            {/* 근무 시간 계산 */}
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                근무 시간 정보
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 dark:text-gray-400">총 근무시간:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-white">
                    {(() => {
                      const start = new Date(`2000-01-01T${formData.start_time}`);
                      const end = new Date(`2000-01-01T${formData.end_time}`);
                      const diffMs = end.getTime() - start.getTime();
                      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
                      const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                      return `${diffHours}시간 ${diffMinutes}분`;
                    })()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">근무일:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-white">
                    {new Date(formData.date).toLocaleDateString('ko-KR', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </span>
                </div>
              </div>
            </div>

            {/* 버튼 */}
            <div className="flex gap-4 pt-6">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    저장 중...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    스케줄 저장
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
              >
                <X className="h-4 w-4" />
                취소
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 