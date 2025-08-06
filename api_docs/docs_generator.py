import os
import json
import yaml
import inspect
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from flask import Flask, Blueprint
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ApiEndpoint:
    """API 엔드포인트 정보"""
    path: str
    methods: List[str]
    function_name: str
    docstring: str
    parameters: List[Dict[str, Any]]
    responses: Dict[str, Any]
    tags: List[str]
    summary: str
    description: str

@dataclass
class ApiDocsConfig:
    """API 문서 설정"""
    title: str = "비즈니스 관리 시스템 API"
    version: str = "1.0.0"
    description: str = "비즈니스 관리 시스템의 REST API 문서"
    contact_name: str = "API Support"
    contact_email: str = "support@example.com"
    server_url: str = "http://localhost:5000"
    output_dir: str = "data/api_docs"
    enable_swagger_ui: bool = True
    enable_redoc: bool = True
    enable_postman: bool = True
    enable_insomnia: bool = True

class ApiDocsGenerator:
    """API 문서 생성기 클래스"""
    
    def __init__(self, app: Flask, config: ApiDocsConfig):
        self.app = app
        self.config = config
        self.endpoints: List[ApiEndpoint] = []
        
        # 출력 디렉토리 생성
        os.makedirs(config.output_dir, exist_ok=True)
        
        logger.info("API 문서 생성기가 초기화되었습니다")
    
    def scan_endpoints(self):
        """Flask 앱의 모든 엔드포인트 스캔"""
        try:
            for rule in self.app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    self._process_endpoint(rule)
            
            logger.info(f"총 {len(self.endpoints)}개의 엔드포인트를 스캔했습니다")
            
        except Exception as e:
            logger.error(f"엔드포인트 스캔 실패: {str(e)}")
    
    def _process_endpoint(self, rule):
        """개별 엔드포인트 처리"""
        try:
            # 뷰 함수 가져오기
            view_func = self.app.view_functions.get(rule.endpoint)
            if not view_func:
                return
            
            # 메서드 목록
            methods = list(rule.methods - {'HEAD', 'OPTIONS'})
            
            # 경로 파라미터 추출
            path_params = []
            for param in rule.arguments:
                path_params.append({
                    "name": param,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                })
            
            # 함수 정보 추출
            function_name = view_func.__name__
            docstring = inspect.getdoc(view_func) or ""
            
            # 태그 추출 (Blueprint 이름 기반)
            tags = []
            if hasattr(view_func, '__blueprint__'):
                tags.append(view_func.__blueprint__.name)
            else:
                tags.append("default")
            
            # 요약 및 설명 추출
            summary = self._extract_summary(docstring)
            description = self._extract_description(docstring)
            
            # 응답 스키마 추출
            responses = self._extract_responses(docstring)
            
            endpoint = ApiEndpoint(
                path=str(rule),
                methods=methods,
                function_name=function_name,
                docstring=docstring,
                parameters=path_params,
                responses=responses,
                tags=tags,
                summary=summary,
                description=description
            )
            
            self.endpoints.append(endpoint)
            
        except Exception as e:
            logger.error(f"엔드포인트 처리 실패: {rule} - {str(e)}")
    
    def _extract_summary(self, docstring: str) -> str:
        """docstring에서 요약 추출"""
        if not docstring:
            return ""
        
        lines = docstring.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('@') and not line.startswith(':'):
                return line
        
        return ""
    
    def _extract_description(self, docstring: str) -> str:
        """docstring에서 설명 추출"""
        if not docstring:
            return ""
        
        lines = docstring.strip().split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('@') and not line.startswith(':'):
                description_lines.append(line)
        
        return '\n'.join(description_lines)
    
    def _extract_responses(self, docstring: str) -> Dict[str, Any]:
        """docstring에서 응답 정보 추출"""
        responses = {
            "200": {
                "description": "성공",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"},
                                "data": {"type": "object"}
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "잘못된 요청",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "500": {
                "description": "서버 오류",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
        
        # docstring에서 응답 정보 파싱
        if "@response" in docstring:
            response_pattern = r'@response\s+(\d+)\s+(.+)'
            matches = re.findall(response_pattern, docstring)
            for code, desc in matches:
                responses[code] = {
                    "description": desc.strip(),
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
        
        return responses
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """OpenAPI 3.0 스펙 생성"""
        try:
            # 기본 정보
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": self.config.title,
                    "version": self.config.version,
                    "description": self.config.description,
                    "contact": {
                        "name": self.config.contact_name,
                        "email": self.config.contact_email
                    }
                },
                "servers": [
                    {
                        "url": self.config.server_url,
                        "description": "개발 서버"
                    }
                ],
                "paths": {},
                "components": {
                    "schemas": {},
                    "securitySchemes": {
                        "bearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT"
                        }
                    }
                },
                "tags": []
            }
            
            # 태그 정보 수집
            tags_set = set()
            for endpoint in self.endpoints:
                tags_set.update(endpoint.tags)
            
            for tag in sorted(tags_set):
                openapi_spec["tags"].append({
                    "name": tag,
                    "description": f"{tag} 관련 API"
                })
            
            # 엔드포인트 정보 추가
            for endpoint in self.endpoints:
                path = endpoint.path
                if path not in openapi_spec["paths"]:
                    openapi_spec["paths"][path] = {}
                
                for method in endpoint.methods:
                    method_lower = method.lower()
                    openapi_spec["paths"][path][method_lower] = {
                        "tags": endpoint.tags,
                        "summary": endpoint.summary,
                        "description": endpoint.description,
                        "parameters": endpoint.parameters,
                        "responses": endpoint.responses
                    }
                    
                    # POST/PUT 메서드에 요청 본문 추가
                    if method_lower in ['post', 'put', 'patch']:
                        openapi_spec["paths"][path][method_lower]["requestBody"] = {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "data": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
            
            return openapi_spec
            
        except Exception as e:
            logger.error(f"OpenAPI 스펙 생성 실패: {str(e)}")
            return {}
    
    def save_openapi_spec(self, spec: Dict[str, Any]):
        """OpenAPI 스펙을 파일로 저장"""
        try:
            # JSON 형식으로 저장
            json_path = os.path.join(self.config.output_dir, "openapi.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(spec, f, ensure_ascii=False, indent=2)
            
            # YAML 형식으로 저장
            yaml_path = os.path.join(self.config.output_dir, "openapi.yaml")
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(spec, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"OpenAPI 스펙이 저장되었습니다: {json_path}, {yaml_path}")
            
        except Exception as e:
            logger.error(f"OpenAPI 스펙 저장 실패: {str(e)}")
    
    def generate_markdown_docs(self, spec: Dict[str, Any]):
        """마크다운 문서 생성"""
        try:
            md_content = []
            
            # 헤더
            md_content.append(f"# {spec['info']['title']}")
            md_content.append(f"**버전**: {spec['info']['version']}")
            md_content.append(f"**설명**: {spec['info']['description']}")
            md_content.append(f"**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            md_content.append("")
            
            # 서버 정보
            md_content.append("## 서버 정보")
            for server in spec.get('servers', []):
                md_content.append(f"- **URL**: {server['url']}")
                md_content.append(f"- **설명**: {server.get('description', '')}")
            md_content.append("")
            
            # 인증 정보
            md_content.append("## 인증")
            md_content.append("이 API는 JWT Bearer 토큰을 사용합니다.")
            md_content.append("")
            md_content.append("```http")
            md_content.append("Authorization: Bearer <your-token>")
            md_content.append("```")
            md_content.append("")
            
            # 태그별 엔드포인트
            paths = spec.get('paths', {})
            tags = spec.get('tags', [])
            
            for tag in tags:
                tag_name = tag['name']
                md_content.append(f"## {tag_name}")
                md_content.append(tag.get('description', ''))
                md_content.append("")
                
                # 해당 태그의 엔드포인트 찾기
                for path, methods in paths.items():
                    for method, details in methods.items():
                        if tag_name in details.get('tags', []):
                            md_content.append(f"### {method.upper()} {path}")
                            md_content.append("")
                            
                            if details.get('summary'):
                                md_content.append(f"**요약**: {details['summary']}")
                                md_content.append("")
                            
                            if details.get('description'):
                                md_content.append(f"**설명**: {details['description']}")
                                md_content.append("")
                            
                            # 파라미터
                            if details.get('parameters'):
                                md_content.append("**파라미터**:")
                                md_content.append("")
                                for param in details['parameters']:
                                    md_content.append(f"- `{param['name']}` ({param['in']}) - {param.get('description', '')}")
                                md_content.append("")
                            
                            # 응답
                            if details.get('responses'):
                                md_content.append("**응답**:")
                                md_content.append("")
                                for code, response in details['responses'].items():
                                    md_content.append(f"- `{code}`: {response.get('description', '')}")
                                md_content.append("")
                            
                            md_content.append("---")
                            md_content.append("")
            
            # 파일 저장
            md_path = os.path.join(self.config.output_dir, "api_documentation.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            
            logger.info(f"마크다운 문서가 생성되었습니다: {md_path}")
            
        except Exception as e:
            logger.error(f"마크다운 문서 생성 실패: {str(e)}")
    
    def generate_postman_collection(self, spec: Dict[str, Any]):
        """Postman 컬렉션 생성"""
        try:
            collection = {
                "info": {
                    "name": spec['info']['title'],
                    "description": spec['info']['description'],
                    "version": spec['info']['version'],
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                },
                "variable": [
                    {
                        "key": "base_url",
                        "value": self.config.server_url,
                        "type": "string"
                    }
                ],
                "item": []
            }
            
            # 태그별로 그룹화
            paths = spec.get('paths', {})
            tags = spec.get('tags', [])
            
            for tag in tags:
                tag_name = tag['name']
                tag_items = []
                
                for path, methods in paths.items():
                    for method, details in methods.items():
                        if tag_name in details.get('tags', []):
                            item = {
                                "name": f"{method.upper()} {path}",
                                "request": {
                                    "method": method.upper(),
                                    "header": [
                                        {
                                            "key": "Content-Type",
                                            "value": "application/json"
                                        }
                                    ],
                                    "url": {
                                        "raw": f"{{{{base_url}}}}{path}",
                                        "host": ["{{base_url}}"],
                                        "path": path.strip('/').split('/')
                                    }
                                }
                            }
                            
                            # 요청 본문 추가
                            if method.lower() in ['post', 'put', 'patch']:
                                item["request"]["body"] = {
                                    "mode": "raw",
                                    "raw": "{\n  \"data\": {}\n}",
                                    "options": {
                                        "raw": {
                                            "language": "json"
                                        }
                                    }
                                }
                            
                            tag_items.append(item)
                
                if tag_items:
                    collection["item"].append({
                        "name": tag_name,
                        "item": tag_items
                    })
            
            # 파일 저장
            postman_path = os.path.join(self.config.output_dir, "postman_collection.json")
            with open(postman_path, 'w', encoding='utf-8') as f:
                json.dump(collection, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Postman 컬렉션이 생성되었습니다: {postman_path}")
            
        except Exception as e:
            logger.error(f"Postman 컬렉션 생성 실패: {str(e)}")
    
    def generate_insomnia_collection(self, spec: Dict[str, Any]):
        """Insomnia 컬렉션 생성"""
        try:
            collection = {
                "_type": "export",
                "__export_format": 4,
                "__export_date": datetime.now().isoformat(),
                "__export_source": "insomnia.desktop.app:v2023.5.8",
                "resources": [
                    {
                        "_id": "req_root",
                        "parentId": "wrk_api",
                        "modified": int(datetime.now().timestamp() * 1000),
                        "created": int(datetime.now().timestamp() * 1000),
                        "url": "{{ _.base_url }}",
                        "name": "Root",
                        "description": "",
                        "method": "GET",
                        "body": {},
                        "parameters": [],
                        "headers": [],
                        "authentication": {},
                        "metaSortKey": -1000000000000,
                        "isPrivate": False,
                        "settingStoreCookies": True,
                        "settingSendCookies": True,
                        "settingDisableRenderRequestBody": False,
                        "settingEncodeUrl": True,
                        "settingRebuildPath": True,
                        "settingFollowRedirects": "global",
                        "_type": "request"
                    }
                ]
            }
            
            # 워크스페이스 추가
            workspace = {
                "_id": "wrk_api",
                "parentId": None,
                "modified": int(datetime.now().timestamp() * 1000),
                "created": int(datetime.now().timestamp() * 1000),
                "name": spec['info']['title'],
                "description": spec['info']['description'],
                "scope": "collection",
                "_type": "workspace"
            }
            collection["resources"].append(workspace)
            
            # 환경 추가
            environment = {
                "_id": "env_api",
                "parentId": "wrk_api",
                "modified": int(datetime.now().timestamp() * 1000),
                "created": int(datetime.now().timestamp() * 1000),
                "name": "API Environment",
                "data": {
                    "base_url": self.config.server_url
                },
                "dataPropertyOrder": {
                    "&": ["base_url"]
                },
                "color": None,
                "isPrivate": False,
                "metaSortKey": 1000000000000,
                "_type": "environment"
            }
            collection["resources"].append(environment)
            
            # 파일 저장
            insomnia_path = os.path.join(self.config.output_dir, "insomnia_collection.json")
            with open(insomnia_path, 'w', encoding='utf-8') as f:
                json.dump(collection, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Insomnia 컬렉션이 생성되었습니다: {insomnia_path}")
            
        except Exception as e:
            logger.error(f"Insomnia 컬렉션 생성 실패: {str(e)}")
    
    def generate_all_docs(self):
        """모든 문서 생성"""
        try:
            # 엔드포인트 스캔
            self.scan_endpoints()
            
            # OpenAPI 스펙 생성
            spec = self.generate_openapi_spec()
            if not spec:
                logger.error("OpenAPI 스펙 생성에 실패했습니다")
                return False
            
            # 문서 저장
            self.save_openapi_spec(spec)
            
            # 추가 문서 생성
            if self.config.enable_swagger_ui:
                self.generate_markdown_docs(spec)
            
            if self.config.enable_postman:
                self.generate_postman_collection(spec)
            
            if self.config.enable_insomnia:
                self.generate_insomnia_collection(spec)
            
            logger.info("모든 API 문서가 생성되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"문서 생성 실패: {str(e)}")
            return False 