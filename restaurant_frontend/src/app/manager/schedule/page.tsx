"use client";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ManagerSchedulePage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user || (user.role !== "manager" && user.role !== "admin")) {
      alert("접근 권한이 없습니다!");
      router.replace("/dashboard");
    }
  }, [user, router]);

  if (!user || (user.role !== "manager" && user.role !== "admin")) return null;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">근무표 관리 (매장 관리자/관리자 전용)</h2>
      {/* 근무표 관리 컴포넌트 */}
      <p>여기에 근무표 관리 기능을 추가하세요.</p>
    </div>
  );
} 