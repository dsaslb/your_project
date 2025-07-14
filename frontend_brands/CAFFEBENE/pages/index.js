import React from 'react';

export default function 카페베네Dashboard() {
  return (
    <div style={ padding: '20px', fontFamily: 'Arial, sans-serif' }>
      <h1 style={ color: '#333' }>카페베네 대시보드</h1>
      <p>브랜드 전용 프론트엔드 서버가 생성되었습니다.</p>
      <div style={ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '5px' }>
        <h3>브랜드 정보</h3>
        <p><strong>코드:</strong> CAFFEBENE</p>
        <p><strong>설명:</strong> 프리미엄 커피 브랜드</p>
        <p><strong>웹사이트:</strong> <a href="https://caffebene.co.kr" target="_blank">https://caffebene.co.kr</a></p>
        <p><strong>연락처:</strong> contact@caffebene.co.kr</p>
      </div>
    </div>
  );
}
