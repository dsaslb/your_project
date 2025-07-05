"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/components/UserContext";

const dummyUsers = [
  { id: "admin", pw: "admin123", approved: true },
  { id: "manager", pw: "manager123", approved: true },
  { id: "waituser", pw: "wait123", approved: false },
];

export default function LoginPage() {
  const [id, setId] = useState("");
  const [pw, setPw] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();
  const { login } = useUser();

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    const user = dummyUsers.find(u => u.id === id && u.pw === pw);
    if (!user) {
      setError("아이디 또는 비밀번호가 올바르지 않습니다.");
      return;
    }
    if (!user.approved) {
      setError("가입 승인 대기 중입니다. 관리자 승인 후 로그인 가능합니다.");
      return;
    }
    login({ id: user.id });
    router.replace("/dashboard");
  }

  function handleSocialLogin(provider: string) {
    alert(`${provider} 소셜 로그인은 추후 연동 예정입니다.`);
  }

  function handleSignup() {
    alert("회원가입 신청이 접수되었습니다. 관리자 승인 후 로그인 가능합니다.");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-zinc-100 to-zinc-300 dark:from-zinc-900 dark:to-zinc-800">
      <div className="w-full max-w-md bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8">
        <h1 className="text-2xl font-bold mb-6 text-center">매장 관리 시스템 로그인</h1>
        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="text"
            placeholder="아이디"
            value={id}
            onChange={e => setId(e.target.value)}
            className="w-full px-4 py-2 rounded border bg-zinc-50 dark:bg-zinc-800 focus:outline-none"
            autoFocus
          />
          <input
            type="password"
            placeholder="비밀번호"
            value={pw}
            onChange={e => setPw(e.target.value)}
            className="w-full px-4 py-2 rounded border bg-zinc-50 dark:bg-zinc-800 focus:outline-none"
          />
          {error && <div className="text-red-500 text-sm text-center">{error}</div>}
          <button type="submit" className="w-full bg-black text-white py-2 rounded font-bold hover:bg-zinc-800 transition">로그인</button>
        </form>
        <div className="flex flex-col gap-2 mt-6">
          <button onClick={() => handleSocialLogin("네이버")}
            className="w-full bg-green-500 text-white py-2 rounded font-bold hover:bg-green-600 transition">네이버로 로그인</button>
          <button onClick={() => handleSocialLogin("구글")}
            className="w-full bg-blue-500 text-white py-2 rounded font-bold hover:bg-blue-600 transition">구글(지메일)로 로그인</button>
        </div>
        <div className="mt-6 text-center">
          <button onClick={handleSignup} className="text-sm text-zinc-500 hover:underline">회원가입 신청</button>
        </div>
        <div className="mt-4 text-xs text-zinc-400 text-center">예시 계정: admin/admin123, manager/manager123</div>
      </div>
    </div>
  );
} 