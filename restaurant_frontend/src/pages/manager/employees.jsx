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

export default function ManagerEmployeesPage() {
  const { user } = useAuth();
  // 본인이 관리하는 매장 찾기
  const myStore = stores.find(s => s.managerId === user.id);
  if (!myStore) return <div>관리 매장이 없습니다</div>;
  const myEmployees = employees.filter(e => e.storeId === myStore.id);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">
        {myStore.name} 직원 목록
      </h2>
      <ul>
        {myEmployees.map(e => (
          <li key={e.id}>
            {e.name} ({e.role})
          </li>
        ))}
      </ul>
    </div>
  );
} 