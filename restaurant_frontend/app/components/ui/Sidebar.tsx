import Link from "next/link";

export function Sidebar() {
  return (
    <aside className="w-60 h-screen bg-[hsl(var(--sidebar-background))] text-[hsl(var(--sidebar-foreground))] border-r border-[hsl(var(--sidebar-border))] flex flex-col">
      <div className="p-6 font-bold text-xl">관리자 시스템</div>
      <nav className="flex-1 flex flex-col gap-2 px-4">
        <Link href="/dashboard" className="py-2 px-3 rounded hover:bg-[hsl(var(--sidebar-accent))]">대시보드</Link>
        <Link href="/schedule" className="py-2 px-3 rounded hover:bg-[hsl(var(--sidebar-accent))]">스케줄</Link>
        <Link href="/employees" className="py-2 px-3 rounded hover:bg-[hsl(var(--sidebar-accent))]">직원관리</Link>
        {/* 필요에 따라 메뉴 추가 */}
      </nav>
    </aside>
  );
} 