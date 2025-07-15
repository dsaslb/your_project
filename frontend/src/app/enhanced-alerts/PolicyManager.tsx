import React, { useEffect, useState } from 'react';
// 운영 자동화 정책/규칙 관리 UI (초보자용 설명, 글로벌 다국어 지원)

const messages = {
  title: { ko: '운영 자동화 정책 관리', en: 'Automation Policy Management' },
  add: { ko: '정책 추가', en: 'Add Policy' },
  name: { ko: '정책명', en: 'Name' },
  desc: { ko: '설명', en: 'Description' },
  trigger: { ko: '트리거', en: 'Trigger' },
  actions: { ko: '액션', en: 'Actions' },
  save: { ko: '저장', en: 'Save' },
  delete: { ko: '삭제', en: 'Delete' },
  edit: { ko: '수정', en: 'Edit' },
  cancel: { ko: '취소', en: 'Cancel' },
  loading: { ko: '로딩 중...', en: 'Loading...' }
};
function getLang() {
  if (typeof window !== 'undefined') {
    return (navigator.language || 'ko').startsWith('en') ? 'en' : 'ko';
  }
  return 'ko';
}

const PolicyManager: React.FC = () => {
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<any>(null);
  const [form, setForm] = useState<any>({ name: '', description: '', trigger_type: '', actions: [] });
  const lang = getLang();

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    setLoading(true);
    const res = await fetch('/api/automation/policy');
    const data = await res.json();
    setPolicies(data.policies || []);
    setLoading(false);
  };

  const handleSave = async () => {
    if (editing) {
      await fetch(`/api/automation/policy/${editing.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
    } else {
      await fetch('/api/automation/policy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
    }
    setForm({ name: '', description: '', trigger_type: '', actions: [] });
    setEditing(null);
    fetchPolicies();
  };

  const handleEdit = (policy: any) => {
    setEditing(policy);
    setForm(policy);
  };

  const handleDelete = async (id: number) => {
    await fetch(`/api/automation/policy/${id}`, { method: 'DELETE' });
    fetchPolicies();
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">{messages.title[lang]}</h2>
      {loading ? (
        <div>{messages.loading[lang]}</div>
      ) : (
        <>
          <table className="w-full mb-4">
            <thead>
              <tr>
                <th>{messages.name[lang]}</th>
                <th>{messages.desc[lang]}</th>
                <th>{messages.trigger[lang]}</th>
                <th>{messages.actions[lang]}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {policies.map((p) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td>{p.description}</td>
                  <td>{p.trigger_type}</td>
                  <td>{p.actions?.map((a: any) => a.type).join(', ')}</td>
                  <td>
                    <button onClick={() => handleEdit(p)}>{messages.edit[lang]}</button>
                    <button onClick={() => handleDelete(p.id)} className="ml-2 text-red-500">{messages.delete[lang]}</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mb-2 font-semibold">{editing ? messages.edit[lang] : messages.add[lang]}</div>
          <input className="border p-1 mr-2" placeholder={messages.name[lang]} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          <input className="border p-1 mr-2" placeholder={messages.desc[lang]} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
          <input className="border p-1 mr-2" placeholder={messages.trigger[lang]} value={form.trigger_type} onChange={e => setForm({ ...form, trigger_type: e.target.value })} />
          <input className="border p-1 mr-2" placeholder={messages.actions[lang]} value={form.actions.map((a: any) => a.type).join(',')} onChange={e => setForm({ ...form, actions: e.target.value.split(',').map((t: string) => ({ type: t })) })} />
          <button onClick={handleSave} className="bg-blue-500 text-white px-2 py-1 rounded mr-2">{messages.save[lang]}</button>
          {editing && <button onClick={() => { setEditing(null); setForm({ name: '', description: '', trigger_type: '', actions: [] }); }} className="bg-gray-300 px-2 py-1 rounded">{messages.cancel[lang]}</button>}
        </>
      )}
    </div>
  );
};

export default PolicyManager; 