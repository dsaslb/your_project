"""
API 문서 자동화 시스템
엔터프라이즈급 API 문서 생성, 관리, 배포 시스템
"""

import logging
import json
import yaml
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jinja2
import markdown
import requests
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import webbrowser
from urllib.parse import urljoin, urlparse
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocFormat(Enum):
    """문서 형식"""
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    JSON = "json"
    YAML = "yaml"
    OPENAPI = "openapi"

class DocTheme(Enum):
    """문서 테마"""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    CUSTOM = "custom"

@dataclass
class APIDocumentation:
    """API 문서 정보"""
    id: str
    version: str
    title: str
    description: str
    format: DocFormat
    theme: DocTheme
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    generated_at: datetime
    file_path: Optional[str] = None
    url: Optional[str] = None

@dataclass
class DocumentationTemplate:
    """문서 템플릿"""
    id: str
    name: str
    description: str
    format: DocFormat
    template_content: str
    css_styles: Optional[str] = None
    js_scripts: Optional[str] = None
    created_at: datetime = None

@dataclass
class CodeExample:
    """코드 예제"""
    language: str
    title: str
    code: str
    description: Optional[str] = None
    output: Optional[str] = None

class APIDocumentationGenerator:
    """API 문서 자동화 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.db_connection = None
        self.templates: Dict[str, DocumentationTemplate] = {}
        self.documentations: Dict[str, APIDocumentation] = {}
        self.jinja_env = None
        self.output_dir = config.get('output_dir', './api_docs')
        
        self._initialize_connections()
        self._setup_jinja_environment()
        self._load_templates()
        self._create_output_directory()
        self._setup_default_templates()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            # PostgreSQL 연결
            self.db_connection = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            
            logger.info("API 문서 생성기 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _setup_jinja_environment(self):
        """Jinja2 환경 설정"""
        try:
            template_dir = Path(__file__).parent / 'templates'
            template_dir.mkdir(exist_ok=True)
            
            self.jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(template_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # 커스텀 필터 추가
            self.jinja_env.filters['to_json'] = json.dumps
            self.jinja_env.filters['to_yaml'] = yaml.dump
            self.jinja_env.filters['markdown'] = markdown.markdown
            
        except Exception as e:
            logger.error(f"Jinja2 환경 설정 오류: {e}")
            raise
    
    def _load_templates(self):
        """템플릿 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM documentation_templates ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    template = DocumentationTemplate(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        format=DocFormat(row['format']),
                        template_content=row['template_content'],
                        css_styles=row['css_styles'],
                        js_scripts=row['js_scripts'],
                        created_at=row['created_at']
                    )
                    self.templates[template.id] = template
            
            logger.info(f"{len(self.templates)}개의 문서 템플릿 로드 완료")
            
        except Exception as e:
            logger.error(f"템플릿 로드 오류: {e}")
    
    def _create_output_directory(self):
        """출력 디렉토리 생성"""
        try:
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"출력 디렉토리 생성 완료: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"출력 디렉토리 생성 오류: {e}")
            raise
    
    def _setup_default_templates(self):
        """기본 템플릿 설정"""
        try:
            # HTML 기본 템플릿
            html_template = DocumentationTemplate(
                id=str(uuid.uuid4()),
                name="Default HTML Template",
                description="기본 HTML API 문서 템플릿",
                format=DocFormat.HTML,
                template_content=self._get_default_html_template(),
                css_styles=self._get_default_css_styles(),
                js_scripts=self._get_default_js_scripts(),
                created_at=datetime.now()
            )
            
            # Markdown 기본 템플릿
            markdown_template = DocumentationTemplate(
                id=str(uuid.uuid4()),
                name="Default Markdown Template",
                description="기본 Markdown API 문서 템플릿",
                format=DocFormat.MARKDOWN,
                template_content=self._get_default_markdown_template(),
                created_at=datetime.now()
            )
            
            # OpenAPI 기본 템플릿
            openapi_template = DocumentationTemplate(
                id=str(uuid.uuid4()),
                name="Default OpenAPI Template",
                description="기본 OpenAPI 3.0 템플릿",
                format=DocFormat.OPENAPI,
                template_content=self._get_default_openapi_template(),
                created_at=datetime.now()
            )
            
            self.templates[html_template.id] = html_template
            self.templates[markdown_template.id] = markdown_template
            self.templates[openapi_template.id] = openapi_template
            
            # 데이터베이스에 저장
            self._save_template_to_db(html_template)
            self._save_template_to_db(markdown_template)
            self._save_template_to_db(openapi_template)
            
            logger.info("기본 템플릿 설정 완료")
            
        except Exception as e:
            logger.error(f"기본 템플릿 설정 오류: {e}")
    
    def _get_default_html_template(self) -> str:
        """기본 HTML 템플릿"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ api_info.title }} - API 문서</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{{ api_info.title }}</h1>
            <p class="description">{{ api_info.description }}</p>
            <div class="version-info">
                <span class="version">버전: {{ api_info.version }}</span>
                <span class="status">상태: {{ api_info.status }}</span>
            </div>
        </header>
        
        <nav class="sidebar">
            <h3>목차</h3>
            <ul class="toc">
                {% for section in sections %}
                <li><a href="#{{ section.id }}">{{ section.title }}</a></li>
                {% endfor %}
            </ul>
        </nav>
        
        <main class="content">
            {% for section in sections %}
            <section id="{{ section.id }}" class="section">
                <h2>{{ section.title }}</h2>
                {% if section.description %}
                <p>{{ section.description }}</p>
                {% endif %}
                
                {% if section.endpoints %}
                <div class="endpoints">
                    {% for endpoint in section.endpoints %}
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="method {{ endpoint.method.lower() }}">{{ endpoint.method }}</span>
                            <span class="path">{{ endpoint.path }}</span>
                        </div>
                        <div class="endpoint-description">
                            {{ endpoint.description }}
                        </div>
                        
                        {% if endpoint.parameters %}
                        <div class="parameters">
                            <h4>파라미터</h4>
                            <table class="param-table">
                                <thead>
                                    <tr>
                                        <th>이름</th>
                                        <th>타입</th>
                                        <th>필수</th>
                                        <th>설명</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for param in endpoint.parameters %}
                                    <tr>
                                        <td>{{ param.name }}</td>
                                        <td><code>{{ param.type }}</code></td>
                                        <td>{{ "예" if param.required else "아니오" }}</td>
                                        <td>{{ param.description }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% endif %}
                        
                        {% if endpoint.examples %}
                        <div class="examples">
                            <h4>예제</h4>
                            {% for example in endpoint.examples %}
                            <div class="example">
                                <h5>{{ example.title }}</h5>
                                {% if example.description %}
                                <p>{{ example.description }}</p>
                                {% endif %}
                                <pre><code class="language-{{ example.language }}">{{ example.code }}</code></pre>
                                {% if example.output %}
                                <h6>응답</h6>
                                <pre><code class="language-json">{{ example.output }}</code></pre>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </section>
            {% endfor %}
        </main>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
    <script src="scripts.js"></script>
</body>
</html>
        """
    
    def _get_default_css_styles(self) -> str:
        """기본 CSS 스타일"""
        return """
/* 기본 스타일 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    display: flex;
    min-height: 100vh;
}

/* 헤더 */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    text-align: center;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.description {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 1rem;
}

.version-info {
    display: flex;
    justify-content: center;
    gap: 2rem;
}

.version, .status {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
}

/* 사이드바 */
.sidebar {
    width: 250px;
    background: white;
    padding: 2rem;
    border-right: 1px solid #e9ecef;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
}

.sidebar h3 {
    margin-bottom: 1rem;
    color: #495057;
}

.toc {
    list-style: none;
}

.toc li {
    margin-bottom: 0.5rem;
}

.toc a {
    color: #6c757d;
    text-decoration: none;
    padding: 0.5rem;
    display: block;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.toc a:hover {
    background-color: #f8f9fa;
    color: #495057;
}

/* 메인 콘텐츠 */
.content {
    flex: 1;
    margin-left: 250px;
    padding: 2rem;
}

.section {
    background: white;
    margin-bottom: 2rem;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section h2 {
    color: #495057;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e9ecef;
}

/* 엔드포인트 */
.endpoint {
    margin-bottom: 2rem;
    padding: 1.5rem;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    background: #f8f9fa;
}

.endpoint-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.method {
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.9rem;
    margin-right: 1rem;
}

.method.get { background: #d4edda; color: #155724; }
.method.post { background: #cce5ff; color: #004085; }
.method.put { background: #fff3cd; color: #856404; }
.method.delete { background: #f8d7da; color: #721c24; }
.method.patch { background: #e2e3e5; color: #383d41; }

.path {
    font-family: 'Courier New', monospace;
    font-size: 1.1rem;
    color: #495057;
}

.endpoint-description {
    color: #6c757d;
    margin-bottom: 1rem;
}

/* 테이블 */
.param-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

.param-table th,
.param-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

.param-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #495057;
}

/* 예제 */
.examples {
    margin-top: 1.5rem;
}

.example {
    margin-bottom: 1.5rem;
}

.example h5 {
    color: #495057;
    margin-bottom: 0.5rem;
}

.example h6 {
    color: #6c757d;
    margin: 1rem 0 0.5rem 0;
}

pre {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1rem;
    overflow-x: auto;
    margin: 0.5rem 0;
}

code {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        position: static;
        height: auto;
    }
    
    .content {
        margin-left: 0;
    }
    
    .endpoint-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .method {
        margin-bottom: 0.5rem;
        margin-right: 0;
    }
}
        """
    
    def _get_default_js_scripts(self) -> str:
        """기본 JavaScript 스크립트"""
        return """
// 스크롤 시 사이드바 하이라이트
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.section');
    const tocLinks = document.querySelectorAll('.toc a');
    
    window.addEventListener('scroll', function() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
});

// 코드 블록 복사 기능
document.addEventListener('DOMContentLoaded', function() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        const copyButton = document.createElement('button');
        copyButton.textContent = '복사';
        copyButton.className = 'copy-button';
        copyButton.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.25rem 0.5rem;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
        `;
        
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(block.textContent).then(function() {
                copyButton.textContent = '복사됨!';
                setTimeout(() => {
                    copyButton.textContent = '복사';
                }, 2000);
            });
        });
        
        block.parentElement.style.position = 'relative';
        block.parentElement.appendChild(copyButton);
    });
});

// 검색 기능
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'API 검색...';
    searchInput.className = 'search-input';
    searchInput.style.cssText = `
        width: 100%;
        padding: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        border-radius: 4px;
        font-size: 0.9rem;
    `;
    
    const sidebar = document.querySelector('.sidebar');
    sidebar.insertBefore(searchInput, sidebar.firstChild);
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const endpoints = document.querySelectorAll('.endpoint');
        
        endpoints.forEach(endpoint => {
            const text = endpoint.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                endpoint.style.display = 'block';
            } else {
                endpoint.style.display = 'none';
            }
        });
    });
});
        """
    
    def _get_default_markdown_template(self) -> str:
        """기본 Markdown 템플릿"""
        return """
# {{ api_info.title }}

{{ api_info.description }}

**버전**: {{ api_info.version }}  
**상태**: {{ api_info.status }}  
**생성일**: {{ api_info.generated_at }}

---

{% for section in sections %}
## {{ section.title }}

{% if section.description %}
{{ section.description }}
{% endif %}

{% if section.endpoints %}
{% for endpoint in section.endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

{{ endpoint.description }}

{% if endpoint.parameters %}
#### 파라미터

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
{% for param in endpoint.parameters %}
| {{ param.name }} | `{{ param.type }}` | {{ "예" if param.required else "아니오" }} | {{ param.description }} |
{% endfor %}
{% endif %}

{% if endpoint.examples %}
#### 예제

{% for example in endpoint.examples %}
**{{ example.title }}**

{% if example.description %}
{{ example.description }}
{% endif %}

```{{ example.language }}
{{ example.code }}
```

{% if example.output %}
**응답**

```json
{{ example.output }}
```
{% endif %}

{% endfor %}
{% endif %}

---
{% endfor %}
{% endif %}
{% endfor %}
        """
    
    def _get_default_openapi_template(self) -> str:
        """기본 OpenAPI 템플릿"""
        return """
openapi: 3.0.0
info:
  title: {{ api_info.title }}
  description: {{ api_info.description }}
  version: {{ api_info.version }}
  contact:
    name: API Support
    email: support@company.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.company.com/v{{ api_info.version }}
    description: Production server
  - url: https://staging-api.company.com/v{{ api_info.version }}
    description: Staging server

paths:
{% for section in sections %}
{% if section.endpoints %}
{% for endpoint in section.endpoints %}
  {{ endpoint.path }}:
    {{ endpoint.method.lower() }}:
      summary: {{ endpoint.description }}
      tags:
        - {{ section.title }}
      {% if endpoint.parameters %}
      parameters:
      {% for param in endpoint.parameters %}
        - name: {{ param.name }}
          in: {{ param.in if param.in else "query" }}
          required: {{ param.required }}
          schema:
            type: {{ param.type }}
          description: {{ param.description }}
      {% endfor %}
      {% endif %}
      {% if endpoint.request_body %}
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/{{ endpoint.request_body.schema }}'
      {% endif %}
      responses:
        '200':
          description: 성공
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/{{ endpoint.response_schema }}'
        '400':
          description: 잘못된 요청
        '401':
          description: 인증 실패
        '404':
          description: 리소스를 찾을 수 없음
        '500':
          description: 서버 오류
{% endfor %}
{% endif %}
{% endfor %}

components:
  schemas:
{% for schema in schemas %}
    {{ schema.name }}:
      type: object
      properties:
      {% for prop in schema.properties %}
        {{ prop.name }}:
          type: {{ prop.type }}
          description: {{ prop.description }}
          {% if prop.required %}
          required: true
          {% endif %}
      {% endfor %}
{% endfor %}

  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
        """
    
    def _save_template_to_db(self, template: DocumentationTemplate):
        """템플릿을 데이터베이스에 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO documentation_templates 
                    (id, name, description, format, template_content, css_styles, js_scripts, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    template.id,
                    template.name,
                    template.description,
                    template.format.value,
                    template.template_content,
                    template.css_styles,
                    template.js_scripts,
                    template.created_at
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"템플릿 저장 오류: {e}")
            raise
    
    def generate_documentation(self, api_data: Dict[str, Any], template_id: str = None, 
                             format: DocFormat = DocFormat.HTML) -> str:
        """API 문서 생성"""
        try:
            # 템플릿 선택
            if template_id:
                template = self.templates.get(template_id)
            else:
                # 형식에 맞는 기본 템플릿 선택
                template = next((t for t in self.templates.values() if t.format == format), None)
            
            if not template:
                raise ValueError(f"적합한 템플릿을 찾을 수 없습니다: {format.value}")
            
            # 문서 ID 생성
            doc_id = str(uuid.uuid4())
            
            # 템플릿 렌더링
            if template.format == DocFormat.HTML:
                content = self._render_html_template(template, api_data)
                file_path = self._save_html_documentation(doc_id, content, template)
            elif template.format == DocFormat.MARKDOWN:
                content = self._render_markdown_template(template, api_data)
                file_path = self._save_markdown_documentation(doc_id, content)
            elif template.format == DocFormat.OPENAPI:
                content = self._render_openapi_template(template, api_data)
                file_path = self._save_openapi_documentation(doc_id, content)
            else:
                raise ValueError(f"지원하지 않는 형식: {template.format.value}")
            
            # 문서 정보 저장
            documentation = APIDocumentation(
                id=doc_id,
                version=api_data.get('version', '1.0.0'),
                title=api_data.get('title', 'API Documentation'),
                description=api_data.get('description', ''),
                format=template.format,
                theme=DocTheme.DEFAULT,
                content=api_data,
                metadata={
                    'template_id': template.id,
                    'generated_by': 'APIDocumentationGenerator'
                },
                generated_at=datetime.now(),
                file_path=file_path,
                url=self._generate_documentation_url(doc_id, template.format)
            )
            
            self.documentations[doc_id] = documentation
            
            # 데이터베이스에 저장
            self._save_documentation_to_db(documentation)
            
            # 캐시에 저장
            self._cache_documentation(documentation)
            
            logger.info(f"API 문서 생성 완료: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"API 문서 생성 오류: {e}")
            raise
    
    def _render_html_template(self, template: DocumentationTemplate, api_data: Dict[str, Any]) -> str:
        """HTML 템플릿 렌더링"""
        try:
            template_obj = self.jinja_env.from_string(template.template_content)
            html_content = template_obj.render(**api_data)
            
            # CSS와 JS 추가
            if template.css_styles:
                css_link = f'<link rel="stylesheet" href="styles.css">'
                html_content = html_content.replace('</head>', f'{css_link}\n</head>')
            
            if template.js_scripts:
                js_script = f'<script>{template.js_scripts}</script>'
                html_content = html_content.replace('</body>', f'{js_script}\n</body>')
            
            return html_content
            
        except Exception as e:
            logger.error(f"HTML 템플릿 렌더링 오류: {e}")
            raise
    
    def _render_markdown_template(self, template: DocumentationTemplate, api_data: Dict[str, Any]) -> str:
        """Markdown 템플릿 렌더링"""
        try:
            template_obj = self.jinja_env.from_string(template.template_content)
            return template_obj.render(**api_data)
            
        except Exception as e:
            logger.error(f"Markdown 템플릿 렌더링 오류: {e}")
            raise
    
    def _render_openapi_template(self, template: DocumentationTemplate, api_data: Dict[str, Any]) -> str:
        """OpenAPI 템플릿 렌더링"""
        try:
            template_obj = self.jinja_env.from_string(template.template_content)
            return template_obj.render(**api_data)
            
        except Exception as e:
            logger.error(f"OpenAPI 템플릿 렌더링 오류: {e}")
            raise
    
    def _save_html_documentation(self, doc_id: str, content: str, template: DocumentationTemplate) -> str:
        """HTML 문서 저장"""
        try:
            # HTML 파일 저장
            html_file = Path(self.output_dir) / f"{doc_id}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # CSS 파일 저장
            if template.css_styles:
                css_file = Path(self.output_dir) / f"{doc_id}_styles.css"
                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write(template.css_styles)
            
            # JS 파일 저장
            if template.js_scripts:
                js_file = Path(self.output_dir) / f"{doc_id}_scripts.js"
                with open(js_file, 'w', encoding='utf-8') as f:
                    f.write(template.js_scripts)
            
            return str(html_file)
            
        except Exception as e:
            logger.error(f"HTML 문서 저장 오류: {e}")
            raise
    
    def _save_markdown_documentation(self, doc_id: str, content: str) -> str:
        """Markdown 문서 저장"""
        try:
            file_path = Path(self.output_dir) / f"{doc_id}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Markdown 문서 저장 오류: {e}")
            raise
    
    def _save_openapi_documentation(self, doc_id: str, content: str) -> str:
        """OpenAPI 문서 저장"""
        try:
            file_path = Path(self.output_dir) / f"{doc_id}.yaml"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"OpenAPI 문서 저장 오류: {e}")
            raise
    
    def _generate_documentation_url(self, doc_id: str, format: DocFormat) -> str:
        """문서 URL 생성"""
        try:
            base_url = self.config.get('base_url', 'http://localhost:8080')
            return f"{base_url}/docs/{doc_id}"
            
        except Exception as e:
            logger.error(f"문서 URL 생성 오류: {e}")
            return ""
    
    def _save_documentation_to_db(self, documentation: APIDocumentation):
        """문서를 데이터베이스에 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_documentations 
                    (id, version, title, description, format, theme, content, 
                     metadata, generated_at, file_path, url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    documentation.id,
                    documentation.version,
                    documentation.title,
                    documentation.description,
                    documentation.format.value,
                    documentation.theme.value,
                    json.dumps(documentation.content),
                    json.dumps(documentation.metadata),
                    documentation.generated_at,
                    documentation.file_path,
                    documentation.url
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"문서 저장 오류: {e}")
            raise
    
    def _cache_documentation(self, documentation: APIDocumentation):
        """문서 캐싱"""
        try:
            cache_key = f"doc:{documentation.id}"
            cache_data = {
                'id': documentation.id,
                'version': documentation.version,
                'title': documentation.title,
                'format': documentation.format.value,
                'url': documentation.url,
                'generated_at': documentation.generated_at.isoformat()
            }
            
            self.redis_client.setex(
                cache_key,
                3600,  # 1시간 TTL
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.error(f"문서 캐싱 오류: {e}")
    
    def get_documentation(self, doc_id: str) -> Optional[APIDocumentation]:
        """문서 조회"""
        try:
            # 캐시에서 조회
            cache_key = f"doc:{doc_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            # 메모리에서 조회
            return self.documentations.get(doc_id)
            
        except Exception as e:
            logger.error(f"문서 조회 오류: {e}")
            return None
    
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """새 템플릿 생성"""
        try:
            template_id = str(uuid.uuid4())
            
            template = DocumentationTemplate(
                id=template_id,
                name=template_data['name'],
                description=template_data.get('description', ''),
                format=DocFormat(template_data['format']),
                template_content=template_data['template_content'],
                css_styles=template_data.get('css_styles'),
                js_scripts=template_data.get('js_scripts'),
                created_at=datetime.now()
            )
            
            self.templates[template_id] = template
            
            # 데이터베이스에 저장
            self._save_template_to_db(template)
            
            logger.info(f"새 템플릿 생성 완료: {template_id}")
            return template_id
            
        except Exception as e:
            logger.error(f"템플릿 생성 오류: {e}")
            raise
    
    def generate_code_examples(self, api_data: Dict[str, Any]) -> List[CodeExample]:
        """코드 예제 생성"""
        try:
            examples = []
            
            for section in api_data.get('sections', []):
                for endpoint in section.get('endpoints', []):
                    # JavaScript 예제
                    js_example = self._generate_javascript_example(endpoint)
                    examples.append(js_example)
                    
                    # Python 예제
                    python_example = self._generate_python_example(endpoint)
                    examples.append(python_example)
                    
                    # cURL 예제
                    curl_example = self._generate_curl_example(endpoint)
                    examples.append(curl_example)
            
            return examples
            
        except Exception as e:
            logger.error(f"코드 예제 생성 오류: {e}")
            return []
    
    def _generate_javascript_example(self, endpoint: Dict[str, Any]) -> CodeExample:
        """JavaScript 예제 생성"""
        try:
            method = endpoint['method']
            path = endpoint['path']
            params = endpoint.get('parameters', [])
            
            # 파라미터 처리
            param_code = ""
            if params:
                param_code = ",\n  " + ",\n  ".join([
                    f"{param['name']}: '{param.get('example', 'value')}'"
                    for param in params if not param.get('required', False)
                ])
            
            code = f"""// {endpoint['description']}
fetch('{path}'{param_code})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));"""
            
            return CodeExample(
                language="javascript",
                title=f"JavaScript - {method} {path}",
                code=code,
                description="브라우저에서 실행 가능한 JavaScript 예제"
            )
            
        except Exception as e:
            logger.error(f"JavaScript 예제 생성 오류: {e}")
            return CodeExample("javascript", "Error", "// 예제 생성 실패")
    
    def _generate_python_example(self, endpoint: Dict[str, Any]) -> CodeExample:
        """Python 예제 생성"""
        try:
            method = endpoint['method']
            path = endpoint['path']
            params = endpoint.get('parameters', [])
            
            # 파라미터 처리
            param_code = ""
            if params:
                param_code = ",\n    " + ",\n    ".join([
                    f"{param['name']}='{param.get('example', 'value')}'"
                    for param in params if not param.get('required', False)
                ])
            
            code = f"""import requests

# {endpoint['description']}
response = requests.{method.lower()}(
    '{path}'{param_code}
)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f'Error: {{response.status_code}}')"""
            
            return CodeExample(
                language="python",
                title=f"Python - {method} {path}",
                code=code,
                description="Python requests 라이브러리를 사용한 예제"
            )
            
        except Exception as e:
            logger.error(f"Python 예제 생성 오류: {e}")
            return CodeExample("python", "Error", "# 예제 생성 실패")
    
    def _generate_curl_example(self, endpoint: Dict[str, Any]) -> CodeExample:
        """cURL 예제 생성"""
        try:
            method = endpoint['method']
            path = endpoint['path']
            params = endpoint.get('parameters', [])
            
            # 파라미터 처리
            param_code = ""
            if params:
                param_code = " \\\n  " + " \\\n  ".join([
                    f"-d '{param['name']}={param.get('example', 'value')}'"
                    for param in params if not param.get('required', False)
                ])
            
            code = f"""# {endpoint['description']}
curl -X {method} \\
  '{path}'{param_code} \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer YOUR_API_KEY'"""
            
            return CodeExample(
                language="bash",
                title=f"cURL - {method} {path}",
                code=code,
                description="터미널에서 실행 가능한 cURL 예제"
            )
            
        except Exception as e:
            logger.error(f"cURL 예제 생성 오류: {e}")
            return CodeExample("bash", "Error", "# 예제 생성 실패")
    
    def serve_documentation(self, doc_id: str, port: int = 8080):
        """문서 서버 실행"""
        try:
            documentation = self.get_documentation(doc_id)
            if not documentation or not documentation.file_path:
                raise ValueError(f"문서를 찾을 수 없습니다: {doc_id}")
            
            # 간단한 HTTP 서버 실행
            import http.server
            import socketserver
            
            os.chdir(self.output_dir)
            
            with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
                print(f"문서 서버가 http://localhost:{port} 에서 실행 중입니다.")
                print(f"문서 URL: http://localhost:{port}/{Path(documentation.file_path).name}")
                
                # 브라우저에서 열기
                webbrowser.open(f"http://localhost:{port}/{Path(documentation.file_path).name}")
                
                httpd.serve_forever()
                
        except Exception as e:
            logger.error(f"문서 서버 실행 오류: {e}")
            raise

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 6
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'your_program',
            'user': 'postgres',
            'password': 'password'
        },
        'output_dir': './api_docs',
        'base_url': 'http://localhost:8080'
    }
    
    # API 문서 생성기 생성
    doc_generator = APIDocumentationGenerator(config)
    
    # 샘플 API 데이터
    api_data = {
        'api_info': {
            'title': 'Your Program API',
            'description': 'Your Program의 REST API 문서',
            'version': '1.0.0',
            'status': 'Active',
            'generated_at': datetime.now().isoformat()
        },
        'sections': [
            {
                'id': 'users',
                'title': '사용자 관리',
                'description': '사용자 계정 관리 API',
                'endpoints': [
                    {
                        'method': 'GET',
                        'path': '/api/users',
                        'description': '사용자 목록 조회',
                        'parameters': [
                            {
                                'name': 'page',
                                'type': 'integer',
                                'required': False,
                                'description': '페이지 번호'
                            }
                        ],
                        'examples': [
                            {
                                'language': 'javascript',
                                'title': '사용자 목록 조회',
                                'code': 'fetch("/api/users?page=1")',
                                'output': '{"users": [], "total": 0}'
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # 문서 생성
    doc_id = doc_generator.generate_documentation(api_data, format=DocFormat.HTML)
    print(f"API 문서 생성 완료: {doc_id}")
    
    # 문서 서버 실행
    # doc_generator.serve_documentation(doc_id) 