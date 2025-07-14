"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Database, Download } from "lucide-react";
import { toast } from "sonner";

const TestDataGenerator: React.FC = () => {
  const [days, setDays] = useState(30);
  const [generating, setGenerating] = useState(false);

  const generateTestData = async () => {
    try {
      setGenerating(true);
      
      const response = await fetch('/api/attendance/test-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          days: days
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success(data.message);
      } else {
        toast.error(data.error || '테스트 데이터 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('테스트 데이터 생성 오류:', error);
      toast.error('테스트 데이터 생성 중 오류가 발생했습니다.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="w-5 h-5" />
          테스트 데이터 생성
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Label htmlFor="days">생성할 일수</Label>
            <Input
              id="days"
              type="number"
              min="1"
              max="365"
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value) || 30)}
              placeholder="30"
            />
            <p className="text-sm text-gray-500 mt-1">
              지정한 일수만큼의 출퇴근 기록을 생성합니다.
            </p>
          </div>
          
          <Button 
            onClick={generateTestData} 
            disabled={generating}
            className="w-full"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                생성 중...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                테스트 데이터 생성
              </>
            )}
          </Button>
          
          <div className="text-xs text-gray-500">
            <p>• 모든 직원에 대해 랜덤한 출퇴근 시간이 생성됩니다.</p>
            <p>• 지각, 조퇴, 초과근무 상황이 포함됩니다.</p>
            <p>• 이미 기록이 있는 날짜는 건너뜁니다.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TestDataGenerator; 