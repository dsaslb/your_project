#!/usr/bin/env python3
"""
API 문서 생성 스크립트
퀀텀 비즈니스 관리 시스템의 API 문서를 자동으로 생성합니다.
"""

import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.documentation_generator import APIDocumentationGenerator
from api.api_documentation import api_documentation

def create_api_docs_directory():
    """API 문서 디렉토리 생성"""
    docs_dir = project_root / "docs" / "api"
    docs_dir.mkdir(parents=True, exist_ok=True)
    return docs_dir

def generate_static_docs(docs_dir):
    """정적 API 문서 생성"""
    print("📝 정적 API 문서 생성 중...")
    
    # OpenAPI JSON 저장
    json_path = docs_dir / "openapi.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(api_documentation, f, ensure_ascii=False, indent=2)
    
    # OpenAPI YAML 저장
    yaml_path = docs_dir / "openapi.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(api_documentation, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ 정적 문서 생성 완료:")
    print(f"   - JSON: {json_path}")
    print(f"   - YAML: {yaml_path}")

def generate_markdown_docs(docs_dir):
    """Markdown 형식의 API 문서 생성"""
    print("📄 Markdown 문서 생성 중...")
    
    generator = APIDocumentationGenerator()
    md_content = generator.generate_markdown_docs(api_documentation)
    
    md_path = docs_dir / "API_Documentation.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Markdown 문서 생성 완료: {md_path}")

def generate_postman_collection(docs_dir):
    """Postman 컬렉션 생성"""
    print("📮 Postman 컬렉션 생성 중...")
    
    collection = {
        "info": {
            "name": "퀀텀 비즈니스 관리 시스템 API",
            "description": "비즈니스 관리를 위한 종합 API 컬렉션",
            "version": "1.0.0",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:5000",
                "type": "string"
            },
            {
                "key": "auth_token",
                "value": "",
                "type": "string"
            }
        ],
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{auth_token}}",
                    "type": "string"
                }
            ]
        },
        "item": []
    }
    
    # API 엔드포인트를 Postman 컬렉션으로 변환
    for path, methods in api_documentation["paths"].items():
        for method, method_info in methods.items():
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
                        "raw": "{{base_url}}" + path,
                        "host": ["{{base_url}}"],
                        "path": path.strip("/").split("/")
                    }
                }
            }
            
            # 요청 본문이 있는 경우 추가
            if method_info.get("requestBody"):
                item["request"]["body"] = {
                    "mode": "raw",
                    "raw": "{}",
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }
            
            # 파라미터가 있는 경우 추가
            if method_info.get("parameters"):
                item["request"]["url"]["query"] = []
                for param in method_info["parameters"]:
                    item["request"]["url"]["query"].append({
                        "key": param["name"],
                        "value": "",
                        "description": param.get("description", ""),
                        "disabled": not param.get("required", False)
                    })
            
            collection["item"].append(item)
    
    # Postman 컬렉션 저장
    postman_path = docs_dir / "postman_collection.json"
    with open(postman_path, 'w', encoding='utf-8') as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Postman 컬렉션 생성 완료: {postman_path}")

def generate_insomnia_collection(docs_dir):
    """Insomnia 컬렉션 생성"""
    print("🌙 Insomnia 컬렉션 생성 중...")
    
    insomnia_collection = {
        "_type": "export",
        "__export_format": 4,
        "__export_date": datetime.now().isoformat(),
        "__export_source": "insomnia.desktop.app:v2023.5.8",
        "resources": [
            {
                "_id": "req_root",
                "parentId": "wrk_quantum",
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
                "metaSortKey": -int(datetime.now().timestamp() * 1000),
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
    
    # API 엔드포인트를 Insomnia 리소스로 변환
    for path, methods in api_documentation["paths"].items():
        for method, method_info in methods.items():
            resource_id = f"req_{method}_{path.replace('/', '_').replace('-', '_')}"
            
            resource = {
                "_id": resource_id,
                "parentId": "wrk_quantum",
                "modified": int(datetime.now().timestamp() * 1000),
                "created": int(datetime.now().timestamp() * 1000),
                "url": "{{ _.base_url }}" + path,
                "name": f"{method.upper()} {path}",
                "description": method_info.get("summary", ""),
                "method": method.upper(),
                "body": {},
                "parameters": [],
                "headers": [
                    {
                        "name": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "authentication": {
                    "type": "bearer",
                    "token": "{{ _.auth_token }}"
                },
                "metaSortKey": -int(datetime.now().timestamp() * 1000),
                "isPrivate": False,
                "settingStoreCookies": True,
                "settingSendCookies": True,
                "settingDisableRenderRequestBody": False,
                "settingEncodeUrl": True,
                "settingRebuildPath": True,
                "settingFollowRedirects": "global",
                "_type": "request"
            }
            
            insomnia_collection["resources"].append(resource)
    
    # Insomnia 컬렉션 저장
    insomnia_path = docs_dir / "insomnia_collection.json"
    with open(insomnia_path, 'w', encoding='utf-8') as f:
        json.dump(insomnia_collection, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Insomnia 컬렉션 생성 완료: {insomnia_path}")

def generate_readme(docs_dir):
    """API 문서 README 생성"""
    print("📖 README 생성 중...")
    
    readme_content = f"""# 퀀텀 비즈니스 관리 시스템 API 문서

## 개요

이 문서는 퀀텀 비즈니스 관리 시스템의 API 엔드포인트에 대한 설명을 제공합니다.

## 문서 버전

- **버전**: {api_documentation['info']['version']}
- **생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **OpenAPI 버전**: {api_documentation['openapi']}

## 서버 정보

"""
    
    for server in api_documentation["servers"]:
        readme_content += f"- **{server['description']}**: `{server['url']}`\n"
    
    readme_content += """
## 인증

이 API는 JWT Bearer 토큰을 사용한 인증을 지원합니다.

```http
Authorization: Bearer <your-token>
```

## 문서 형식

이 디렉토리에는 다음과 같은 형식의 API 문서가 포함되어 있습니다:

- **openapi.json**: OpenAPI 3.0 JSON 형식
- **openapi.yaml**: OpenAPI 3.0 YAML 형식
- **API_Documentation.md**: Markdown 형식의 상세 문서
- **postman_collection.json**: Postman 컬렉션
- **insomnia_collection.json**: Insomnia 컬렉션

## API 그룹

"""
    
    for tag in api_documentation["tags"]:
        readme_content += f"- **{tag['name']}**: {tag['description']}\n"
    
    readme_content += """
## 사용 방법

### Swagger UI 사용

1. API 문서 서버를 시작합니다:
   ```bash
   python api/api_documentation.py
   ```

2. 브라우저에서 다음 URL에 접속합니다:
   ```
   http://localhost:5000/api/docs
   ```

### Postman 사용

1. Postman을 엽니다
2. Import 버튼을 클릭합니다
3. `postman_collection.json` 파일을 선택합니다
4. 환경 변수를 설정합니다:
   - `base_url`: API 서버 URL
   - `auth_token`: 인증 토큰

### Insomnia 사용

1. Insomnia를 엽니다
2. Import/Export 메뉴에서 Import를 선택합니다
3. `insomnia_collection.json` 파일을 선택합니다
4. 환경 변수를 설정합니다

## 개발자 정보

- **연락처**: {api_documentation['info']['contact']['name']}
- **이메일**: {api_documentation['info']['contact']['email']}

## 라이선스

이 API는 MIT 라이선스 하에 배포됩니다.
""".format(
        contact_name=api_documentation['info']['contact']['name'],
        contact_email=api_documentation['info']['contact']['email']
    )
    
    readme_path = docs_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ README 생성 완료: {readme_path}")

def main():
    """메인 함수"""
    print("🚀 API 문서 생성 시작")
    print("=" * 50)
    
    # 문서 디렉토리 생성
    docs_dir = create_api_docs_directory()
    print(f"📁 문서 디렉토리: {docs_dir}")
    print()
    
    try:
        # 정적 문서 생성
        generate_static_docs(docs_dir)
        print()
        
        # Markdown 문서 생성
        generate_markdown_docs(docs_dir)
        print()
        
        # Postman 컬렉션 생성
        generate_postman_collection(docs_dir)
        print()
        
        # Insomnia 컬렉션 생성
        generate_insomnia_collection(docs_dir)
        print()
        
        # README 생성
        generate_readme(docs_dir)
        print()
        
        print("🎉 API 문서 생성 완료!")
        print("=" * 50)
        print(f"📂 생성된 파일들:")
        for file_path in docs_dir.glob("*"):
            if file_path.is_file():
                print(f"   - {file_path.name}")
        
        print()
        print("📖 문서를 확인하려면:")
        print(f"   - Swagger UI: http://localhost:5000/api/docs")
        print(f"   - Markdown: {docs_dir / 'API_Documentation.md'}")
        print(f"   - README: {docs_dir / 'README.md'}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 