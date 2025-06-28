"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import {
  Select as SelectComponent,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChefHat, Plus, Search, MoreHorizontal, Star, DollarSign, Package, TrendingUp } from "lucide-react";

export function MenuManagement() {
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const menuData = [
    {
      id: 1,
      name: "불고기 정식",
      category: "메인",
      price: 18000,
      cost: 8000,
      profit: 10000,
      status: "available",
      rating: 4.8,
      orders: 45,
      image: "/placeholder.svg?height=60&width=60",
    },
    {
      id: 2,
      name: "김치찌개",
      category: "찌개",
      price: 12000,
      cost: 5000,
      profit: 7000,
      status: "available",
      rating: 4.6,
      orders: 32,
      image: "/placeholder.svg?height=60&width=60",
    },
    {
      id: 3,
      name: "비빔밥",
      category: "메인",
      price: 15000,
      cost: 6000,
      profit: 9000,
      status: "available",
      rating: 4.7,
      orders: 28,
      image: "/placeholder.svg?height=60&width=60",
    },
    {
      id: 4,
      name: "냉면",
      category: "면류",
      price: 13000,
      cost: 4500,
      profit: 8500,
      status: "soldout",
      rating: 4.5,
      orders: 15,
      image: "/placeholder.svg?height=60&width=60",
    },
    {
      id: 5,
      name: "갈비탕",
      category: "탕류",
      price: 16000,
      cost: 7000,
      profit: 9000,
      status: "available",
      rating: 4.9,
      orders: 38,
      image: "/placeholder.svg?height=60&width=60",
    },
  ];

  const categories = ["all", "메인", "찌개", "면류", "탕류", "사이드", "음료"];

  const filteredMenu = menuData.filter(
    (item) =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (categoryFilter === "all" || item.category === categoryFilter),
  );

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      available: {
        label: "판매중",
        className: "bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300",
      },
      soldout: {
        label: "품절",
        className: "bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300",
      },
      discontinued: {
        label: "단종",
        className: "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300",
      },
    };
    const config = statusConfig[status as keyof typeof statusConfig];
    return (
      <Badge variant="outline" className={config.className}>
        {config.label}
      </Badge>
    );
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      메인: "from-red-500 to-orange-500",
      찌개: "from-orange-500 to-yellow-500",
      면류: "from-blue-500 to-cyan-500",
      탕류: "from-green-500 to-emerald-500",
      사이드: "from-purple-500 to-pink-500",
      음료: "from-indigo-500 to-blue-500",
    };
    return colors[category as keyof typeof colors] || "from-gray-500 to-gray-600";
  };

  const totalRevenue = menuData.reduce((sum, item) => sum + item.price * item.orders, 0);
  const totalProfit = menuData.reduce((sum, item) => sum + item.profit * item.orders, 0);
  const totalOrders = menuData.reduce((sum, item) => sum + item.orders, 0);
  const avgRating = menuData.reduce((sum, item) => sum + item.rating, 0) / menuData.length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
            메뉴 관리
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">메뉴 정보와 판매 현황을 관리하세요</p>
        </div>
        <Button className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white shadow-lg">
          <Plus className="h-4 w-4 mr-2" />새 메뉴 추가
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
                <DollarSign className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 매출</p>
                <p className="text-2xl font-bold text-green-600">₩{totalRevenue.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 수익</p>
                <p className="text-2xl font-bold text-blue-600">₩{totalProfit.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-red-500">
                <Package className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 주문</p>
                <p className="text-2xl font-bold text-orange-600">{totalOrders}건</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-gradient-to-r from-yellow-500 to-orange-500">
                <Star className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">평균 평점</p>
                <p className="text-2xl font-bold text-yellow-600">{avgRating.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <ChefHat className="h-6 w-6 text-red-500" />
            <span>메뉴 목록</span>
          </CardTitle>
          <CardDescription>메뉴 정보를 검색하고 관리하세요</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-6">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="메뉴명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <SelectComponent value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="카테고리" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category === "all" ? "전체" : category}
                  </SelectItem>
                ))}
              </SelectContent>
            </SelectComponent>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>메뉴 정보</TableHead>
                  <TableHead>카테고리</TableHead>
                  <TableHead className="text-right">가격</TableHead>
                  <TableHead className="text-right">원가</TableHead>
                  <TableHead className="text-right">수익</TableHead>
                  <TableHead className="text-center">평점</TableHead>
                  <TableHead className="text-center">주문수</TableHead>
                  <TableHead className="text-center">상태</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMenu.map((item) => (
                  <TableRow key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden">
                          <img
                            src={item.image || "/placeholder.svg"}
                            alt={item.name}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{item.name}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            ID: {item.id.toString().padStart(3, "0")}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={`bg-gradient-to-r ${getCategoryColor(item.category)} text-white border-0`}
                      >
                        {item.category}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">₩{item.price.toLocaleString()}</TableCell>
                    <TableCell className="text-right font-mono text-gray-500">₩{item.cost.toLocaleString()}</TableCell>
                    <TableCell className="text-right font-mono text-green-600">
                      ₩{item.profit.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex items-center justify-center space-x-1">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span className="font-medium">{item.rating}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-center font-medium">{item.orders}건</TableCell>
                    <TableCell className="text-center">{getStatusBadge(item.status)}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>상세 보기</DropdownMenuItem>
                          <DropdownMenuItem>정보 수정</DropdownMenuItem>
                          <DropdownMenuItem>가격 변경</DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">메뉴 삭제</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 