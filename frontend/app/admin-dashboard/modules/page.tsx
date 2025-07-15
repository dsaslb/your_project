import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

interface ModuleInfo {
  id: string;
  name: string;
  description: string;
  version: string;
  status: string;
}

export default function ModuleManagerPage() {
  const [modules, setModules] = useState<ModuleInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // 실제로는 API에서 모듈 목록을 불러옴
    fetch('/api/marketplace/modules')
      .then(res => res.json())
      .then(data => {
        setModules(data.modules || data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">모듈/플러그인 관리</h1>
      {loading ? (
        <div>로딩 중...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((mod) => (
            <Card key={mod.id} className="hover:shadow-lg transition-all">
              <CardHeader>
                <CardTitle>{mod.name} <Badge>{mod.status}</Badge></CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-2 text-slate-700">{mod.description}</div>
                <div className="text-xs text-slate-500">버전: {mod.version}</div>
                <Button size="sm" className="mt-3" variant="outline" onClick={() => router.push(`/admin-dashboard/modules/${mod.id}`)}>
                  상세/설정
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 