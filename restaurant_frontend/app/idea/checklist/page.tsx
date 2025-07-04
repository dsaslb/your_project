"use client";
import React, { useState } from "react";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useNotifications } from "@/components/NotificationSystem";

const steps = [
  "출근", "청소", "주문", "조리", "서빙", "계산", "테이블 정리"
];

export default function ChecklistPage() {
  const [checked, setChecked] = useState(Array(steps.length).fill(false));
  const { addNotification } = useNotifications();

  const handleCheck = (idx: number) => {
    const newChecked = [...checked];
    newChecked[idx] = !newChecked[idx];
    setChecked(newChecked);
    if (newChecked[idx]) {
      addNotification({
        id: Date.now(),
        title: `${steps[idx]} 완료!`,
        content: `${steps[idx]} 단계가 완료되었습니다.`,
        category: 'success',
        priority: '일반',
        is_read: false,
        created_at: new Date().toISOString(),
      });
    }
  };

  // 미완료 경고(예시: 마지막 단계 미완료시)
  const handleSubmit = () => {
    if (checked.every(Boolean)) {
      addNotification({
        id: Date.now(),
        title: "업무 체크리스트 완료",
        content: "모든 단계를 완료했습니다!",
        category: 'success',
        priority: '일반',
        is_read: false,
        created_at: new Date().toISOString(),
      });
    } else {
      addNotification({
        id: Date.now(),
        title: "미완료 경고",
        content: "아직 완료되지 않은 단계가 있습니다. 관리자에게 알림이 전송됩니다.",
        category: 'warning',
        priority: '중요',
        is_read: false,
        created_at: new Date().toISOString(),
      });
    }
  };

  const progress = (checked.filter(Boolean).length / steps.length) * 100;

  return (
    <div className="max-w-md mx-auto p-4 bg-white dark:bg-gray-900 rounded-lg shadow mt-4">
      <h2 className="text-xl font-bold mb-2">직원 업무 체크리스트</h2>
      <Progress value={progress} className="mb-4" />
      <ul className="space-y-2">
        {steps.map((step, idx) => (
          <li key={step} className="flex items-center justify-between">
            <span>{step}</span>
            <Button
              size="sm"
              variant={checked[idx] ? "success" : "outline"}
              onClick={() => handleCheck(idx)}
              className="ml-2"
            >
              {checked[idx] ? <Badge variant="success">완료</Badge> : "체크"}
            </Button>
          </li>
        ))}
      </ul>
      <Button className="w-full mt-6" onClick={handleSubmit}>
        전체 완료 제출
      </Button>
    </div>
  );
} 