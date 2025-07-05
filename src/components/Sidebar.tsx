import { Card } from "./card";
import { Button } from "./button";
import { Home, Users, ClipboardList, ShoppingCart, Boxes, Calendar, Settings } from "lucide-react";
import Link from "next/link";

const menu = [
  { label: "대시보드", icon: <Home size={18} />, href: "/dashboard" },
  { label: "직원 관리", icon: <Users size={18} />, href: "/staff" },
  { label: "발주 관리", icon: <ClipboardList size={18} />, href: "/orders" },
  { label: "재고 관리", icon: <Boxes size={18} />, href: "/inventory" },
  { label: "스케줄", icon: <Calendar size={18} />, href: "/schedule" },
  { label: "설정", icon: <Settings size={18} />, href: "/settings" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 min-h-screen bg-white dark:bg-zinc-900 border-r flex flex-col p-4">
      <Card className="mb-6 p-4 flex flex-col items-center">
        <div className="font-bold text-lg mb-2">맛있는집</div>
        <div className="text-xs text-zinc-500 dark:text-zinc-400">매장 관리 시스템</div>
      </Card>
      <nav className="flex flex-col gap-2">
        {menu.map((item) => (
          <Link href={item.href} key={item.label} legacyBehavior>
            <a className="flex items-center gap-3 px-3 py-2 rounded hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
              {item.icon}
              <span className="text-sm font-medium">{item.label}</span>
            </a>
          </Link>
        ))}
      </nav>
      <div className="flex-1" />
      <div className="mt-6 text-xs text-zinc-400 text-center">© 2025 맛있는집</div>
    </aside>
  );
} 