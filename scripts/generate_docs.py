#!/usr/bin/env python3
"""
API 문서 자동 생성 스크립트
Flask 애플리케이션에서 API 엔드포인트를 자동으로 분석하여 문서 생성
"""

import os
import json
import inspect
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class APIDocGenerator:
    """API 문서 자동 생성기"""
    
    def __init__(self, app_dir: str = ".", output_dir: str = "docs"):
        self.app_dir = Path(app_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # API 엔드포인트 정보
        self.endpoints = []
        
        # Flask 앱 모듈들
        self.flask_modules = [
            'app.py',
            'api/',
            'routes/'
        ]
    
    def scan_endpoints(self):
        """Flask 애플리케이션에서 API 엔드포인트 스캔"""
        print("🔍 API 엔드포인트 스캔 중...")
        
        # app.py 스캔
        app_file = self.app_dir / 'app.py'
        if app_file.exists():
            self._scan_file(app_file)
        
        # api 디렉토리 스캔
        api_dir = self.app_dir / 'api'
        if api_dir.exists():
            for file_path in api_dir.rglob('*.py'):
                if file_path.name != '__init__.py':
                    self._scan_file(file_path)
        
        # routes 디렉토리 스캔
        routes_dir = self.app_dir / 'routes'
        if routes_dir.exists():
            for file_path in routes_dir.rglob('*.py'):
                if file_path.name != '__init__.py':
                    self._scan_file(file_path)
        
        print(f"✅ {len(self.endpoints)}개의 엔드포인트 발견")
    
    def _scan_file(self, file_path: Path):
        """파일에서 API 엔드포인트 스캔"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST 파싱
            tree = ast.parse(content)
            
            # Flask 라우트 데코레이터 찾기
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._analyze_function(node, file_path)
                    
        except Exception as e:
            print(f"⚠️ 파일 스캔 실패 {file_path}: {e}")
    
    def _analyze_function(self, func_node: ast.FunctionDef, file_path: Path):
        """함수에서 API 엔드포인트 정보 추출"""
        # 데코레이터 확인
        for decorator in func_node.decorators:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr in ['route', 'get', 'post', 'put', 'delete']:
                        endpoint_info = self._extract_endpoint_info(decorator, func_node, file_path)
                        if endpoint_info:
                            self.endpoints.append(endpoint_info)
    
    def _extract_endpoint_info(self, decorator: ast.Call, func_node: ast.FunctionDef, file_path: Path) -> Optional[Dict[str, Any]]:
        """엔드포인트 정보 추출"""
        try:
            # HTTP 메서드와 경로 추출
            http_method = decorator.func.attr.upper()
            if http_method == 'ROUTE':
                http_method = 'GET'  # 기본값
            
            # 경로 추출
            path = '/'
            if decorator.args:
                path = ast.literal_eval(decorator.args[0])
            
            # 함수 정보 추출
            func_info = {
                'name': func_node.name,
                'path': path,
                'method': http_method,
                'file': str(file_path.relative_to(self.app_dir)),
                'line': func_node.lineno,
                'docstring': ast.get_docstring(func_node) or '',
                'parameters': self._extract_parameters(func_node),
                'returns': self._extract_return_type(func_node)
            }
            
            # 추가 정보 추출
            func_info.update(self._extract_additional_info(decorator, func_node))
            
            return func_info
            
        except Exception as e:
            print(f"⚠️ 엔드포인트 정보 추출 실패: {e}")
            return None
    
    def _extract_parameters(self, func_node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """함수 매개변수 추출"""
        parameters = []
        
        for arg in func_node.args.args:
            if arg.arg not in ['self', 'cls']:  # Flask 함수는 보통 self/cls 없음
                param_info = {
                    'name': arg.arg,
                    'type': self._get_type_annotation(arg.annotation),
                    'required': True
                }
                parameters.append(param_info)
        
        return parameters
    
    def _extract_return_type(self, func_node: ast.FunctionDef) -> str:
        """반환 타입 추출"""
        if func_node.returns:
            return self._get_type_annotation(func_node.returns)
        return 'Any'
    
    def _get_type_annotation(self, annotation) -> str:
        """타입 어노테이션을 문자열로 변환"""
        if annotation is None:
            return 'Any'
        
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Attribute):
                return f"{annotation.value.id}.{annotation.attr}"
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            else:
                return 'Any'
        except:
            return 'Any'
    
    def _extract_additional_info(self, decorator: ast.Call, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """추가 정보 추출 (인증, 권한 등)"""
        info = {
            'auth_required': False,
            'permissions': [],
            'rate_limit': None,
            'content_type': 'application/json'
        }
        
        # 함수 본문에서 추가 정보 추출
        func_body = ast.unparse(func_node) if hasattr(ast, 'unparse') else ''
        
        # 인증 필요 여부 확인
        if any(keyword in func_body.lower() for keyword in ['@login_required', '@auth_required', 'jwt_required']):
            info['auth_required'] = True
        
        # 권한 확인
        permission_pattern = r'@permission_required\([\'"]([^\'"]+)[\'"]\)'
        permissions = re.findall(permission_pattern, func_body)
        info['permissions'] = permissions
        
        # Rate limiting 확인
        rate_limit_pattern = r'@rate_limit\((\d+)\)'
        rate_matches = re.findall(rate_limit_pattern, func_body)
        if rate_matches:
            info['rate_limit'] = int(rate_matches[0])
        
        return info
    
    def generate_markdown_docs(self):
        """Markdown 형식의 API 문서 생성"""
        print("📝 Markdown 문서 생성 중...")
        
        # 문서 템플릿
        template = self._load_template()
        
        # 엔드포인트 그룹화
        grouped_endpoints = self._group_endpoints()
        
        # 문서 내용 생성
        content = template.format(
            generation_date=datetime.now().strftime('%Y년 %m월 %d일'),
            endpoints=self._generate_endpoints_section(grouped_endpoints)
        )
        
        # 파일 저장
        output_file = self.output_dir / 'API_DOCUMENTATION.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ API 문서 생성 완료: {output_file}")
    
    def _load_template(self) -> str:
        """문서 템플릿 로드"""
        return """# 📚 Your Program API 문서

**생성일**: {generation_date}  
**기본 URL**: `http://localhost:5000`

## 📋 목차

{endpoints}

## 🔐 인증

모든 API는 JWT 토큰 기반 인증을 사용합니다.

### 인증 헤더
```
Authorization: Bearer <access_token>
```

### 토큰 갱신
액세스 토큰이 만료되면 리프레시 토큰을 사용하여 새로운 토큰을 발급받을 수 있습니다.

## 📊 응답 형식

### 성공 응답
```json
{{
  "success": true,
  "data": {{
    // 응답 데이터
  }}
}}
```

### 오류 응답
```json
{{
  "success": false,
  "error": {{
    "code": "ERROR_CODE",
    "message": "오류 메시지"
  }}
}}
```

## 🔒 보안

- 모든 API는 HTTPS를 통해 제공됩니다
- Rate limiting이 적용됩니다
- 입력 데이터는 검증됩니다
- 민감한 정보는 로그에 기록되지 않습니다

---

**© 2025 Your Program. All rights reserved.**
"""
    
    def _group_endpoints(self) -> Dict[str, List[Dict[str, Any]]]:
        """엔드포인트 그룹화"""
        groups = {}
        
        for endpoint in self.endpoints:
            # 경로에서 그룹 추출
            path_parts = endpoint['path'].split('/')
            if len(path_parts) > 2:
                group = path_parts[2].title()  # /api/auth/login -> Auth
            else:
                group = 'General'
            
            if group not in groups:
                groups[group] = []
            
            groups[group].append(endpoint)
        
        return groups
    
    def _generate_endpoints_section(self, grouped_endpoints: Dict[str, List[Dict[str, Any]]]) -> str:
        """엔드포인트 섹션 생성"""
        sections = []
        
        # 목차 생성
        toc_items = []
        for group in sorted(grouped_endpoints.keys()):
            toc_items.append(f"- [{group} API](#{group.lower()}-api)")
        sections.append("## 📋 API 목록\n" + "\n".join(toc_items) + "\n")
        
        # 각 그룹별 섹션 생성
        for group, endpoints in sorted(grouped_endpoints.items()):
            section = self._generate_group_section(group, endpoints)
            sections.append(section)
        
        return "\n".join(sections)
    
    def _generate_group_section(self, group: str, endpoints: List[Dict[str, Any]]) -> str:
        """그룹별 섹션 생성"""
        section = f"## {group} API\n\n"
        
        for endpoint in sorted(endpoints, key=lambda x: x['path']):
            section += self._generate_endpoint_doc(endpoint)
            section += "\n\n"
        
        return section
    
    def _generate_endpoint_doc(self, endpoint: Dict[str, Any]) -> str:
        """개별 엔드포인트 문서 생성"""
        doc = f"### {endpoint['name'].replace('_', ' ').title()}\n\n"
        
        # 기본 정보
        doc += f"**Endpoint**: `{endpoint['method']} {endpoint['path']}`\n\n"
        
        # 설명
        if endpoint['docstring']:
            doc += f"{endpoint['docstring']}\n\n"
        
        # 인증 요구사항
        if endpoint['auth_required']:
            doc += "**인증**: 필요\n\n"
        
        # 권한 요구사항
        if endpoint['permissions']:
            doc += f"**권한**: {', '.join(endpoint['permissions'])}\n\n"
        
        # Rate limiting
        if endpoint['rate_limit']:
            doc += f"**Rate Limit**: {endpoint['rate_limit']} requests/min\n\n"
        
        # 매개변수
        if endpoint['parameters']:
            doc += "**Parameters**:\n"
            for param in endpoint['parameters']:
                doc += f"- `{param['name']}` ({param['type']}) - {param.get('description', 'No description')}\n"
            doc += "\n"
        
        # 예시 요청
        doc += "**Example Request**:\n"
        doc += "```http\n"
        doc += f"{endpoint['method']} {endpoint['path']}\n"
        if endpoint['auth_required']:
            doc += "Authorization: Bearer <access_token>\n"
        doc += "Content-Type: application/json\n\n"
        
        # 요청 본문 예시
        if endpoint['parameters']:
            body = {}
            for param in endpoint['parameters']:
                if param['type'] == 'str':
                    body[param['name']] = "example_value"
                elif param['type'] == 'int':
                    body[param['name']] = 123
                elif param['type'] == 'bool':
                    body[param['name']] = True
                else:
                    body[param['name']] = "value"
            
            doc += json.dumps(body, indent=2, ensure_ascii=False)
        
        doc += "\n```\n\n"
        
        # 예시 응답
        doc += "**Example Response**:\n"
        doc += "```json\n"
        doc += "{\n"
        doc += '  "success": true,\n'
        doc += '  "data": {\n'
        doc += '    "message": "Success"\n'
        doc += "  }\n"
        doc += "}\n"
        doc += "```\n"
        
        return doc
    
    def generate_openapi_spec(self):
        """OpenAPI 3.0 스펙 생성"""
        print("🔧 OpenAPI 스펙 생성 중...")
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Your Program API",
                "version": "1.0.0",
                "description": "Your Program REST API Documentation",
                "contact": {
                    "name": "Your Program Team",
                    "email": "support@yourprogram.com"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:5000",
                    "description": "Development server"
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                },
                "schemas": {
                    "Error": {
                        "type": "object",
                        "properties": {
                            "success": {
                                "type": "boolean",
                                "example": False
                            },
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {
                                        "type": "string",
                                        "example": "AUTH_INVALID_CREDENTIALS"
                                    },
                                    "message": {
                                        "type": "string",
                                        "example": "Invalid credentials"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # 엔드포인트를 OpenAPI 형식으로 변환
        for endpoint in self.endpoints:
            path_item = self._convert_to_openapi_path(endpoint)
            
            if endpoint['path'] not in spec['paths']:
                spec['paths'][endpoint['path']] = {}
            
            spec['paths'][endpoint['path']][endpoint['method'].lower()] = path_item
        
        # 파일 저장
        output_file = self.output_dir / 'openapi.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        
        print(f"✅ OpenAPI 스펙 생성 완료: {output_file}")
    
    def _convert_to_openapi_path(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """엔드포인트를 OpenAPI 경로 아이템으로 변환"""
        path_item = {
            "summary": endpoint['name'].replace('_', ' ').title(),
            "description": endpoint['docstring'] or f"{endpoint['method']} {endpoint['path']}",
            "tags": [endpoint['path'].split('/')[2] if len(endpoint['path'].split('/')) > 2 else 'general'],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {
                                        "type": "boolean",
                                        "example": True
                                    },
                                    "data": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Bad Request",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Error"
                            }
                        }
                    }
                },
                "401": {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Error"
                            }
                        }
                    }
                }
            }
        }
        
        # 인증 요구사항
        if endpoint['auth_required']:
            path_item["security"] = [{"bearerAuth": []}]
        
        # 매개변수
        if endpoint['parameters']:
            path_item["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
            }
            
            for param in endpoint['parameters']:
                param_type = self._convert_type_to_openapi(param['type'])
                path_item["requestBody"]["content"]["application/json"]["schema"]["properties"][param['name']] = {
                    "type": param_type,
                    "description": param.get('description', '')
                }
                
                if param.get('required', True):
                    path_item["requestBody"]["content"]["application/json"]["schema"]["required"].append(param['name'])
        
        return path_item
    
    def _convert_type_to_openapi(self, type_str: str) -> str:
        """Python 타입을 OpenAPI 타입으로 변환"""
        type_mapping = {
            'str': 'string',
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'list': 'array',
            'dict': 'object'
        }
        
        return type_mapping.get(type_str.lower(), 'string')
    
    def generate_postman_collection(self):
        """Postman 컬렉션 생성"""
        print("📮 Postman 컬렉션 생성 중...")
        
        collection = {
            "info": {
                "name": "Your Program API",
                "description": "Your Program REST API Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost:5000",
                    "type": "string"
                },
                {
                    "key": "access_token",
                    "value": "",
                    "type": "string"
                }
            ],
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            },
            "item": []
        }
        
        # 엔드포인트 그룹화
        grouped_endpoints = self._group_endpoints()
        
        # 각 그룹별로 폴더 생성
        for group, endpoints in grouped_endpoints.items():
            folder = {
                "name": group,
                "item": []
            }
            
            for endpoint in endpoints:
                request = self._convert_to_postman_request(endpoint)
                folder["item"].append(request)
            
            collection["item"].append(folder)
        
        # 파일 저장
        output_file = self.output_dir / 'postman_collection.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Postman 컬렉션 생성 완료: {output_file}")
    
    def _convert_to_postman_request(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """엔드포인트를 Postman 요청으로 변환"""
        request = {
            "name": endpoint['name'].replace('_', ' ').title(),
            "request": {
                "method": endpoint['method'],
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "url": {
                    "raw": "{{base_url}}" + endpoint['path'],
                    "host": ["{{base_url}}"],
                    "path": endpoint['path'].split('/')[1:]
                }
            }
        }
        
        # 인증 요구사항
        if endpoint['auth_required']:
            request["request"]["auth"] = {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            }
        
        # 요청 본문
        if endpoint['parameters']:
            body = {}
            for param in endpoint['parameters']:
                if param['type'] == 'str':
                    body[param['name']] = "example_value"
                elif param['type'] == 'int':
                    body[param['name']] = 123
                elif param['type'] == 'bool':
                    body[param['name']] = True
                else:
                    body[param['name']] = "value"
            
            request["request"]["body"] = {
                "mode": "raw",
                "raw": json.dumps(body, indent=2, ensure_ascii=False),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }
        
        return request
    
    def generate_all_docs(self):
        """모든 문서 생성"""
        print("🚀 API 문서 자동 생성 시작...")
        
        # 엔드포인트 스캔
        self.scan_endpoints()
        
        # 문서 생성
        self.generate_markdown_docs()
        self.generate_openapi_spec()
        self.generate_postman_collection()
        
        print("🎉 모든 API 문서 생성 완료!")

def main():
    """메인 함수"""
    generator = APIDocGenerator()
    generator.generate_all_docs()

if __name__ == "__main__":
    main() 