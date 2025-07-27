import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import StoreListPage from '../../app/brand/[brand_id]/store/page';

// fetch mocking
beforeEach(() => {
  global.fetch = jest.fn((url, options) => {
    if (url.includes('/api/stores?brand_id=')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ stores: [{ id: '1', name: '테스트매장', address: '서울' }] }) });
    }
    if (url.includes('/api/profile')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ role: 'admin' }) });
    }
    if (url.includes('/api/stores') && options?.method === 'POST') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  }) as any;
});

describe('브랜드별 매장 페이지', () => {
  it('매장 목록이 정상적으로 렌더링된다', async () => {
    render(<StoreListPage params={{ brand_id: '1' }} />);
    expect(screen.getByText('로딩 중...')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('테스트매장 (서울)')).toBeInTheDocument());
  });

  it('매장 추가 폼이 노출되고, 추가 버튼 클릭 시 fetch가 호출된다', async () => {
    render(<StoreListPage params={{ brand_id: '1' }} />);
    await waitFor(() => screen.getByText('테스트매장 (서울)'));
    fireEvent.click(screen.getByText('매장 추가'));
    fireEvent.change(screen.getByPlaceholderText('매장명'), { target: { value: '새매장' } });
    fireEvent.change(screen.getByPlaceholderText('주소'), { target: { value: '부산' } });
    fireEvent.click(screen.getByText('추가'));
    await waitFor(() => expect(global.fetch).toHaveBeenCalledWith(
      '/api/stores',
      expect.objectContaining({ method: 'POST' })
    ));
  });
}); 