"use client";
import { useState, useEffect } from "react";
import {
  Shield,
  Users,
  Building2,
  Settings,
  Check,
  X,
  Edit,
  Save,
  Lock,
  Unlock,
  Eye,
  EyeOff,
} from "lucide-react";

interface Permission {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
}

interface User {
  id: string;
  username: string;
  role: string;
  branch_id: number;
  permissions: string[];
}

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [selectedUser, setSelectedUser] = useState<string>("");
  const [isLoaded, setIsLoaded] = useState(false);
  const [editingRole, setEditingRole] = useState<string>("");

  useEffect(() => {
    loadPermissionsData();
  }, []);

  const loadPermissionsData = async () => {
    // 실제로는 API 호출
    const mockPermissions: Permission[] = [
      // 직원 관리 권한
      { id: "staff_view", name: "직원 조회", description: "직원 목록 및 정보 조회", category: "직원 관리", enabled: true },
      { id: "staff_create", name: "직원 등록", description: "새 직원 등록 및 계정 생성", category: "직원 관리", enabled: true },
      { id: "staff_edit", name: "직원 수정", description: "직원 정보 수정", category: "직원 관리", enabled: true },
      { id: "staff_delete", name: "직원 삭제", description: "직원 계정 삭제", category: "직원 관리", enabled: false },
      { id: "staff_approve", name: "직원 승인", description: "신규 직원 승인", category: "직원 관리", enabled: true },

      // 스케줄 관리 권한
      { id: "schedule_view", name: "스케줄 조회", description: "근무 스케줄 조회", category: "스케줄 관리", enabled: true },
      { id: "schedule_create", name: "스케줄 생성", description: "새 스케줄 생성", category: "스케줄 관리", enabled: true },
      { id: "schedule_edit", name: "스케줄 수정", description: "기존 스케줄 수정", category: "스케줄 관리", enabled: true },
      { id: "schedule_delete", name: "스케줄 삭제", description: "스케줄 삭제", category: "스케줄 관리", enabled: false },

      // 재고 관리 권한
      { id: "inventory_view", name: "재고 조회", description: "재고 현황 조회", category: "재고 관리", enabled: true },
      { id: "inventory_edit", name: "재고 수정", description: "재고 수량 수정", category: "재고 관리", enabled: true },
      { id: "inventory_order", name: "발주 관리", description: "재료 발주 및 관리", category: "재고 관리", enabled: true },

      // 매장 관리 권한
      { id: "branch_view", name: "매장 조회", description: "매장 정보 조회", category: "매장 관리", enabled: true },
      { id: "branch_edit", name: "매장 수정", description: "매장 정보 수정", category: "매장 관리", enabled: false },
      { id: "branch_create", name: "매장 생성", description: "새 매장 등록", category: "매장 관리", enabled: false },

      // 시스템 관리 권한
      { id: "system_settings", name: "시스템 설정", description: "시스템 설정 변경", category: "시스템 관리", enabled: false },
      { id: "system_backup", name: "백업 관리", description: "데이터 백업 및 복원", category: "시스템 관리", enabled: false },
      { id: "system_logs", name: "로그 조회", description: "시스템 로그 조회", category: "시스템 관리", enabled: false },

      // 보고서 권한
      { id: "reports_view", name: "보고서 조회", description: "통계 및 보고서 조회", category: "보고서", enabled: true },
      { id: "reports_export", name: "보고서 내보내기", description: "보고서 파일 다운로드", category: "보고서", enabled: true },
      { id: "reports_create", name: "보고서 생성", description: "새 보고서 생성", category: "보고서", enabled: false },
    ];

    const mockRoles: Role[] = [
      {
        id: "brand_admin",
        name: "브랜드 관리자",
        description: "전체 브랜드 관리 권한",
        permissions: ["staff_view", "staff_create", "staff_edit", "staff_approve", "schedule_view", "schedule_create", "schedule_edit", "inventory_view", "inventory_edit", "inventory_order", "branch_view", "reports_view", "reports_export"],
      },
      {
        id: "branch_manager",
        name: "매장 관리자",
        description: "개별 매장 관리 권한",
        permissions: ["staff_view", "staff_create", "staff_edit", "schedule_view", "schedule_create", "schedule_edit", "inventory_view", "inventory_edit", "inventory_order", "reports_view"],
      },
      {
        id: "staff_manager",
        name: "직원 관리자",
        description: "직원 관리 전담",
        permissions: ["staff_view", "staff_create", "staff_edit", "staff_approve", "schedule_view"],
      },
      {
        id: "inventory_manager",
        name: "재고 관리자",
        description: "재고 관리 전담",
        permissions: ["inventory_view", "inventory_edit", "inventory_order"],
      },
    ];

    const mockUsers: User[] = [
      { id: "1", username: "admin", role: "brand_admin", branch_id: 1, permissions: ["staff_view", "staff_create", "staff_edit", "staff_approve", "schedule_view", "schedule_create", "schedule_edit", "inventory_view", "inventory_edit", "inventory_order", "branch_view", "reports_view", "reports_export"] },
      { id: "2", username: "admin_branch_1", role: "branch_manager", branch_id: 1, permissions: ["staff_view", "staff_create", "staff_edit", "schedule_view", "schedule_create", "schedule_edit", "inventory_view", "inventory_edit", "inventory_order", "reports_view"] },
      { id: "3", username: "admin_branch_2", role: "branch_manager", branch_id: 2, permissions: ["staff_view", "staff_create", "staff_edit", "schedule_view", "schedule_create", "schedule_edit", "inventory_view", "inventory_edit", "inventory_order", "reports_view"] },
    ];

    setPermissions(mockPermissions);
    setRoles(mockRoles);
    setUsers(mockUsers);
    setIsLoaded(true);
  };

  const togglePermission = (permissionId: string) => {
    setPermissions(permissions.map(p => 
      p.id === permissionId ? { ...p, enabled: !p.enabled } : p
    ));
  };

  const updateRolePermissions = (roleId: string, permissionIds: string[]) => {
    setRoles(roles.map(role => 
      role.id === roleId ? { ...role, permissions: permissionIds } : role
    ));
  };

  const updateUserPermissions = (userId: string, permissionIds: string[]) => {
    setUsers(users.map(user => 
      user.id === userId ? { ...user, permissions: permissionIds } : user
    ));
  };

  const getPermissionById = (id: string) => {
    return permissions.find(p => p.id === id);
  };

  const getRoleById = (id: string) => {
    return roles.find(r => r.id === id);
  };

  const getUserById = (id: string) => {
    return users.find(u => u.id === id);
  };

  const getPermissionsByCategory = () => {
    const categories = [...new Set(permissions.map(p => p.category))];
    return categories.map(category => ({
      category,
      permissions: permissions.filter(p => p.category === category)
    }));
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">권한 데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">권한 관리</h1>
        <p className="text-gray-600 mt-2">브랜드 관리자 권한 세분화 및 관리</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 권한 목록 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">권한 목록</h3>
          <div className="space-y-4">
            {getPermissionsByCategory().map(({ category, permissions: categoryPermissions }) => (
              <div key={category} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">{category}</h4>
                <div className="space-y-2">
                  {categoryPermissions.map((permission) => (
                    <div key={permission.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <Shield className="h-4 w-4 text-gray-400" />
                          <span className="text-sm font-medium text-gray-900">{permission.name}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{permission.description}</p>
                      </div>
                      <button
                        onClick={() => togglePermission(permission.id)}
                        className={`p-1 rounded ${
                          permission.enabled 
                            ? "text-green-600 hover:text-green-700" 
                            : "text-red-600 hover:text-red-700"
                        }`}
                      >
                        {permission.enabled ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 역할 관리 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">역할 관리</h3>
          <div className="space-y-4">
            {roles.map((role) => (
              <div key={role.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-medium text-gray-900">{role.name}</h4>
                    <p className="text-sm text-gray-500">{role.description}</p>
                  </div>
                  <button
                    onClick={() => setEditingRole(editingRole === role.id ? "" : role.id)}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                </div>
                
                {editingRole === role.id ? (
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600 mb-2">권한 설정:</div>
                    {permissions.map((permission) => (
                      <label key={permission.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={role.permissions.includes(permission.id)}
                          onChange={(e) => {
                            const newPermissions = e.target.checked
                              ? [...role.permissions, permission.id]
                              : role.permissions.filter(p => p !== permission.id);
                            updateRolePermissions(role.id, newPermissions);
                          }}
                          className="rounded border-gray-300"
                        />
                        <span className="text-sm text-gray-700">{permission.name}</span>
                      </label>
                    ))}
                    <div className="flex space-x-2 mt-3">
                      <button
                        onClick={() => setEditingRole("")}
                        className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                      >
                        취소
                      </button>
                      <button
                        onClick={() => setEditingRole("")}
                        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        저장
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-1">
                    {role.permissions.slice(0, 3).map((permissionId) => {
                      const permission = getPermissionById(permissionId);
                      return permission ? (
                        <span key={permissionId} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                          {permission.name}
                        </span>
                      ) : null;
                    })}
                    {role.permissions.length > 3 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                        +{role.permissions.length - 3}개 더
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 사용자 권한 관리 */}
      <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">사용자 권한 관리</h3>
        <div className="space-y-4">
          {users.map((user) => (
            <div key={user.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-medium text-gray-900">{user.username}</h4>
                  <p className="text-sm text-gray-500">
                    역할: {getRoleById(user.role)?.name || user.role} | 
                    매장: {user.branch_id}번
                  </p>
                </div>
                <button
                  onClick={() => setSelectedUser(selectedUser === user.id ? "" : user.id)}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  {selectedUser === user.id ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              
              {selectedUser === user.id && (
                <div className="space-y-2">
                  <div className="text-sm text-gray-600 mb-2">개별 권한 설정:</div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {permissions.map((permission) => (
                      <label key={permission.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={user.permissions.includes(permission.id)}
                          onChange={(e) => {
                            const newPermissions = e.target.checked
                              ? [...user.permissions, permission.id]
                              : user.permissions.filter(p => p !== permission.id);
                            updateUserPermissions(user.id, newPermissions);
                          }}
                          className="rounded border-gray-300"
                        />
                        <span className="text-sm text-gray-700">{permission.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 