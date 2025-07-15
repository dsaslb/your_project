import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ModuleInfo {
  id: string;
  name: string;
  description: string;
  version: string;
  status: string;
}

interface ModuleSettings {
  [key: string]: {
    label: string;
    type: string;
    value: any;
    options?: string[];
  };
}

export default function ModuleDetailPage({ params }: { params: { id: string } }) {
  const moduleId = params.id;
  const [module, setModule] = useState<ModuleInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState<ModuleSettings>({});
  const [settingsLoading, setSettingsLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');

  useEffect(() => {
    fetch(`/api/marketplace/modules`)
      .then(res => res.json())
      .then(data => {
        const found = (data.modules || data || []).find((m: ModuleInfo) => m.id === moduleId);
        setModule(found || null);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [moduleId]);

  useEffect(() => {
    setSettingsLoading(true);
    fetch(`/api/module-settings/${moduleId}`)
      .then(res => res.json())
      .then(data => {
        setSettings(data.settings || {});
        setSettingsLoading(false);
      })
      .catch(() => setSettingsLoading(false));
  }, [moduleId]);

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        value
      }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg('');
    try {
      const res = await fetch(`/api/modules/${moduleId}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings }),
      });
      const data = await res.json();
      if (data.success) setSaveMsg('저장 완료!');
      else setSaveMsg('저장 실패: ' + (data.error || '')); 
    } catch (e) {
      setSaveMsg('저장 실패: 네트워크 오류');
    }
    setSaving(false);
  };

  if (loading) return <div className="p-8">로딩 중...</div>;
  if (!module) return <div className="p-8">모듈 정보를 찾을 수 없습니다.</div>;

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>
            {module.name} <Badge>{module.status}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-2 text-slate-700">{module.description}</div>
          <div className="text-xs text-slate-500 mb-4">버전: {module.version}</div>
          <Button size="sm" variant="outline" onClick={() => window.history.back()} className="mb-6">목록으로</Button>

          <h2 className="text-lg font-bold mb-2 mt-4">설정</h2>
          {settingsLoading ? (
            <div>설정값 불러오는 중...</div>
          ) : (
            <form onSubmit={e => { e.preventDefault(); handleSave(); }}>
              <div className="space-y-4">
                {Object.entries(settings).map(([key, setting]) => (
                  <div key={key}>
                    <label className="block font-medium mb-1">{setting.label}</label>
                    {setting.type === 'checkbox' ? (
                      <input type="checkbox" checked={!!setting.value} onChange={e => handleChange(key, e.target.checked)} />
                    ) : setting.type === 'number' ? (
                      <input type="number" value={setting.value} onChange={e => handleChange(key, Number(e.target.value))} className="border rounded px-2 py-1" />
                    ) : setting.type === 'select' ? (
                      <select value={setting.value} onChange={e => handleChange(key, e.target.value)} className="border rounded px-2 py-1">
                        {setting.options?.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                      </select>
                    ) : (
                      <input type="text" value={setting.value} onChange={e => handleChange(key, e.target.value)} className="border rounded px-2 py-1" />
                    )}
                  </div>
                ))}
              </div>
              <Button type="submit" size="sm" className="mt-6" disabled={saving}>{saving ? '저장 중...' : '저장'}</Button>
              {saveMsg && <div className="mt-2 text-sm text-green-600">{saveMsg}</div>}
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 