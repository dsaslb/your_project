import React, { useState } from 'react';

const defaultSettings = {
  logo: '',
  color: '#2563eb',
  theme: 'light',
  notifications: true,
};

export default function BrandSettingsPage({ params }: { params: { brand_id: string } }) {
  const { brand_id } = params;
  const [settings, setSettings] = useState(defaultSettings);
  const [previewColor, setPreviewColor] = useState(settings.color);
  const [applied, setApplied] = useState(false);

  // 실시간 미리보기/저장/적용
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setSettings(prev => ({ ...prev, [name]: checked }));
    } else {
      setSettings(prev => ({ ...prev, [name]: value }));
      if (name === 'color') setPreviewColor(value);
    }
    setApplied(false); // 변경 시 적용 상태 해제
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = ev => {
        setSettings(prev => ({ ...prev, logo: ev.target?.result as string }));
      };
      reader.readAsDataURL(e.target.files[0]);
    }
    setApplied(false);
  };

  const handleSave = async () => {
    // 실제로는 API로 저장
    setApplied(true);
    alert('설정이 저장되었습니다! (샘플)');
    // 샘플: 테마/색상/알림이 즉시 적용된 것처럼 효과
    document.body.style.background = settings.theme === 'dark' ? '#18181b' : '#f8fafc';
    document.body.style.setProperty('--brand-color', settings.color);
    // 알림 샘플
    if (settings.notifications) {
      // eslint-disable-next-line no-alert
      alert('알림이 활성화되었습니다! (샘플)');
    }
  };

  return (
    <div className="max-w-xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">브랜드 설정</h1>
      <div className="mb-4">
        <label className="block mb-1 font-semibold">로고 업로드</label>
        <input type="file" accept="image/*" onChange={handleLogoChange} aria-label="로고 업로드" />
        {settings.logo && <img src={settings.logo} alt="로고 미리보기" className="h-16 mt-2" />}
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-semibold">대표 색상</label>
        <input type="color" name="color" value={settings.color} onChange={handleChange} aria-label="대표 색상 선택" />
        <span className="ml-2">{settings.color}</span>
        <div className="w-16 h-4 mt-2 rounded" style={{ background: previewColor }} />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-semibold">테마</label>
        <select name="theme" value={settings.theme} onChange={handleChange} aria-label="테마 선택">
          <option value="light">라이트</option>
          <option value="dark">다크</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-semibold">알림</label>
        <input type="checkbox" name="notifications" checked={settings.notifications} onChange={handleChange} aria-label="알림 설정" />
        <span className="ml-2">{settings.notifications ? 'ON' : 'OFF'}</span>
      </div>
      <button className="px-6 py-2 bg-blue-600 text-white rounded" onClick={handleSave} aria-label="설정 저장">설정 저장</button>
      {applied && (
        <div className="mt-4 text-green-600 font-semibold">설정이 즉시 적용되었습니다! (샘플)</div>
      )}
      <div className="mt-8 text-xs text-gray-500">
        브랜드별 로고/색상/테마/알림을 실시간으로 미리보고 저장/적용할 수 있습니다.<br />
        (실제 저장/적용은 API 연동 필요, 샘플 UI)
      </div>
    </div>
  );
} 