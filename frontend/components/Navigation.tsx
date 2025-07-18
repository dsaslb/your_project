import React from 'react';
import Link from 'next/link';

const Navigation: React.FC = () => {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto">
        <h1 className="text-xl font-bold mb-4">멀티테넌시 관리 시스템</h1>
        <div className="flex space-x-4">
          <Link href="/admin/industry" className="hover:text-gray-300">
            업종 관리자
          </Link>
          <Link href="/admin/brand" className="hover:text-gray-300">
            브랜드 관리자
          </Link>
          <Link href="/admin/branch" className="hover:text-gray-300">
            매장 관리자
          </Link>
          <Link href="/user" className="hover:text-gray-300">
            직원(사용자)
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 