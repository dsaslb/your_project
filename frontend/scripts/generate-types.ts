#!/usr/bin/env tsx

import { execSync } from 'child_process';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
const OUTPUT_DIR = join(__dirname, '..', 'src', 'types');
const OUTPUT_FILE = join(OUTPUT_DIR, 'api-types.ts');

async function generateTypes() {
  try {
    console.log('🔄 OpenAPI 스펙에서 TypeScript 타입을 생성하는 중...');
    
    // 출력 디렉토리 생성
    mkdirSync(OUTPUT_DIR, { recursive: true });
    
    // OpenAPI 스펙 URL
    const openApiUrl = `${API_BASE_URL}/swagger-ui/swagger.json`;
    
    // openapi-typescript를 사용하여 타입 생성
    const command = `npx openapi-typescript ${openApiUrl} --output ${OUTPUT_FILE}`;
    
    console.log(`📡 API 스펙을 가져오는 중: ${openApiUrl}`);
    execSync(command, { stdio: 'inherit' });
    
    // 생성된 파일에 헤더 추가
    const header = `/**
 * 자동 생성된 API 타입 정의
 * 이 파일은 OpenAPI 스펙에서 자동으로 생성됩니다.
 * 수동으로 수정하지 마세요.
 * 
 * 생성 시간: ${new Date().toISOString()}
 * API URL: ${API_BASE_URL}
 */

`;
    
    const content = writeFileSync(OUTPUT_FILE, 'utf8');
    const newContent = header + content;
    writeFileSync(OUTPUT_FILE, newContent);
    
    console.log('✅ TypeScript 타입 생성 완료!');
    console.log(`📁 생성된 파일: ${OUTPUT_FILE}`);
    
  } catch (error) {
    console.error('❌ 타입 생성 실패:', error);
    process.exit(1);
  }
}

// 스크립트 실행
generateTypes(); 