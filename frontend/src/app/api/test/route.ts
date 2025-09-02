import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    message: '테스트 API가 정상 작동 중입니다',
    timestamp: new Date().toISOString(),
    status: 'success'
  });
}
