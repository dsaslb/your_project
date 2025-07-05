import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>오늘 매출</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">₩2,350,000</div>
          <div className="text-xs text-zinc-500 mt-2">전일 대비 +7.8%</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>주문 수</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">45건</div>
          <div className="text-xs text-zinc-500 mt-2">대기 8 · 완료 35 · 취소 2</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>직원 출근</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">8명</div>
          <div className="text-xs text-zinc-500 mt-2">총 15명</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>공지사항</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm">오늘 15:00 전체 회의 예정<br/>주방 위생 점검 필수</div>
        </CardContent>
      </Card>
    </div>
  );
} 