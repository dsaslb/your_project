#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const API_BASE_URL = 'http://localhost:5000';
const OUTPUT_DIR = path.join(__dirname, '../frontend/src/types');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'api-types.ts');

interface SwaggerSpec {
  openapi: string;
  info: {
    title: string;
    version: string;
    description?: string;
  };
  paths: Record<string, any>;
  components: {
    schemas: Record<string, any>;
  };
}

interface TypeScriptType {
  name: string;
  content: string;
  imports: string[];
}

class TypeGenerator {
  private types: TypeScriptType[] = [];
  private imports: Set<string> = new Set();

  async generateTypes(): Promise<void> {
    console.log('🚀 TypeScript 타입 생성 시작...');
    
    try {
      // 1. Swagger JSON 가져오기
      console.log('📥 Swagger JSON 가져오는 중...');
      const swaggerSpec = await this.fetchSwaggerSpec();
      
      // 2. 스키마에서 타입 생성
      console.log('🔧 스키마에서 타입 생성 중...');
      this.generateTypesFromSchemas(swaggerSpec.components.schemas);
      
      // 3. API 응답 타입 생성
      console.log('🌐 API 응답 타입 생성 중...');
      this.generateApiResponseTypes(swaggerSpec.paths);
      
      // 4. 파일 생성
      console.log('💾 타입 파일 생성 중...');
      await this.writeTypeFile();
      
      console.log('✅ TypeScript 타입 생성 완료!');
      console.log(`📁 생성된 파일: ${OUTPUT_FILE}`);
      
    } catch (error) {
      console.error('❌ 타입 생성 실패:', error);
      process.exit(1);
    }
  }

  private async fetchSwaggerSpec(): Promise<SwaggerSpec> {
    try {
      const response = await fetch(`${API_BASE_URL}/openapi.json`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json() as SwaggerSpec;
    } catch (error) {
      console.error('Swagger JSON 가져오기 실패:', error);
      throw error;
    }
  }

  private generateTypesFromSchemas(schemas: Record<string, any>): void {
    for (const [schemaName, schema] of Object.entries(schemas)) {
      if (schema.type === 'object' && schema.properties) {
        const typeName = this.toPascalCase(schemaName);
        const content = this.generateObjectType(typeName, schema);
        
        this.types.push({
          name: typeName,
          content,
          imports: this.extractImports(content)
        });
      } else if (schema.type === 'array' && schema.items) {
        const typeName = this.toPascalCase(schemaName);
        const content = this.generateArrayType(typeName, schema);
        
        this.types.push({
          name: typeName,
          content,
          imports: this.extractImports(content)
        });
      }
    }
  }

  private generateObjectType(name: string, schema: any): string {
    const properties = schema.properties || {};
    const required = schema.required || [];
    
    let content = `export interface ${name} {\n`;
    
    for (const [propName, propSchema] of Object.entries(properties)) {
      const isRequired = required.includes(propName);
      const type = this.getTypeScriptType(propSchema);
      const optional = isRequired ? '' : '?';
      
      content += `  ${propName}${optional}: ${type};\n`;
    }
    
    content += '}\n';
    return content;
  }

  private generateArrayType(name: string, schema: any): string {
    const itemType = this.getTypeScriptType(schema.items);
    return `export type ${name} = ${itemType}[];\n`;
  }

  private getTypeScriptType(schema: any): string {
    if (schema.$ref) {
      return this.resolveRef(schema.$ref);
    }
    
    switch (schema.type) {
      case 'string':
        if (schema.enum) {
          return schema.enum.map((v: string) => `'${v}'`).join(' | ');
        }
        return 'string';
      case 'number':
      case 'integer':
        return 'number';
      case 'boolean':
        return 'boolean';
      case 'array':
        const itemType = this.getTypeScriptType(schema.items);
        return `${itemType}[]`;
      case 'object':
        return 'Record<string, any>';
      default:
        return 'any';
    }
  }

  private resolveRef(ref: string): string {
    const parts = ref.split('/');
    const schemaName = parts[parts.length - 1];
    return this.toPascalCase(schemaName);
  }

  private toPascalCase(str: string): string {
    return str
      .split(/[-_]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join('');
  }

  private extractImports(content: string): string[] {
    const imports: string[] = [];
    const importRegex = /import\s+.*\s+from\s+['"]([^'"]+)['"]/g;
    let match;
    
    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1]);
    }
    
    return imports;
  }

  private generateApiResponseTypes(paths: Record<string, any>): void {
    // API 응답 타입 생성
    const apiTypes = `
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

    this.types.push({
      name: 'ApiTypes',
      content: apiTypes,
      imports: []
    });
  }

  private async writeTypeFile(): Promise<void> {
    // 출력 디렉토리 생성
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // 파일 헤더
    let content = `// ===== 자동 생성된 TypeScript 타입 =====
// 이 파일은 Swagger JSON에서 자동 생성되었습니다.
// 수동으로 편집하지 마세요.

`;

    // 모든 타입 추가
    for (const type of this.types) {
      content += `// ===== ${type.name} =====\n`;
      content += type.content;
      content += '\n';
    }

    // 파일 작성
    fs.writeFileSync(OUTPUT_FILE, content, 'utf8');
  }
}

// 스크립트 실행
async function main() {
  const generator = new TypeGenerator();
  await generator.generateTypes();
}

// 에러 처리
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

main().catch((error) => {
  console.error('스크립트 실행 실패:', error);
  process.exit(1);
}); 