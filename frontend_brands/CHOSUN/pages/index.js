import React from 'react';

export default function 초선마리Dashboard() {
  return (
    <div style={ padding: '20px', fontFamily: 'Arial, sans-serif' }>
      <h1 style={ color: '#333' }>초선마리 대시보드</h1>
      <p>브랜드 전용 프론트엔드 서버가 생성되었습니다.</p>
      <div style={ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '5px' }>
        <h3>브랜드 정보</h3>
        <p><strong>코드:</strong> CHOSUN</p>
        <p><strong>설명:</strong> 한국 전통 차 브랜드</p>
        <p><strong>웹사이트:</strong> <a href="https://chosunmari.com" target="_blank">https://chosunmari.com</a></p>
        <p><strong>연락처:</strong> contact@chosunmari.com</p>
      </div>
    </div>
  );
}
