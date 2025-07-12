"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Package, DollarSign, Building, Save, X, AlertTriangle } from "lucide-react";

interface InventoryForm {
  name: string;
  category: string;
  currentStock: number;
  minStock: number;
  unit: string;
  price: number;
  supplier: string;
  description: string;
}

export default function InventoryAddPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<InventoryForm>({
    name: "",
    category: "",
    currentStock: 0,
    minStock: 0,
    unit: "",
    price: 0,
    supplier: "",
    description: ""
  });

  const categories = [
    "육류", "채소", "반찬", "곡물", "조미료", "유제품", "음료", "기타"
  ];

  const units = [
    "kg", "g", "L", "ml", "개", "봉", "박스", "팩", "병", "캔"
  ];

  const suppliers = [
    "한우공급업체", "돈육공급업체", "닭고기공급업체", "채소공급업체", 
    "김치공급업체", "쌀공급업체", "조미료공급업체", "유제품공급업체",
    "음료공급업체", "기타공급업체"
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'currentStock' || name === 'minStock' || name === 'price' ? parseFloat(value) || 0 : value
    }));
  };

  const calculateStatus = () => {
    if (formData.currentStock === 0 || formData.minStock === 0) return "부족";
    const ratio = formData.currentStock / formData.minStock;
    if (ratio < 0.8) return "부족";
    if (ratio < 1.2) return "위험";
    return "충분";
  };

  const calculateTotalValue = () => {
    return formData.currentStock * formData.price;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('/api/inventory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: formData.name,
          category: formData.category,
          current_stock: formData.currentStock,
          min_stock: formData.minStock,
          unit: formData.unit,
          price: formData.price,
          supplier: formData.supplier,
          description: formData.description,
          status: calculateStatus()
        })
      });

      const result = await response.json();

      if (result.success) {
        alert("품목이 성공적으로 추가되었습니다.");
        router.push('/inventory');
      } else {
        alert(result.message || "품목 추가 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error('Error adding inventory item:', error);
      alert("품목 추가 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  const status = calculateStatus();
  const totalValue = calculateTotalValue();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </button>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">품목 추가</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            새로운 재고 품목을 추가합니다.
          </p>
        </div>

        {/* Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 기본 정보 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Package className="inline h-4 w-4 mr-2" />
                  품목명
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="품목명을 입력하세요"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  카테고리
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  required
                >
                  <option value="">카테고리를 선택하세요</option>
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* 재고 정보 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  현재 재고
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    name="currentStock"
                    value={formData.currentStock}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  />
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleInputChange}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  >
                    <option value="">단위</option>
                    {units.map(unit => (
                      <option key={unit} value={unit}>{unit}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  최소 재고
                </label>
                <input
                  type="number"
                  name="minStock"
                  value={formData.minStock}
                  onChange={handleInputChange}
                  min="0"
                  step="0.01"
                  placeholder="최소 재고량"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <DollarSign className="inline h-4 w-4 mr-2" />
                  단가
                </label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleInputChange}
                  min="0"
                  step="1"
                  placeholder="단가"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
            </div>

            {/* 공급업체 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Building className="inline h-4 w-4 mr-2" />
                공급업체
              </label>
              <select
                name="supplier"
                value={formData.supplier}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              >
                <option value="">공급업체를 선택하세요</option>
                {suppliers.map(supplier => (
                  <option key={supplier} value={supplier}>{supplier}</option>
                ))}
              </select>
            </div>

            {/* 설명 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                설명
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                placeholder="품목에 대한 추가 설명을 입력하세요..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
              />
            </div>

            {/* 재고 상태 및 가치 정보 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  재고 상태
                </h3>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                  status === "부족" ? "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400" :
                  status === "위험" ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400" :
                  "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                }`}>
                  {status === "부족" && <AlertTriangle className="h-3 w-3 mr-1" />}
                  {status}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  재고 비율
                </h3>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {formData.minStock > 0 ? Math.round((formData.currentStock / formData.minStock) * 100) : 0}%
                </p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  총 재고가치
                </h3>
                <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                  ₩{totalValue.toLocaleString()}
                </p>
              </div>
            </div>

            {/* 재고 부족 경고 */}
            {status === "부족" && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <div className="flex items-center">
                  <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 mr-2" />
                  <span className="text-red-800 dark:text-red-200 font-medium">
                    재고가 부족합니다. 발주를 고려해주세요.
                  </span>
                </div>
              </div>
            )}

            {/* 버튼 */}
            <div className="flex gap-4 pt-6">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    추가 중...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    품목 추가
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
              >
                <X className="h-4 w-4" />
                취소
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 