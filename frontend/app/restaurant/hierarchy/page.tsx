"use client";
import useUserStore from '@/store/useUserStore';

export default function RestaurantHierarchyPage() {
  const { user } = useUserStore();
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">레스토랑 계층 구조</h1>
      <p>현재 역할: <b>{user?.role}</b></p>
      <div className="mt-4">(여기에 계층 구조 UI가 들어갈 예정입니다)</div>
    </div>
  );
} 