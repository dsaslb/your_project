import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function AdminSettingsPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user.role !== "admin") {
      alert("접근 권한이 없습니다!");
      router.replace("/dashboard");
    }
  }, [user, router]);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">시스템 설정</h2>
      {/* 설정 폼/컴포넌트 */}
    </div>
  );
} 