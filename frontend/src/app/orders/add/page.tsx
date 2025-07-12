"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, User, Phone, ShoppingCart, Calendar, Clock, MapPin, FileText, Save, X, Plus, Minus } from "lucide-react";

interface MenuItem {
  id: number;
  name: string;
  price: number;
  category: string;
  description: string;
}

interface OrderItem {
  menu_id: number;
  name: string;
  price: number;
  quantity: number;
}

interface OrderForm {
  customer_name: string;
  phone: string;
  table: string;
  items: OrderItem[];
  notes: string;
  estimated_time: string;
}

export default function OrderAddPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [menuList, setMenuList] = useState<MenuItem[]>([]);
  const [formData, setFormData] = useState<OrderForm>({
    customer_name: "",
    phone: "",
    table: "",
    items: [],
    notes: "",
    estimated_time: "30"
  });

  // 더미 메뉴 데이터
  const dummyMenu = [
    { id: 1, name: "불고기", price: 15000, category: "메인", description: "맛있는 불고기" },
    { id: 2, name: "김치찌개", price: 12000, category: "찌개", description: "얼큰한 김치찌개" },
    { id: 3, name: "제육볶음", price: 14000, category: "메인", description: "매콤달콤 제육볶음" },
    { id: 4, name: "된장찌개", price: 11000, category: "찌개", description: "구수한 된장찌개" },
    { id: 5, name: "삼겹살", price: 18000, category: "고기", description: "신선한 삼겹살" },
    { id: 6, name: "치킨", price: 20000, category: "치킨", description: "바삭한 치킨" },
    { id: 7, name: "파스타", price: 16000, category: "양식", description: "알덴테 파스타" },
    { id: 8, name: "샐러드", price: 8000, category: "샐러드", description: "신선한 샐러드" },
    { id: 9, name: "공기밥", price: 1000, category: "밥", description: "쌀밥" },
    { id: 10, name: "소주", price: 4000, category: "음료", description: "시원한 소주" },
    { id: 11, name: "콜라", price: 2000, category: "음료", description: "시원한 콜라" },
    { id: 12, name: "와인", price: 12000, category: "음료", description: "고급 와인" }
  ];

  useEffect(() => {
    setMenuList(dummyMenu);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addMenuItem = (menu: MenuItem) => {
    const existingItem = formData.items.find(item => item.menu_id === menu.id);
    
    if (existingItem) {
      setFormData(prev => ({
        ...prev,
        items: prev.items.map(item => 
          item.menu_id === menu.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        items: [...prev.items, {
          menu_id: menu.id,
          name: menu.name,
          price: menu.price,
          quantity: 1
        }]
      }));
    }
  };

  const updateItemQuantity = (menuId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      setFormData(prev => ({
        ...prev,
        items: prev.items.filter(item => item.menu_id !== menuId)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        items: prev.items.map(item => 
          item.menu_id === menuId 
            ? { ...item, quantity: newQuantity }
            : item
        )
      }));
    }
  };

  const removeItem = (menuId: number) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter(item => item.menu_id !== menuId)
    }));
  };

  const calculateTotal = () => {
    return formData.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
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
          customer_name: formData.customer_name,
          phone: formData.phone,
          table: formData.table,
          items: formData.items,
          notes: formData.notes,
          estimated_time: formData.estimated_time,
          total: calculateTotal()
        })
      });

      const result = await response.json();

      if (result.success) {
        alert("주문이 성공적으로 추가되었습니다.");
        router.push('/orders');
      } else {
        alert(result.message || "주문 추가 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error('Error adding order:', error);
      alert("주문 추가 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">주문 추가</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            새로운 주문을 추가합니다.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 메뉴 선택 */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <ShoppingCart className="inline h-5 w-5 mr-2" />
                메뉴 선택
              </h2>
              
              {/* 카테고리별 메뉴 */}
              <div className="space-y-6">
                {Array.from(new Set(menuList.map(item => item.category))).map(category => (
                  <div key={category}>
                    <h3 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
                      {category}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {menuList.filter(item => item.category === category).map(menu => (
                        <div
                          key={menu.id}
                          className="border border-gray-200 dark:border-gray-600 rounded-lg p-3 hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer transition-colors"
                          onClick={() => addMenuItem(menu)}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">{menu.name}</h4>
                              <p className="text-sm text-gray-500 dark:text-gray-400">{menu.description}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold text-gray-900 dark:text-white">₩{menu.price.toLocaleString()}</p>
                              <button className="mt-1 text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 transition-colors">
                                추가
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

          {/* 주문 정보 */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                주문 정보
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* 고객 정보 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <User className="inline h-4 w-4 mr-2" />
                    고객명
                  </label>
                  <input
                    type="text"
                    name="customer_name"
                    value={formData.customer_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Phone className="inline h-4 w-4 mr-2" />
                    연락처
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="010-1234-5678"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <MapPin className="inline h-4 w-4 mr-2" />
                    테이블
                  </label>
                  <select
                    name="table"
                    value={formData.table}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  >
                    <option value="">테이블을 선택하세요</option>
                    <option value="A-1">A-1</option>
                    <option value="A-2">A-2</option>
                    <option value="A-3">A-3</option>
                    <option value="B-1">B-1</option>
                    <option value="B-2">B-2</option>
                    <option value="C-1">C-1</option>
                    <option value="C-2">C-2</option>
                    <option value="D-1">D-1</option>
                    <option value="D-2">D-2</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Clock className="inline h-4 w-4 mr-2" />
                    예상 완료시간 (분)
                  </label>
                  <select
                    name="estimated_time"
                    value={formData.estimated_time}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    required
                  >
                    <option value="15">15분</option>
                    <option value="20">20분</option>
                    <option value="25">25분</option>
                    <option value="30">30분</option>
                    <option value="35">35분</option>
                    <option value="40">40분</option>
                    <option value="45">45분</option>
                    <option value="50">50분</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <FileText className="inline h-4 w-4 mr-2" />
                    요청사항
                  </label>
                  <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="특별한 요청사항이 있으시면 입력해주세요..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                  />
                </div>

                {/* 선택된 메뉴 */}
                {formData.items.length > 0 && (
                  <div className="border-t border-gray-200 dark:border-gray-600 pt-4">
                    <h3 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
                      선택된 메뉴
                    </h3>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {formData.items.map(item => (
                        <div key={item.menu_id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{item.name}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">₩{item.price.toLocaleString()}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => updateItemQuantity(item.menu_id, item.quantity - 1)}
                              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                            >
                              <Minus className="h-3 w-3" />
                            </button>
                            <span className="text-sm font-medium text-gray-900 dark:text-white min-w-[20px] text-center">
                              {item.quantity}
                            </span>
                            <button
                              type="button"
                              onClick={() => updateItemQuantity(item.menu_id, item.quantity + 1)}
                              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                            >
                              <Plus className="h-3 w-3" />
                            </button>
                            <button
                              type="button"
                              onClick={() => removeItem(item.menu_id)}
                              className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 총 금액 */}
                {formData.items.length > 0 && (
                  <div className="border-t border-gray-200 dark:border-gray-600 pt-4">
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-semibold text-gray-900 dark:text-white">총 금액</span>
                      <span className="text-xl font-bold text-blue-600 dark:text-blue-400">
                        ₩{calculateTotal().toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}

                {/* 버튼 */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={isLoading || formData.items.length === 0}
                    className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        주문 중...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4" />
                        주문 완료
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