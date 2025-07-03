"use client";
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useNotifications } from "@/components/NotificationSystem";

const qscItems = [
  { category: "위생", items: ["손씻기", "유니폼", "주방 청결"] },
  { category: "서비스", items: ["인사", "응대", "친절"] },
  { category: "제품 품질", items: ["조리상태", "온도", "맛"] }
];

export default function QSCPage() {
  const [checked, setChecked] = useState(
    qscItems.map(cat => cat.items.map(() => false))
  );
  const { addNotification } = useNotifications();

  const handleCheck = (catIdx: number, itemIdx: number) => {
    const newChecked = checked.map(arr => [...arr]);
    newChecked[catIdx][itemIdx] = !newChecked[catIdx][itemIdx];
    setChecked(newChecked);
    if (newChecked[catIdx][itemIdx]) {
      addNotification({
        type: "success",
        title: `${qscItems[catIdx].category} - ${qscItems[catIdx].items[itemIdx]} 점검 완료!`,
        message: "점검이 완료되었습니다."
      });
    }
  };

  const handleSubmit = () => {
    const allChecked = checked.flat().every(Boolean);
    if (allChecked) {
      addNotification({
        type: "success",
        title: "QSC 점검 완료",
        message: "모든 항목 점검이 완료되었습니다!"
      });
    } else {
      addNotification({
        type: "warning",
        title: "QSC 미흡 경고",
        message: "미점검 항목이 있습니다. 관리자에게 알림이 전송됩니다."
      });
    }
  };

  const progress = (checked.flat().filter(Boolean).length / checked.flat().length) * 100;

  return (
    <div className="max-w-lg mx-auto p-4 bg-white dark:bg-gray-900 rounded-lg shadow mt-4">
      <h2 className="text-xl font-bold mb-2">QSC 점검 체크리스트</h2>
      <Progress value={progress} className="mb-4" />
      {qscItems.map((cat, catIdx) => (
        <Card key={cat.category} className="mb-2">
          <CardHeader>
            <CardTitle>{cat.category}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {cat.items.map((item, itemIdx) => (
                <li key={item} className="flex items-center justify-between">
                  <span>{item}</span>
                  <Button
                    size="sm"
                    variant={checked[catIdx][itemIdx] ? "success" : "outline"}
                    onClick={() => handleCheck(catIdx, itemIdx)}
                  >
                    {checked[catIdx][itemIdx] ? <Badge variant="success">완료</Badge> : "체크"}
                  </Button>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ))}
      <Button className="w-full mt-6" onClick={handleSubmit}>
        전체 점검 제출
      </Button>
    </div>
  );
}
