"use client";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AdminSettingsPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user || user.role !== "admin") {
      alert("접근 권한이 없습니다!");
      router.replace("/dashboard");
    }
  }, [user, router]);

  if (!user || user.role !== "admin") return null;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">시스템 설정 (관리자 전용)</h2>
      {/* 설정 폼/컴포넌트 */}
      <p>여기에 시스템 전체 설정 폼/컴포넌트를 추가하세요.</p>
    </div>
  );
} 