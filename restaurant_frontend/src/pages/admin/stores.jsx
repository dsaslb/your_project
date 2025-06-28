import { useAuth } from "@/context/AuthContext";

const stores = [
  { id: 1, name: "강남점", managerId: 2 },
  { id: 2, name: "홍대점", managerId: 3 },
];
const employees = [
  { id: 10, name: "김철수", storeId: 1, role: "employee" },
  { id: 11, name: "이영희", storeId: 1, role: "employee" },
  { id: 12, name: "박민수", storeId: 2, role: "employee" },
];

export default function StoreListPage() {
  const { user } = useAuth();
  if (user.role !== "admin") return <div>접근 불가</div>;
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">전체 매장 관리</h2>
      <table className="min-w-full bg-[hsl(var(--card))] rounded-xl overflow-hidden">
        <thead className="bg-[hsl(var(--muted))]">
          <tr>
            <th className="p-3 text-left">매장명</th>
            <th className="p-3 text-left">매니저</th>
            <th className="p-3 text-left">직원수</th>
          </tr>
        </thead>
        <tbody>
          {stores.map((store) => {
            const empList = employees.filter(e => e.storeId === store.id);
            return (
              <tr key={store.id} className="border-t border-[hsl(var(--border))]">
                <td className="p-3">{store.name}</td>
                <td className="p-3">
                  {empList.find(e => e.id === store.managerId)?.name || "-"}
                </td>
                <td className="p-3">{empList.length}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
} 