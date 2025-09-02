import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5000';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const path = params.path.join('/');
    const url = new URL(request.url);
    const queryString = url.search;
    
    console.log(`프록시 요청: ${BACKEND_URL}/${path}${queryString}`);
    
    const response = await fetch(`${BACKEND_URL}/${path}${queryString}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      console.error(`백엔드 응답 오류: ${response.status}`);
      return NextResponse.json(
        { error: `백엔드 오류: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('프록시 응답 성공:', data);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('프록시 오류:', error);
    return NextResponse.json(
      { error: '프록시 요청 실패', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const path = params.path.join('/');
    const body = await request.json();
    
    console.log(`프록시 POST 요청: ${BACKEND_URL}/${path}`);
    
    const response = await fetch(`${BACKEND_URL}/${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `백엔드 오류: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('프록시 POST 오류:', error);
    return NextResponse.json(
      { error: '프록시 요청 실패', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const path = params.path.join('/');
    const body = await request.json();
    
    const response = await fetch(`${BACKEND_URL}/${path}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...Object.fromEntries(request.headers.entries()),
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('프록시 오류:', error);
    return NextResponse.json(
      { error: '프록시 요청 실패', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const path = params.path.join('/');
    
    const response = await fetch(`${BACKEND_URL}/${path}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...Object.fromEntries(request.headers.entries()),
      },
    });

    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('프록시 오류:', error);
    return NextResponse.json(
      { error: '프록시 요청 실패', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
