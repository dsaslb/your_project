import os
import json
import inspect
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Flask
from flask_restx import Api, Resource, fields
import yaml

class APIDocumentationGenerator:
    """API 문서 자동 생성기"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.api_endpoints = []
        self.models = {}
        self.base_url = "http://localhost:5000"
        
    def scan_app_routes(self, app: Flask) -> List[Dict[str, Any]]:
        """Flask 앱의 모든 라우트를 스캔하여 API 엔드포인트 정보 추출"""
        endpoints = []
        
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                endpoint_info = {
                    'path': rule.rule,
                    'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                    'endpoint': rule.endpoint,
                    'function': app.view_functions.get(rule.endpoint)
                }
                endpoints.append(endpoint_info)
        
        return endpoints
    
    def extract_function_docstring(self, func) -> Dict[str, str]:
        """함수의 docstring에서 API 정보 추출"""
        if not func or not hasattr(func, '__doc__') or not func.__doc__:
            return {}
        
        docstring = func.__doc__
        info = {}
        
        # 요약 추출
        summary_match = re.search(r'@summary\s+(.+)', docstring)
        if summary_match:
            info['summary'] = summary_match.group(1).strip()
        
        # 설명 추출
        description_match = re.search(r'@description\s+(.+)', docstring)
        if description_match:
            info['description'] = description_match.group(1).strip()
        
        # 태그 추출
        tag_match = re.search(r'@tag\s+(.+)', docstring)
        if tag_match:
            info['tag'] = tag_match.group(1).strip()
        
        # 파라미터 추출
        params = re.findall(r'@param\s+(\w+)\s+(.+)', docstring)
        if params:
            info['parameters'] = {name: desc.strip() for name, desc in params}
        
        # 응답 추출
        response_match = re.search(r'@response\s+(\d+)\s+(.+)', docstring)
        if response_match:
            info['response'] = {
                'code': response_match.group(1),
                'description': response_match.group(2).strip()
            }
        
        return info
    
    def generate_openapi_spec(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """OpenAPI 3.0 스펙 생성"""
        paths = {}
        
        for endpoint in endpoints:
            path = endpoint['path']
            methods = endpoint['methods']
            func = endpoint['function']
            
            if path not in paths:
                paths[path] = {}
            
            # 각 HTTP 메서드에 대한 정보 생성
            for method in methods:
                method_lower = method.lower()
                
                # 함수 정보 추출
                func_info = self.extract_function_docstring(func)
                
                # 기본 정보 설정
                path_info = {
                    'tags': [func_info.get('tag', '기타')],
                    'summary': func_info.get('summary', f'{method} {path}'),
                    'description': func_info.get('description', ''),
                    'responses': {
                        '200': {
                            'description': '성공',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'success': {'type': 'boolean'},
                                            'data': {'type': 'object'}
                                        }
                                    }
                                }
                            }
                        },
                        '400': {
                            'description': '잘못된 요청',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/Error'
                                    }
                                }
                            }
                        },
                        '401': {
                            'description': '인증 실패',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/Error'
                                    }
                                }
                            }
                        },
                        '500': {
                            'description': '서버 오류',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/Error'
                                    }
                                }
                            }
                        }
                    }
                }
                
                # POST/PUT 메서드의 경우 requestBody 추가
                if method_lower in ['post', 'put', 'patch']:
                    path_info['requestBody'] = {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {}
                                }
                            }
                        }
                    }
                
                # 파라미터가 있는 경우 추가
                if func_info.get('parameters'):
                    path_info['parameters'] = []
                    for param_name, param_desc in func_info['parameters'].items():
                        path_info['parameters'].append({
                            'name': param_name,
                            'in': 'query',
                            'description': param_desc,
                            'required': False,
                            'schema': {'type': 'string'}
                        })
                
                paths[path][method_lower] = path_info
        
        return {
            'openapi': '3.0.0',
            'info': {
                'title': '퀀텀 비즈니스 관리 시스템 API',
                'description': '자동 생성된 API 문서',
                'version': '1.0.0',
                'contact': {
                    'name': 'API 지원팀',
                    'email': 'support@quantum-business.com'
                }
            },
            'servers': [
                {
                    'url': self.base_url,
                    'description': '개발 서버'
                }
            ],
            'paths': paths,
            'components': {
                'securitySchemes': {
                    'BearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT'
                    }
                },
                'schemas': {
                    'Error': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'message': {'type': 'string'},
                            'error_code': {'type': 'string'}
                        }
                    },
                    'Success': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'message': {'type': 'string'},
                            'data': {'type': 'object'}
                        }
                    }
                }
            },
            'tags': [
                {'name': '인증', 'description': '사용자 인증 관련 API'},
                {'name': '대시보드', 'description': '대시보드 관련 API'},
                {'name': '매장 관리', 'description': '매장 정보 관리 API'},
                {'name': '재고 관리', 'description': '재고 현황 관리 API'},
                {'name': '주문 관리', 'description': '주문 처리 관리 API'},
                {'name': '스케줄 관리', 'description': '직원 스케줄 관리 API'},
                {'name': '알림', 'description': '시스템 알림 관리 API'},
                {'name': '사용자 관리', 'description': '사용자 계정 관리 API'},
                {'name': '기타', 'description': '기타 API'}
            ]
        }
    
    def generate_markdown_docs(self, openapi_spec: Dict[str, Any]) -> str:
        """Markdown 형식의 API 문서 생성"""
        md_content = []
        
        # 헤더
        md_content.append(f"# {openapi_spec['info']['title']}")
        md_content.append(f"**버전**: {openapi_spec['info']['version']}")
        md_content.append(f"**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_content.append("")
        md_content.append(openapi_spec['info']['description'])
        md_content.append("")
        
        # 서버 정보
        md_content.append("## 서버 정보")
        for server in openapi_spec['servers']:
            md_content.append(f"- **{server['description']}**: `{server['url']}`")
        md_content.append("")
        
        # 인증 정보
        md_content.append("## 인증")
        md_content.append("이 API는 JWT Bearer 토큰을 사용한 인증을 지원합니다.")
        md_content.append("")
        md_content.append("```http")
        md_content.append("Authorization: Bearer <your-token>")
        md_content.append("```")
        md_content.append("")
        
        # 태그별로 API 그룹화
        paths = openapi_spec['paths']
        tags = {tag['name']: tag['description'] for tag in openapi_spec['tags']}
        
        for tag_name, tag_desc in tags.items():
            md_content.append(f"## {tag_name}")
            md_content.append(tag_desc)
            md_content.append("")
            
            # 해당 태그의 API들 찾기
            for path, methods in paths.items():
                for method, method_info in methods.items():
                    if tag_name in method_info.get('tags', []):
                        # API 엔드포인트 문서 생성
                        md_content.append(f"### {method.upper()} {path}")
                        md_content.append("")
                        
                        if method_info.get('summary'):
                            md_content.append(f"**요약**: {method_info['summary']}")
                            md_content.append("")
                        
                        if method_info.get('description'):
                            md_content.append(f"**설명**: {method_info['description']}")
                            md_content.append("")
                        
                        # 파라미터
                        if method_info.get('parameters'):
                            md_content.append("**파라미터**:")
                            md_content.append("")
                            md_content.append("| 이름 | 타입 | 필수 | 설명 |")
                            md_content.append("|------|------|------|------|")
                            for param in method_info['parameters']:
                                required = "예" if param.get('required', False) else "아니오"
                                md_content.append(f"| {param['name']} | {param['schema']['type']} | {required} | {param['description']} |")
                            md_content.append("")
                        
                        # 요청 본문
                        if method_info.get('requestBody'):
                            md_content.append("**요청 본문**:")
                            md_content.append("")
                            md_content.append("```json")
                            md_content.append("{}")
                            md_content.append("```")
                            md_content.append("")
                        
                        # 응답
                        md_content.append("**응답**:")
                        md_content.append("")
                        for status_code, response in method_info['responses'].items():
                            md_content.append(f"**{status_code}**: {response['description']}")
                            if 'content' in response:
                                md_content.append("```json")
                                md_content.append("{}")
                                md_content.append("```")
                            md_content.append("")
                        
                        md_content.append("---")
                        md_content.append("")
        
        return "\n".join(md_content)
    
    def save_documentation(self, openapi_spec: Dict[str, Any], output_dir: str = "docs"):
        """문서를 파일로 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        # OpenAPI JSON 저장
        json_path = os.path.join(output_dir, "openapi.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
        
        # OpenAPI YAML 저장
        yaml_path = os.path.join(output_dir, "openapi.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
        
        # Markdown 저장
        md_content = self.generate_markdown_docs(openapi_spec)
        md_path = os.path.join(output_dir, "API_Documentation.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"📄 문서가 저장되었습니다:")
        print(f"   - JSON: {json_path}")
        print(f"   - YAML: {yaml_path}")
        print(f"   - Markdown: {md_path}")
    
    def generate_from_app(self, app: Flask, output_dir: str = "docs"):
        """Flask 앱에서 API 문서 생성"""
        print("🔍 API 엔드포인트 스캔 중...")
        endpoints = self.scan_app_routes(app)
        print(f"📊 {len(endpoints)}개의 엔드포인트를 발견했습니다.")
        
        print("📝 OpenAPI 스펙 생성 중...")
        openapi_spec = self.generate_openapi_spec(endpoints)
        
        print("💾 문서 저장 중...")
        self.save_documentation(openapi_spec, output_dir)
        
        return openapi_spec

# 사용 예시
if __name__ == "__main__":
    # Flask 앱 예시 (실제 앱으로 교체)
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/api/test')
    def test_endpoint():
        """
        @summary 테스트 엔드포인트
        @description API 문서 생성 테스트용 엔드포인트
        @tag 기타
        @param name 사용자 이름
        @response 200 성공
        """
        return {"message": "test"}
    
    # 문서 생성기 초기화 및 실행
    generator = APIDocumentationGenerator()
    generator.generate_from_app(app) 