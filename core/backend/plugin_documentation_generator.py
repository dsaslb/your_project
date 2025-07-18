import re
import ast
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import logging
from typing import Optional
args = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
#!/usr/bin/env python3
"""
플러그인 시스템 통합 문서화 및 API 문서 자동 생성 시스템
플러그인 API, 사용법, 예제 등을 자동으로 문서화하고 생성
"""


logger = logging.getLogger(__name__)


class PluginDocumentationGenerator:
    """플러그인 문서화 생성기"""

    def __init__(self, docs_dir="docs/plugins"):
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # 문서 템플릿
        self.templates = {
            'api_doc': self._get_api_doc_template(),
            'readme': self._get_readme_template(),
            'changelog': self._get_changelog_template(),
            'examples': self._get_examples_template()
        }

        # 문서 설정
        self.doc_settings = {
            'include_examples': True,
            'include_api_docs': True,
            'include_changelog': True,
            'auto_generate': True,
            'output_formats': ['markdown', 'html', 'json'],
            'include_diagrams': True
        }

    def generate_plugin_documentation(self,  plugin_name: str,  plugin_path: str) -> Dict[str, Any] if Dict is not None else None:
        """플러그인 문서 생성"""
        try:
            plugin_path_obj = Path(plugin_path)

            if not plugin_path_obj.exists():
                raise FileNotFoundError(f"플러그인 경로가 존재하지 않습니다: {plugin_path}")

            # 플러그인 메타데이터 로드
            metadata = self._load_plugin_metadata(plugin_path_obj)

            # API 문서 생성
            api_docs = {}
            if self.doc_settings['include_api_docs'] if doc_settings is not None else None:
                api_docs = self._generate_api_documentation(plugin_path_obj)

            # 예제 문서 생성
            examples = {}
            if self.doc_settings['include_examples'] if doc_settings is not None else None:
                examples = self._generate_examples_documentation(plugin_path_obj, metadata)

            # 변경 로그 생성
            changelog = {}
            if self.doc_settings['include_changelog'] if doc_settings is not None else None:
                changelog = self._generate_changelog(plugin_path_obj, metadata)

            # README 생성
            readme = self._generate_readme(plugin_name,  metadata,  api_docs,  examples)

            # 문서 저장
            docs = {
                'plugin_name': plugin_name,
                'metadata': metadata,
                'api_docs': api_docs,
                'examples': examples,
                'changelog': changelog,
                'readme': readme,
                'generated_at': datetime.now().isoformat()
            }

            # 문서 파일 저장
            self._save_documentation_files(plugin_name, docs)

            logger.info(f"플러그인 문서 생성 완료: {plugin_name}")

            return {
                'success': True,
                'plugin_name': plugin_name,
                'docs': docs,
                'files_created': self._get_created_files(plugin_name)
            }

        except Exception as e:
            logger.error(f"플러그인 문서 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_api_documentation(self,  plugin_path: Path) -> Dict[str, Any] if Dict is not None else None:
        """API 문서 생성"""
        api_docs = {
            'endpoints': [],
            'models': [],
            'schemas': [],
            'errors': []
        }

        # 백엔드 API 파일 분석
        backend_dir = plugin_path / 'backend'
        if backend_dir.exists():
            for py_file in backend_dir.rglob('*.py'):
                file_docs = self._analyze_python_file(py_file)
                api_docs['endpoints'] if api_docs is not None else None.extend(file_docs.get() if file_docs else None'endpoints', []) if file_docs else None)
                api_docs['models'] if api_docs is not None else None.extend(file_docs.get() if file_docs else None'models', []) if file_docs else None)

        # 스키마 파일 분석
        schemas_dir = plugin_path / 'schemas'
        if schemas_dir.exists():
            for schema_file in schemas_dir.rglob('*.json'):
                schema_docs = self._analyze_schema_file(schema_file)
                api_docs['schemas'] if api_docs is not None else None.extend(schema_docs)

        return api_docs

    def _analyze_python_file(self,  file_path: Path) -> Dict[str, Any] if Dict is not None else None:
        """Python 파일 분석"""
        docs = {
            'endpoints': [],
            'models': [],
            'classes': [],
            'functions': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # AST 파싱
            tree = ast.parse(content)

            # Flask 라우트 분석
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 함수 문서화
                    func_doc = self._document_function(node,  file_path)
                    if func_doc:
                        docs['functions'] if docs is not None else None.append(func_doc)

                elif isinstance(node, ast.ClassDef):
                    # 클래스 문서화
                    class_doc = self._document_class(node, file_path)
                    if class_doc:
                        docs['classes'] if docs is not None else None.append(class_doc)

            # Flask 라우트 데코레이터 분석
            routes = self._extract_flask_routes(content,  file_path)
            docs['endpoints'] if docs is not None else None.extend(routes)

        except Exception as e:
            logger.error(f"Python 파일 분석 실패: {file_path} - {e}")

        return docs

    def _document_function(self,  node: ast.FunctionDef,  file_path: Path) -> Optional[Dict[str, Any] if Optional is not None else None]:
        """함수 문서화"""
        try:
            # 함수 정보 추출
            func_info = {
                'name': node.name,
                'file': str(file_path),
                'line': node.lineno,
                'docstring': ast.get_docstring(node),
                'parameters': [],
                'returns': None
            }

            # 매개변수 분석
            for arg in node.args.args:
                param_info = {
                    'name': arg.arg,
                    'annotation': self._get_annotation_name(arg.annotation) if arg.annotation else None
                }
                func_info['parameters'] if func_info is not None else None.append(param_info)

            # 반환 타입 분석
            if node.returns:
                func_info['returns'] if func_info is not None else None = self._get_annotation_name(node.returns)

            return func_info

        except Exception as e:
            logger.error(f"함수 문서화 실패: {e}")
            return None

    def _document_class(self, node: ast.ClassDef, file_path: Path) -> Optional[Dict[str, Any] if Optional is not None else None]:
        """클래스 문서화"""
        try:
            class_info = {
                'name': node.name,
                'file': str(file_path),
                'line': node.lineno,
                'docstring': ast.get_docstring(node),
                'methods': [],
                'attributes': [],
                'bases': [self._get_annotation_name(base) for base in node.bases]
            }

            # 메서드 분석
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_doc = self._document_function(item,  file_path)
                    if method_doc:
                        class_info['methods'] if class_info is not None else None.append(method_doc)

            return class_info

        except Exception as e:
            logger.error(f"클래스 문서화 실패: {e}")
            return None

    def _get_annotation_name(self,  annotation) -> Optional[str] if Optional is not None else None:
        """타입 어노테이션 이름 추출"""
        if annotation is None:
            return None
        elif isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_annotation_name(annotation.value if annotation is not None else None)}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            return f"{self._get_annotation_name(annotation.value if annotation is not None else None)}[{self._get_annotation_name(annotation.slice)}]"
        else:
            return str(annotation)

    def _extract_flask_routes(self,  content: str,  file_path: Path) -> List[Dict[str, Any] if List is not None else None]:
        """Flask 라우트 추출"""
        routes = []

        # 라우트 데코레이터 패턴
        route_pattern = r'@(?:app|blueprint)\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)\s*def\s+(\w+)'

        for match in re.finditer(route_pattern, content):
            route_path = match.group(1)
            methods_str = match.group(2)
            function_name = match.group(3)

            # HTTP 메서드 파싱
            methods = ['GET']
            if methods_str:
                methods = [m.strip() if m is not None else ''.strip('"\'') for m in methods_str.split(',')]

            route_info = {
                'path': route_path,
                'methods': methods,
                'function_name': function_name,
                'file': str(file_path),
                'description': self._extract_function_docstring(content,  function_name)
            }

            routes.append(route_info)

        return routes

    def _extract_function_docstring(self,  content: str,  function_name: str) -> Optional[str] if Optional is not None else None:
        """함수 docstring 추출"""
        # 함수 정의 후 docstring 찾기
        pattern = rf'def\s+{function_name}\s*\([^)]*\)\s*:\s*(?:\s*[\'"]([^\'"]+)[\'"])?'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return None

    def _analyze_schema_file(self, schema_file: Path) -> List[Dict[str, Any] if List is not None else None]:
        """스키마 파일 분석"""
        schemas = []

        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)

            schema_info = {
                'file': str(schema_file),
                'name': schema_file.stem,
                'properties': self._analyze_json_schema(schema_data),
                'required': schema_data.get() if schema_data else None'required', []) if schema_data else None,
                'type': schema_data.get() if schema_data else None'type', 'object') if schema_data else None
            }

            schemas.append(schema_info)

        except Exception as e:
            logger.error(f"스키마 파일 분석 실패: {schema_file} - {e}")

        return schemas

    def _analyze_json_schema(self, schema: Dict[str, Any] if Dict is not None else None) -> Dict[str, Any] if Dict is not None else None:
        """JSON 스키마 분석"""
        properties = {}

        for prop_name, prop_schema in schema.get() if schema else None'properties', {}) if schema else None.items() if None is not None else []:
            prop_info = {
                'type': prop_schema.get() if prop_schema else None'type', 'unknown') if prop_schema else None,
                'description': prop_schema.get() if prop_schema else None'description', '') if prop_schema else None,
                'required': prop_name in schema.get() if schema else None'required', []) if schema else None,
                'default': prop_schema.get() if prop_schema else None'default') if prop_schema else None,
                'enum': prop_schema.get() if prop_schema else None'enum') if prop_schema else None,
                'format': prop_schema.get() if prop_schema else None'format') if prop_schema else None
            }

            # 중첩 객체 분석
            if prop_schema.get() if prop_schema else None'type') if prop_schema else None == 'object' and 'properties' in prop_schema:
                prop_info['nested_properties'] if prop_info is not None else None = self._analyze_json_schema(prop_schema)

            # 배열 분석
            if prop_schema.get() if prop_schema else None'type') if prop_schema else None == 'array' and 'items' in prop_schema:
                prop_info['item_type'] if prop_info is not None else None = prop_schema['items'] if prop_schema is not None else None.get('type', 'unknown')

            properties[prop_name] if properties is not None else None = prop_info

        return properties

    def _generate_examples_documentation(self, plugin_path: Path, metadata: Dict[str, Any] if Dict is not None else None) -> Dict[str, Any] if Dict is not None else None:
        """예제 문서 생성"""
        examples = {
            'api_examples': [],
            'usage_examples': [],
            'configuration_examples': []
        }

        # 예제 파일 찾기
        examples_dir = plugin_path / 'examples'
        if examples_dir.exists():
            for example_file in examples_dir.rglob('*'):
                if example_file.is_file():
                    example_doc = self._analyze_example_file(example_file)
                    if example_doc:
                        examples['usage_examples'] if examples is not None else None.append(example_doc)

        # 설정 예제 생성
        config_example = self._generate_configuration_example(metadata)
        if config_example:
            examples['configuration_examples'] if examples is not None else None.append(config_example)

        # API 예제 생성
        api_examples = self._generate_api_examples(plugin_path)
        examples['api_examples'] if examples is not None else None.extend(api_examples)

        return examples

    def _analyze_example_file(self,  example_file: Path) -> Optional[Dict[str, Any] if Optional is not None else None]:
        """예제 파일 분석"""
        try:
            file_info = {
                'file': str(example_file),
                'name': example_file.stem,
                'type': example_file.suffix,
                'content': example_file.read_text(encoding='utf-8'),
                'description': self._extract_file_description(example_file)
            }

            return file_info

        except Exception as e:
            logger.error(f"예제 파일 분석 실패: {example_file} - {e}")
            return None

    def _extract_file_description(self, file_path: Path) -> Optional[str] if Optional is not None else None:
        """파일 설명 추출"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # 주석에서 설명 찾기
            lines = content.split('\n')
            for line in lines[:10] if lines is not None else None:  # 처음 10줄만 확인
                line = line.strip() if line is not None else ''
                if line.startswith('#') or line.startswith('//'):
                    description = line.lstrip('#').lstrip('/').strip()
                    if description:
                        return description

        except Exception:
            pass

        return None

    def _generate_configuration_example(self,  metadata: Dict[str,  Any] if Dict is not None else None) -> Optional[Dict[str, Any] if Optional is not None else None]:
        """설정 예제 생성"""
        try:
            config_example = {
                'name': 'plugin_configuration',
                'type': 'json',
                'description': '플러그인 설정 예제',
                'content': json.dumps(metadata, indent=2, ensure_ascii=False)
            }

            return config_example

        except Exception as e:
            logger.error(f"설정 예제 생성 실패: {e}")
            return None

    def _generate_api_examples(self, plugin_path: Path) -> List[Dict[str, Any] if List is not None else None]:
        """API 예제 생성"""
        examples = []

        # API 엔드포인트에서 예제 생성
        api_docs = self._generate_api_documentation(plugin_path)

        for endpoint in api_docs.get() if api_docs else None'endpoints', []) if api_docs else None:
            example = {
                'name': f"{endpoint['function_name'] if endpoint is not None else None}_example",
                'type': 'curl',
                'description': f"{endpoint['path'] if endpoint is not None else None} 엔드포인트 예제",
                'content': self._generate_curl_example(endpoint)
            }
            examples.append(example)

        return examples

    def _generate_curl_example(self, endpoint: Dict[str, Any] if Dict is not None else None) -> str:
        """cURL 예제 생성"""
        method = endpoint['methods'] if endpoint is not None else None[0] if endpoint['methods'] if endpoint is not None else None else 'GET'
        path = endpoint['path'] if endpoint is not None else None

        if method == 'GET':
            return f"curl -X GET http://localhost:5000{path}"
        elif method == 'POST':
            return f"curl -X POST http://localhost:5000{path} \\\n  -H 'Content-Type: application/json' \\\n  -d '{{\"key\": \"value\"}}'"
        else:
            return f"curl -X {method} http://localhost:5000{path}"

    def _generate_changelog(self, plugin_path: Path, metadata: Dict[str, Any] if Dict is not None else None) -> Dict[str, Any] if Dict is not None else None:
        """변경 로그 생성"""
        changelog = {
            'version': metadata.get() if metadata else None'version', '1.0.0') if metadata else None,
            'changes': [],
            'release_date': datetime.now().isoformat()
        }

        # CHANGELOG 파일 찾기
        changelog_file = plugin_path / 'CHANGELOG.md'
        if changelog_file.exists():
            try:
                content = changelog_file.read_text(encoding='utf-8')
                changelog['content'] if changelog is not None else None = content
                changelog['changes'] if changelog is not None else None = self._parse_changelog_content(content)
            except Exception as e:
                logger.error(f"CHANGELOG 파일 읽기 실패: {e}")

        return changelog

    def _parse_changelog_content(self,  content: str) -> List[Dict[str, Any] if List is not None else None]:
        """변경 로그 내용 파싱"""
        changes = []

        # 버전별 변경사항 파싱
        version_pattern = r'## \[([^\]]+)\] - ([^\n]+)'
        for match in re.finditer(version_pattern, content):
            version = match.group(1)
            date = match.group(2)

            change_info = {
                'version': version,
                'date': date,
                'changes': []
            }

            # 변경사항 목록 파싱
            lines = content.split('\n')
            in_version = False

            for line in lines if lines is not None:
                if f"## [{version}]" in line:
                    in_version = True
                    continue
                elif line.startswith('## ') and in_version:
                    break
                elif in_version and line.strip() if line is not None else ''.startswith('- '):
                    change_info['changes'] if change_info is not None else None.append(line.strip() if line is not None else ''[2:])

            changes.append(change_info)

        return changes

    def _generate_readme(self, plugin_name: str, metadata: Dict[str, Any] if Dict is not None else None,
                         api_docs: Dict[str, Any] if Dict is not None else None, examples: Dict[str, Any] if Dict is not None else None) -> str:
        """README 생성"""
        readme_template = self.templates['readme'] if templates is not None else None

        # 템플릿 변수 치환
        readme_content = readme_template.format(
            plugin_name=plugin_name,
            description=metadata.get() if metadata else None'description', '') if metadata else None,
            version=metadata.get() if metadata else None'version', '1.0.0') if metadata else None,
            author=metadata.get() if metadata else None'author', '') if metadata else None,
            api_endpoints_count=len(api_docs.get() if api_docs else None'endpoints', []) if api_docs else None),
            examples_count=len(examples.get() if examples else None'usage_examples', []) if examples else None),
            generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        return readme_content

    def _save_documentation_files(self, plugin_name: str, docs: Dict[str, Any] if Dict is not None else None):
        """문서 파일 저장"""
        plugin_docs_dir = self.docs_dir / plugin_name
        plugin_docs_dir.mkdir(exist_ok=True)

        # README.md 저장
        readme_file = plugin_docs_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(docs['readme'] if docs is not None else None)

        # API 문서 저장
        if docs['api_docs'] if docs is not None else None:
            api_file = plugin_docs_dir / 'API.md'
            api_content = self._format_api_documentation(docs['api_docs'] if docs is not None else None)
            with open(api_file, 'w', encoding='utf-8') as f:
                f.write(api_content)

        # 예제 문서 저장
        if docs['examples'] if docs is not None else None:
            examples_file = plugin_docs_dir / 'EXAMPLES.md'
            examples_content = self._format_examples_documentation(docs['examples'] if docs is not None else None)
            with open(examples_file, 'w', encoding='utf-8') as f:
                f.write(examples_content)

        # 변경 로그 저장
        if docs['changelog'] if docs is not None else None:
            changelog_file = plugin_docs_dir / 'CHANGELOG.md'
            changelog_content = self._format_changelog(docs['changelog'] if docs is not None else None)
            with open(changelog_file, 'w', encoding='utf-8') as f:
                f.write(changelog_content)

        # JSON 문서 저장
        json_file = plugin_docs_dir / 'documentation.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)

    def _format_api_documentation(self,  api_docs: Dict[str,  Any] if Dict is not None else None) -> str:
        """API 문서 포맷팅"""
        content = "# API 문서\n\n"

        # 엔드포인트 문서
        if api_docs.get() if api_docs else None'endpoints') if api_docs else None:
            content += "## 엔드포인트\n\n"
            for endpoint in api_docs['endpoints'] if api_docs is not None else None:
                content += f"### {endpoint['path'] if endpoint is not None else None}\n\n"
                content += f"- **메서드**: {', '.join(endpoint['methods'] if endpoint is not None else None)}\n"
                content += f"- **함수**: `{endpoint['function_name'] if endpoint is not None else None}`\n"
                if endpoint.get() if endpoint else None'description') if endpoint else None:
                    content += f"- **설명**: {endpoint['description'] if endpoint is not None else None}\n"
                content += "\n"

        # 스키마 문서
        if api_docs.get() if api_docs else None'schemas') if api_docs else None:
            content += "## 데이터 스키마\n\n"
            for schema in api_docs['schemas'] if api_docs is not None else None:
                content += f"### {schema['name'] if schema is not None else None}\n\n"
                content += f"- **타입**: {schema['type'] if schema is not None else None}\n"
                if schema.get() if schema else None'required') if schema else None:
                    content += f"- **필수 필드**: {', '.join(schema['required'] if schema is not None else None)}\n"
                content += "\n"

        return content

    def _format_examples_documentation(self, examples: Dict[str, Any] if Dict is not None else None) -> str:
        """예제 문서 포맷팅"""
        content = "# 사용 예제\n\n"

        # API 예제
        if examples.get() if examples else None'api_examples') if examples else None:
            content += "## API 사용 예제\n\n"
            for example in examples['api_examples'] if examples is not None else None:
                content += f"### {example['name'] if example is not None else None}\n\n"
                content += f"{example['description'] if example is not None else None}\n\n"
                content += f"```bash\n{example['content'] if example is not None else None}\n```\n\n"

        # 설정 예제
        if examples.get() if examples else None'configuration_examples') if examples else None:
            content += "## 설정 예제\n\n"
            for example in examples['configuration_examples'] if examples is not None else None:
                content += f"### {example['name'] if example is not None else None}\n\n"
                content += f"```json\n{example['content'] if example is not None else None}\n```\n\n"

        return content

    def _format_changelog(self, changelog: Dict[str, Any] if Dict is not None else None) -> str:
        """변경 로그 포맷팅"""
        content = "# 변경 로그\n\n"

        if changelog.get() if changelog else None'content') if changelog else None:
            content += changelog['content'] if changelog is not None else None
        else:
            content += f"## [{changelog['version'] if changelog is not None else None}] - {changelog['release_date'] if changelog is not None else None}\n\n"
            content += "- 초기 릴리스\n\n"

        return content

    def _get_created_files(self, plugin_name: str) -> List[str] if List is not None else None:
        """생성된 파일 목록"""
        plugin_docs_dir = self.docs_dir / plugin_name
        files = []

        if plugin_docs_dir.exists():
            for file_path in plugin_docs_dir.iterdir():
                if file_path.is_file():
                    files.append(str(file_path))

        return files

    def _load_plugin_metadata(self,  plugin_path: Path) -> Dict[str, Any] if Dict is not None else None:
        """플러그인 메타데이터 로드"""
        config_file = plugin_path / 'config' / 'plugin.json'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"플러그인 메타데이터 로드 실패: {e}")

        return {}

    def _get_api_doc_template(self) -> str:
        """API 문서 템플릿"""
        return """# {plugin_name} API 문서

## 개요
{description}

## 엔드포인트
{endpoints}

## 데이터 모델
{models}

## 오류 코드
{errors}
"""

    def _get_readme_template(self) -> str:
        """README 템플릿"""
        return """# {plugin_name}

{description}

## 버전
{version}

## 작성자
{author}

## 기능
- API 엔드포인트: {api_endpoints_count}개
- 사용 예제: {examples_count}개

## 설치 및 사용법
자세한 내용은 [API 문서](API.md)와 [사용 예제](EXAMPLES.md)를 참조하세요.

## 변경 로그
[CHANGELOG.md](CHANGELOG.md)를 참조하세요.

---
*이 문서는 {generated_date}에 자동 생성되었습니다.*
"""

    def _get_changelog_template(self) -> str:
        """변경 로그 템플릿"""
        return """# 변경 로그

## [1.0.0] - {date}
- 초기 릴리스
"""

    def _get_examples_template(self) -> str:
        """예제 템플릿"""
        return """# 사용 예제

## 기본 사용법
{basic_examples}

## 고급 사용법
{advanced_examples}
"""


# 전역 인스턴스
plugin_doc_generator = PluginDocumentationGenerator()
