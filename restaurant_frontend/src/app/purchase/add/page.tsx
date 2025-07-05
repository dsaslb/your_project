"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Package, Calendar, User, DollarSign, FileText, Save, X, Building } from "lucide-react";

interface Material {
  id: number;
  name: string;
  category: string;
  unit: string;
  price_per_unit: number;
  supplier: string;
  description: string;
}

interface PurchaseForm {
  item: string;
  quantity: number;
  unit: string;
  supplier: string;
  detail: string;
  memo: string;
  order_date: string;
  estimated_cost: number;
}

export default function PurchaseAddPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [materialList, setMaterialList] = useState<Material[]>([]);
  const [formData, setFormData] = useState<PurchaseForm>({
    item: "",
    quantity: 1,
    unit: "",
    supplier: "",
    detail: "",
    memo: "",
    order_date: new Date().toISOString().split('T')[0],
    estimated_cost: 0
  });

  // 더미 재료 데이터
  const dummyMaterials = [
    { id: 1, name: "소고기", category: "육류", unit: "kg", price_per_unit: 45000, supplier: "한우공급업체", description: "한우 등급 소고기" },
    { id: 2, name: "돼지고기", category: "육류", unit: "kg", price_per_unit: 28000, supplier: "돈육공급업체", description: "삼겹살용 돼지고기" },
    { id: 3, name: "닭고기", category: "육류", unit: "kg", price_per_unit: 15000, supplier: "닭고기공급업체", description: "신선한 닭고기" },
    { id: 4, name: "양파", category: "채소", unit: "kg", price_per_unit: 3000, supplier: "채소공급업체", description: "신선한 양파" },
    { id: 5, name: "당근", category: "채소", unit: "kg", price_per_unit: 2500, supplier: "채소공급업체", description: "신선한 당근" },
    { id: 6, name: "김치", category: "반찬", unit: "kg", price_per_unit: 8000, supplier: "김치공급업체", description: "맛김치" },
    { id: 7, name: "쌀", category: "곡물", unit: "kg", price_per_unit: 4500, supplier: "쌀공급업체", description: "고급 쌀" },
    { id: 8, name: "고추장", category: "조미료", unit: "kg", price_per_unit: 12000, supplier: "조미료공급업체", description: "전통 고추장" },
    { id: 9, name: "된장", category: "조미료", unit: "kg", price_per_unit: 8000, supplier: "조미료공급업체", description: "구수한 된장" },
    { id: 10, name: "간장", category: "조미료", unit: "L", price_per_unit: 15000, supplier: "조미료공급업체", description: "고급 간장" },
    { id: 11, name: "올리브오일", category: "조미료", unit: "L", price_per_unit: 25000, supplier: "조미료공급업체", description: "엑스트라 버진 올리브오일" },
    { id: 12, name: "버터", category: "유제품", unit: "kg", price_per_unit: 18000, supplier: "유제품공급업체", description: "고급 버터" }
  ];

  useEffect(() => {
    setMaterialList(dummyMaterials);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleMaterialSelect = (material: Material) => {
    setFormData(prev => ({
      ...prev,
      item: material.name,
      unit: material.unit,
      supplier: material.supplier,
      detail: material.description,
      estimated_cost: material.price_per_unit * prev.quantity
    }));
  };

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const quantity = parseInt(e.target.value) || 0;
    const selectedMaterial = materialList.find(m => m.name === formData.item);
    
    setFormData(prev => ({
      ...prev,
      quantity: quantity,
      estimated_cost: selectedMaterial ? selectedMaterial.price_per_unit * quantity : 0
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          item: formData.item,
          quantity: formData.quantity,
          unit: formData.unit,
          order_date: formData.order_date,
          detail: formData.detail,
          memo: formData.memo,
          supplier: formData.supplier,
          estimated_cost: formData.estimated_cost
        })
      });

      const result = await response.json();

      if (result.success) {
        alert("발주가 성공적으로 추가되었습니다.");
        router.push('/purchase');
      } else {
        alert(result.message || "발주 추가 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error('Error adding purchase:', error);
      alert("발주 추가 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  const selectedMaterial = materialList.find(material => material.name === formData.item);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </button>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">발주 추가</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            새로운 재료 발주를 추가합니다.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 재료 선택 */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <Package className="inline h-5 w-5 mr-2" />
                재료 선택
              </h2>
              
              {/* 카테고리별 재료 */}
              <div className="space-y-6">
                {Array.from(new Set(materialList.map(item => item.category))).map(category => (
                  <div key={category}>
                    <h3 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
                      {category}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {materialList.filter(item => item.category === category).map(material => (
                        <div
                          key={material.id}
                          className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                            formData.item === material.name
                              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                              : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600'
                          }`}
                          onClick={() => handleMaterialSelect(material)}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">{material.name}</h4>
                              <p className="text-sm text-gray-500 dark:text-gray-400">{material.description}</p>
                              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                                공급업체: {material.supplier}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold text-gray-900 dark:text-white">
                                ₩{material.price_per_unit.toLocaleString()}/{material.unit}
                              </p>
                              <button className="mt-1 text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 transition-colors">
                                선택
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 발주 정보 */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                발주 정보
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* 선택된 재료 정보 */}
                {selectedMaterial && (
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg mb-4">
                    <h4 className="font-medium text-blue-900 dark:text-blue-100">{selectedMaterial.name}</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300">{selectedMaterial.description}</p>
                    <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                      공급업체: {selectedMaterial.supplier}
                    </p>
                  </div>
                )}

                {/* 수량 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    수량
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      name="quantity"
                      value={formData.quantity}
                      onChange={handleQuantityChange}
                      min="1"
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      required
                    />
                    <span className="px-3 py-2 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg">
                      {formData.unit}
                    </span>
                  </div>
                </div>

                {/* 발주일 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Calendar className="inline h-4 w-4 mr-2" />
                    발주일
                  </label>
                  <input
                    type="date"
                    name="order_date"
                    value={formData.order_date}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>

                {/* 상세 설명 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    상세 설명
                  </label>
                  <input
                    type="text"
                    name="detail"
                    value={formData.detail}
                    onChange={handleInputChange}
                    placeholder="재료에 대한 상세한 설명을 입력하세요..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>

                {/* 메모 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <FileText className="inline h-4 w-4 mr-2" />
                    메모
                  </label>
                  <textarea
                    name="memo"
                    value={formData.memo}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="발주에 대한 추가 정보나 특이사항을 입력하세요..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                  />
                </div>

                {/* 예상 비용 계산 */}
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    비용 정보
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">단가:</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {selectedMaterial ? `₩${selectedMaterial.price_per_unit.toLocaleString()}/${selectedMaterial.unit}` : '₩0'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">수량:</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {formData.quantity} {formData.unit}
                      </span>
                    </div>
                    <div className="border-t border-gray-200 dark:border-gray-600 pt-2">
                      <div className="flex justify-between">
                        <span className="text-lg font-semibold text-gray-900 dark:text-white">총 예상 비용:</span>
                        <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                          ₩{formData.estimated_cost.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 버튼 */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={isLoading || !formData.item}
                    className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        발주 중...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4" />
                        발주 완료
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
      </div>
    </div>
  );
} 