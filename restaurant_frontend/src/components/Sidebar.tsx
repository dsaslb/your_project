"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser } from "./UserContext";
import { ChevronLeft, ChevronRight } from "lucide-react";

export interface SidebarMenuItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
}

export default function Sidebar({ menu }: { menu: SidebarMenuItem[] }) {
  const pathname = usePathname();
  const { user, logout } = useUser();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside className={`min-h-screen bg-zinc-900 text-white flex flex-col border-r border-zinc-800 transition-all duration-300 ${
      isCollapsed ? "w-16" : "w-64"
    }`}>
      <div className={`h-16 flex items-center justify-between border-b border-zinc-800 px-4 ${
        isCollapsed ? "justify-center" : "px-6"
      }`}>
        {!isCollapsed && (
          <div className="font-bold text-xl">매장관리</div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 hover:bg-zinc-800 rounded transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>
      
      <nav className="flex-1 py-4">
        {menu.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-2 px-6 py-3 hover:bg-zinc-800 transition ${
              pathname === item.href ? "bg-zinc-800 font-bold" : ""
            } ${isCollapsed ? "justify-center px-2" : ""}`}
            title={isCollapsed ? item.label : ""}
          >
            <div className="flex-shrink-0">
              {item.icon}
            </div>
            {!isCollapsed && (
              <span className="truncate">{item.label}</span>
            )}
          </Link>
        ))}
      </nav>
      
      <div className={`p-4 border-t border-zinc-800 ${isCollapsed ? "px-2" : ""}`}>
        {user ? (
          <button 
            onClick={logout} 
            className={`w-full bg-zinc-700 hover:bg-zinc-600 text-white py-2 rounded transition-colors ${
              isCollapsed ? "px-2" : ""
            }`}
            title={isCollapsed ? "로그아웃" : ""}
          >
            {!isCollapsed && "로그아웃"}
          </button>
        ) : null}
      </div>
    </aside>
  );
}
