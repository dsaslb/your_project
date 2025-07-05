import DashboardLayout from "@/components/layouts/DashboardLayout";
import StatCard from "@/components/widgets/StatCard";
import { Bell } from "lucide-react";

const notifications = [
  { time: "09:10", message: "발주 #ORD-002 대기 중" },
  { time: "10:30", message: "재고 부족: 쌀" },
  { time: "11:00", message: "직원 출근: 이영희" },
];

export default function NotificationsPage() {
  return (
    <DashboardLayout title="알림/공지" description="최근 알림 및 공지사항을 확인하세요.">
      <StatCard title="알림 수" value={notifications.length + "건"} icon={<Bell />} />
      <div className="col-span-3 bg-white dark:bg-zinc-900 rounded-lg p-4 shadow">
        <div className="font-bold mb-2">알림 목록</div>
        <ul className="space-y-1">
          {notifications.map((n, i) => (
            <li key={i} className="flex justify-between border-b last:border-none py-1">
              <span>{n.time}</span>
              <span className="flex-1 ml-2">{n.message}</span>
            </li>
          ))}
        </ul>
      </div>
    </DashboardLayout>
  );
} 