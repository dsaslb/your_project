#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const API_BASE_URL = 'http://localhost:5000';
const OUTPUT_DIR = path.join(__dirname, '../frontend/src/types');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'api-types.ts');

async function fetchSwaggerSpec() {
  return new Promise((resolve, reject) => {
    const url = new URL(`${API_BASE_URL}/openapi.json`);
    const client = url.protocol === 'https:' ? https : http;
    
    const req = client.get(url, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const spec = JSON.parse(data);
          resolve(spec);
        } catch (error) {
          reject(new Error(`JSON 파싱 실패: ${error.message}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(new Error(`HTTP 요청 실패: ${error.message}`));
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('요청 시간 초과'));
    });
  });
}

function generateTypeScriptTypes(spec) {
  let content = `// ===== 자동 생성된 TypeScript 타입 =====
// 이 파일은 Swagger JSON에서 자동 생성되었습니다.
// 수동으로 편집하지 마세요.
// 생성 시간: ${new Date().toISOString()}

`;

  // 스키마에서 타입 생성
  if (spec.components && spec.components.schemas) {
    for (const [schemaName, schema] of Object.entries(spec.components.schemas)) {
      if (schema.type === 'object' && schema.properties) {
        const typeName = toPascalCase(schemaName);
        content += generateObjectType(typeName, schema);
      }
    }
  }

  // API 응답 타입 추가
  content += `
// ===== API 응답 타입 =====

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page?: number;
  pageSize?: number;
}

// ===== API 엔드포인트 타입 =====

export interface ApiEndpoints {
  // 헬스체크
  'GET /api/health': {
    response: HealthResponse;
  };
  
  // 인증
  'POST /api/security/auth/login': {
    request: LoginRequest;
    response: LoginResponse;
  };
  
  // 브랜드
  'GET /api/brands': {
    response: PaginatedResponse<Brand>;
  };
  'POST /api/brands': {
    request: BrandCreate;
    response: Brand;
  };
  'GET /api/brands/{id}': {
    response: Brand;
  };
  
  // 매장
  'GET /api/branches': {
    response: PaginatedResponse<Branch>;
  };
  'POST /api/branches': {
    request: BranchCreate;
    response: Branch;
  };
  'GET /api/branches/{id}': {
    response: Branch;
  };
  
  // 직원
  'GET /api/employees': {
    response: PaginatedResponse<Employee>;
  };
  'GET /api/employees/{id}': {
    response: Employee;
  };
  
  // 스케줄
  'GET /api/schedules': {
    response: PaginatedResponse<Schedule>;
  };
  'POST /api/schedules': {
    request: ScheduleCreate;
    response: Schedule;
  };
  
  // 직원 대시보드
  'GET /api/employee/dashboard': {
    response: EmployeeDashboard;
  };
  'POST /api/employee/clock-in': {
    request: ClockInOutRequest;
    response: ClockInOutResponse;
  };
  'POST /api/employee/clock-out': {
    request: ClockInOutRequest;
    response: ClockInOutResponse;
  };
  
  // 관리자 대시보드
  'GET /api/admin/dashboard': {
    response: AdminDashboard;
  };
  
  // 테스트
  'POST /api/test/notification': {
    request: NotificationRequest;
    response: ApiResponse;
  };
  'POST /api/test/system-alert': {
    request: SystemAlertRequest;
    response: ApiResponse;
  };
}

// ===== API 클라이언트 타입 =====

export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface ApiRequestConfig {
  method: ApiMethod;
  url: string;
  data?: any;
  params?: Record<string, any>;
  headers?: Record<string, string>;
}

export interface ApiClient {
  request<T>(config: ApiRequestConfig): Promise<T>;
  get<T>(url: string, config?: Partial<ApiRequestConfig>): Promise<T>;
  post<T>(url: string, data?: any, config?: Partial<ApiRequestConfig>): Promise<T>;
  put<T>(url: string, data?: any, config?: Partial<ApiRequestConfig>): Promise<T>;
  delete<T>(url: string, config?: Partial<ApiRequestConfig>): Promise<T>;
}
`;

  return content;
}

function generateObjectType(name, schema) {
  const properties = schema.properties || {};
  const required = schema.required || [];
  
  let content = `export interface ${name} {\n`;
  
  for (const [propName, propSchema] of Object.entries(properties)) {
    const isRequired = required.includes(propName);
    const type = getTypeScriptType(propSchema);
    const optional = isRequired ? '' : '?';
    
    content += `  ${propName}${optional}: ${type};\n`;
  }
  
  content += '}\n\n';
  return content;
}

function getTypeScriptType(schema) {
  if (schema.$ref) {
    return resolveRef(schema.$ref);
  }
  
  switch (schema.type) {
    case 'string':
      if (schema.enum) {
        return schema.enum.map(v => `'${v}'`).join(' | ');
      }
      return 'string';
    case 'number':
    case 'integer':
      return 'number';
    case 'boolean':
      return 'boolean';
    case 'array':
      const itemType = getTypeScriptType(schema.items);
      return `${itemType}[]`;
    case 'object':
      return 'Record<string, any>';
    default:
      return 'any';
  }
}

function resolveRef(ref) {
  const parts = ref.split('/');
  const schemaName = parts[parts.length - 1];
  return toPascalCase(schemaName);
}

function toPascalCase(str) {
  return str
    .split(/[-_]/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

async function main() {
  try {
    console.log('🚀 TypeScript 타입 생성 시작...');
    
    // 1. Swagger JSON 가져오기
    console.log('📥 Swagger JSON 가져오는 중...');
    const swaggerSpec = await fetchSwaggerSpec();
    
    // 2. TypeScript 타입 생성
    console.log('🔧 TypeScript 타입 생성 중...');
    const typeContent = generateTypeScriptTypes(swaggerSpec);
    
    // 3. 출력 디렉토리 생성
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    
    // 4. 파일 작성
    console.log('💾 타입 파일 생성 중...');
    fs.writeFileSync(OUTPUT_FILE, typeContent, 'utf8');
    
    console.log('✅ TypeScript 타입 생성 완료!');
    console.log(`📁 생성된 파일: ${OUTPUT_FILE}`);
    
  } catch (error) {
    console.error('❌ 타입 생성 실패:', error.message);
    process.exit(1);
  }
}

// 스크립트 실행
main(); 