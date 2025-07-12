#!/usr/bin/env python3
"""
플러그인 문서화 자동화 도구
API 문서, 사용법 가이드, 예제 코드 자동 생성
"""

import json
import logging
import ast
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re
import yaml
from jinja2 import Template

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FunctionDoc:
    """함수 문서 정보"""
    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, Any]]
    return_type: str
    return_description: str
    examples: List[str]
    line_number: int

@dataclass
class ClassDoc:
    """클래스 문서 정보"""
    name: str
    docstring: str
    methods: List[FunctionDoc]
    properties: List[Dict[str, Any]]
    base_classes: List[str]
    line_number: int

@dataclass
class ModuleDoc:
    """모듈 문서 정보"""
    name: str
    docstring: str
    functions: List[FunctionDoc]
    classes: List[ClassDoc]
    imports: List[str]
    constants: List[Dict[str, Any]]
    file_path: str

@dataclass
class PluginDocumentation:
    """플러그인 문서 정보"""
    plugin_id: str
    plugin_name: str
    version: str
    description: str
    author: str
    modules: List[ModuleDoc]
    api_endpoints: List[Dict[str, Any]]
    configuration: Dict[str, Any]
    examples: List[Dict[str, Any]]
    changelog: List[Dict[str, Any]]
    generated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()

class PluginDocumentationGenerator:
    """플러그인 문서화 생성기"""
    
    def __init__(self, output_dir: str = "docs/plugins"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 템플릿 디렉토리 설정
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
        # 기본 템플릿 생성
        self._create_default_templates()
        
    def _create_default_templates(self):
        """기본 템플릿 생성"""
        templates = {
            'readme.md': """# {{ plugin_name }}

## 개요
{{ description }}

## 설치
```bash
pip install {{ plugin_id }}
```

## 사용법
```python
from {{ plugin_id }} import {{ main_class }}

# 기본 사용법
{{ basic_example }}
```

## API 문서
{% for module in modules %}
### {{ module.name }}
{% for function in module.functions %}
#### {{ function.name }}
{{ function.docstring }}

**시그니처:**
```python
{{ function.signature }}
```

**매개변수:**
{% for param in function.parameters %}
- `{{ param.name }}` ({{ param.type }}): {{ param.description }}
{% endfor %}

**반환값:**
{{ function.return_description }}

**예제:**
```python
{{ function.examples[0] if function.examples else "예제가 없습니다" }}
```
{% endfor %}
{% endfor %}

## 설정
```yaml
{{ configuration_yaml }}
```

## 예제
{% for example in examples %}
### {{ example.title }}
{{ example.description }}

```python
{{ example.code }}
```
{% endfor %}

## 변경 이력
{% for change in changelog %}
### {{ change.version }} ({{ change.date }})
{% for item in change.changes %}
- {{ item }}
{% endfor %}
{% endfor %}
""",
            
            'api.md': """# {{ plugin_name }} API 문서

## 개요
이 문서는 {{ plugin_name }} 플러그인의 API를 설명합니다.

## 엔드포인트
{% for endpoint in api_endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}
{{ endpoint.description }}

**매개변수:**
{% for param in endpoint.parameters %}
- `{{ param.name }}` ({{ param.type }}): {{ param.description }}
{% endfor %}

**응답:**
```json
{{ endpoint.response }}
```

**예제:**
```bash
{{ endpoint.example }}
```
{% endfor %}
""",
            
            'examples.md': """# {{ plugin_name }} 예제

## 기본 예제
{% for example in examples %}
### {{ example.title }}
{{ example.description }}

```python
{{ example.code }}
```

**실행 결과:**
```
{{ example.output }}
```
{% endfor %}
""",
            
            'changelog.md': """# {{ plugin_name }} 변경 이력

{% for change in changelog %}
## {{ change.version }} ({{ change.date }})
{% for category, items in change.changes.items() %}
### {{ category }}
{% for item in items %}
- {{ item }}
{% endfor %}
{% endfor %}
{% endfor %}
"""
        }
        
        for template_name, template_content in templates.items():
            template_path = self.template_dir / template_name
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
    
    def generate_documentation(self, plugin_path_str: str) -> Dict[str, Any]:
        """플러그인 문서 생성"""
        try:
            plugin_path: Path = Path(plugin_path_str)
            
            # 플러그인 정보 추출
            plugin_info = self._extract_plugin_info(plugin_path, plugin_config={})
            
            # 모듈 분석
            modules = self._analyze_modules(plugin_path)
            
            # API 엔드포인트 분석
            api_endpoints = self._extract_api_endpoints(plugin_path)
            
            # 설정 정보 추출
            configuration = self._extract_configuration(plugin_path)
            
            # 예제 코드 생성
            examples = self._generate_examples(modules, plugin_info)
            
            # 변경 이력 추출
            changelog = self._extract_changelog(plugin_path)
            
            # 문서 객체 생성
            documentation = PluginDocumentation(
                plugin_id=plugin_info['id'],
                plugin_name=plugin_info['name'],
                version=plugin_info['version'],
                description=plugin_info['description'],
                author=plugin_info['author'],
                modules=modules,
                api_endpoints=api_endpoints,
                configuration=configuration,
                examples=examples,
                changelog=changelog
            )
            
            # 문서 파일 생성
            self._generate_documentation_files(documentation)
            
            logger.info(f"플러그인 문서 생성 완료: {plugin_info['name']}")
            if isinstance(documentation, dict):
                return documentation
            elif hasattr(documentation, '__dict__'):
                return dict(documentation.__dict__)
            else:
                return {}
            
        except Exception as e:
            logger.error(f"문서 생성 실패: {e}")
            return {}  # 명시적으로 Dict[str, Any] 반환
    
    def _extract_plugin_info(self, plugin_path: Path, plugin_config: Dict[str, Any]) -> Dict[str, Any]:
        """플러그인 정보 추출"""
        # plugin.json 파일에서 정보 추출
        plugin_json_path = plugin_path / "config" / "plugin.json"
        if plugin_json_path.exists():
            with open(plugin_json_path, 'r', encoding='utf-8') as f:
                plugin_data = json.load(f)
        else:
            plugin_data = {}
        
        # 설정과 병합
        plugin_info = {
            'id': plugin_config.get('id', plugin_data.get('id', 'unknown')),
            'name': plugin_config.get('name', plugin_data.get('name', 'Unknown Plugin')),
            'version': plugin_config.get('version', plugin_data.get('version', '1.0.0')),
            'description': plugin_config.get('description', plugin_data.get('description', '')),
            'author': plugin_config.get('author', plugin_data.get('author', 'Unknown'))
        }
        
        return plugin_info
    
    def _analyze_modules(self, plugin_path: Path) -> List[ModuleDoc]:
        """모듈 분석"""
        modules = []
        
        # Python 파일 찾기
        python_files = list(plugin_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                module_doc = self._analyze_python_file(py_file)
                if module_doc:
                    modules.append(module_doc)
            except Exception as e:
                logger.error(f"파일 분석 실패: {py_file} - {e}")
        
        return modules
    
    def _analyze_python_file(self, file_path: Path) -> Optional[ModuleDoc]:
        """Python 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST 파싱
            tree = ast.parse(content)
            
            # 모듈 정보 추출
            module_name = file_path.stem
            module_docstring = ast.get_docstring(tree) or ""
            
            # 함수 분석
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_doc = self._extract_function_info(node)
                    if func_doc:
                        functions.append(func_doc)
            
            # 클래스 분석
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_doc = self._extract_class_info(node)
                    if class_doc:
                        classes.append(class_doc)
            
            # 임포트 분석
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            # 상수 분석
            constants = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            constants.append({
                                'name': target.id,
                                'value': self._extract_constant_value(node.value)
                            })
            
            return ModuleDoc(
                name=module_name,
                docstring=module_docstring,
                functions=functions,
                classes=classes,
                imports=imports,
                constants=constants,
                file_path=str(file_path)
            )
            
        except Exception as e:
            logger.error(f"Python 파일 분석 실패: {file_path} - {e}")
            return None
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Optional[FunctionDoc]:
        """함수 정보 추출"""
        try:
            # 함수 시그니처 생성
            args = []
            for arg in node.args.args:
                args.append(arg.arg)
            
            signature = f"{node.name}({', '.join(args)})"
            
            # 매개변수 정보 추출
            parameters = []
            for arg in node.args.args:
                param_type = "Any"
                if arg.annotation:
                    param_type = ast.unparse(arg.annotation)
                
                parameters.append({
                    'name': arg.arg,
                    'type': param_type,
                    'description': '',
                    'default': None
                })
            
            # 반환 타입 추출
            return_type = "Any"
            if node.returns:
                return_type = ast.unparse(node.returns)
            
            # 예제 코드 생성
            examples = self._generate_function_examples(node)
            
            return FunctionDoc(
                name=node.name,
                signature=signature,
                docstring=ast.get_docstring(node) or "",
                parameters=parameters,
                return_type=return_type,
                return_description="",
                examples=examples,
                line_number=node.lineno
            )
            
        except Exception as e:
            logger.error(f"함수 정보 추출 실패: {node.name} - {e}")
            return None
    
    def _extract_class_info(self, node: ast.ClassDef) -> Optional[ClassDoc]:
        """클래스 정보 추출"""
        try:
            # 메서드 추출
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_doc = self._extract_function_info(item)
                    if method_doc:
                        methods.append(method_doc)
            
            # 속성 추출
            properties = []
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            properties.append({
                                'name': target.id,
                                'value': self._extract_constant_value(item.value)
                            })
            
            # 기본 클래스 추출
            base_classes = []
            for base in node.bases:
                base_classes.append(ast.unparse(base))
            
            return ClassDoc(
                name=node.name,
                docstring=ast.get_docstring(node) or "",
                methods=methods,
                properties=properties,
                base_classes=base_classes,
                line_number=node.lineno
            )
            
        except Exception as e:
            logger.error(f"클래스 정보 추출 실패: {node.name} - {e}")
            return None
    
    def _extract_constant_value(self, node: ast.AST) -> str:
        """상수 값 추출"""
        try:
            if isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Str):
                return repr(node.s)
            elif isinstance(node, ast.Num):
                return repr(node.n)
            elif isinstance(node, ast.Name):
                return node.id
            else:
                return ast.unparse(node)
        except Exception:
            return "unknown"
    
    def _generate_function_examples(self, node: ast.FunctionDef) -> List[str]:
        """함수 예제 코드 생성"""
        examples = []
        
        try:
            # 기본 예제 생성
            args = []
            for arg in node.args.args:
                if arg.arg != 'self':
                    args.append(f"{arg.arg}=value")
            
            example = f"# {node.name} 함수 사용 예제\n"
            example += f"result = {node.name}({', '.join(args)})\n"
            example += "print(result)"
            
            examples.append(example)
            
            # docstring에서 예제 추출
            docstring = ast.get_docstring(node) or ""
            code_blocks = re.findall(r'```python\n(.*?)\n```', docstring, re.DOTALL)
            examples.extend(code_blocks)
            
        except Exception as e:
            logger.error(f"함수 예제 생성 실패: {node.name} - {e}")
        
        return examples
    
    def _extract_api_endpoints(self, plugin_path: Path) -> List[Dict[str, Any]]:
        """API 엔드포인트 추출"""
        endpoints = []
        
        try:
            # Flask 라우트 찾기
            for py_file in plugin_path.rglob("*.py"):
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # @app.route 데코레이터 찾기
                route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)\s*def\s+(\w+)'
                matches = re.findall(route_pattern, content)
                
                for match in matches:
                    path, methods, function_name = match
                    method_list = methods.split(',') if methods else ['GET']
                    method_list = [m.strip().strip("'\"") for m in method_list]
                    
                    endpoints.append({
                        'path': path,
                        'method': method_list[0].upper(),
                        'function': function_name,
                        'description': f"{function_name} 함수",
                        'parameters': [],
                        'response': '{}',
                        'example': f"curl -X {method_list[0].upper()} http://localhost:5000{path}"
                    })
            
        except Exception as e:
            logger.error(f"API 엔드포인트 추출 실패: {e}")
        
        return endpoints
    
    def _extract_configuration(self, plugin_path: Path) -> Dict[str, Any]:
        """설정 정보 추출"""
        config = {}
        
        try:
            # config.json 파일 찾기
            config_files = [
                plugin_path / "config.json",
                plugin_path / "config" / "config.json",
                plugin_path / "config.yml",
                plugin_path / "config.yaml"
            ]
            
            for config_file in config_files:
                if config_file.exists():
                    if config_file.suffix in ['.yml', '.yaml']:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                    else:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    break
            
        except Exception as e:
            logger.error(f"설정 정보 추출 실패: {e}")
        
        if isinstance(config, dict):
            return config
        else:
            return {}
    
    def _generate_examples(self, modules: List[ModuleDoc], plugin_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """예제 코드 생성"""
        examples = []
        
        try:
            # 기본 사용 예제
            basic_example = {
                'title': '기본 사용법',
                'description': f"{plugin_info['name']} 플러그인의 기본 사용법을 보여줍니다.",
                'code': f"""from {plugin_info['id']} import main

# 플러그인 초기화
plugin = main()

# 기본 기능 실행
result = plugin.run()
print(result)""",
                'output': '{"status": "success", "message": "Plugin executed successfully"}'
            }
            examples.append(basic_example)
            
            # 모듈별 예제 생성
            for module in modules:
                if module.functions:
                    # 첫 번째 함수를 예제로 사용
                    func = module.functions[0]
                    example = {
                        'title': f'{module.name} 모듈 사용법',
                        'description': f"{module.name} 모듈의 {func.name} 함수 사용 예제입니다.",
                        'code': f"""from {plugin_info['id']}.{module.name} import {func.name}

# {func.name} 함수 호출
result = {func.name}()
print(result)""",
                        'output': '{"result": "example output"}'
                    }
                    examples.append(example)
            
        except Exception as e:
            logger.error(f"예제 코드 생성 실패: {e}")
        
        return examples
    
    def _extract_changelog(self, plugin_path: Path) -> List[Dict[str, Any]]:
        """변경 이력 추출"""
        changelog = []
        
        try:
            # CHANGELOG.md 파일 찾기
            changelog_file = plugin_path / "CHANGELOG.md"
            if changelog_file.exists():
                with open(changelog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 마크다운 파싱하여 변경 이력 추출
                version_pattern = r'##\s+([\d.]+)\s+\(([^)]+)\)'
                matches = re.findall(version_pattern, content)
                
                for version, date in matches:
                    changelog.append({
                        'version': version,
                        'date': date,
                        'changes': {
                            'Added': [],
                            'Changed': [],
                            'Fixed': [],
                            'Removed': []
                        }
                    })
            
            # 기본 변경 이력 생성
            if not changelog:
                changelog.append({
                    'version': '1.0.0',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'changes': {
                        'Added': ['초기 버전 릴리스'],
                        'Changed': [],
                        'Fixed': [],
                        'Removed': []
                    }
                })
            
        except Exception as e:
            logger.error(f"변경 이력 추출 실패: {e}")
        
        return changelog
    
    def _generate_documentation_files(self, documentation: PluginDocumentation):
        """문서 파일 생성"""
        try:
            plugin_dir = self.output_dir / documentation.plugin_id
            plugin_dir.mkdir(exist_ok=True)
            
            # README.md 생성
            self._generate_readme(documentation, plugin_dir)
            
            # API.md 생성
            self._generate_api_doc(documentation, plugin_dir)
            
            # examples.md 생성
            self._generate_examples_doc(documentation, plugin_dir)
            
            # changelog.md 생성
            self._generate_changelog_doc(documentation, plugin_dir)
            
            # JSON 메타데이터 생성
            self._generate_metadata(documentation, plugin_dir)
            
        except Exception as e:
            logger.error(f"문서 파일 생성 실패: {e}")
    
    def _generate_readme(self, documentation: PluginDocumentation, output_dir: Path):
        """README.md 생성"""
        try:
            template_path = self.template_dir / "readme.md"
            with open(template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            
            # 설정을 YAML 형식으로 변환
            config_yaml = yaml.dump(documentation.configuration, default_flow_style=False, allow_unicode=True)
            
            # 메인 클래스 찾기
            main_class = "main"
            if documentation.modules:
                for module in documentation.modules:
                    if module.classes:
                        main_class = module.classes[0].name
                        break
            
            # 기본 예제 생성
            basic_example = f"plugin = {main_class}()\nresult = plugin.run()"
            
            content = template.render(
                plugin_name=documentation.plugin_name,
                description=documentation.description,
                plugin_id=documentation.plugin_id,
                main_class=main_class,
                basic_example=basic_example,
                modules=documentation.modules,
                configuration_yaml=config_yaml,
                examples=documentation.examples,
                changelog=documentation.changelog
            )
            
            readme_path = output_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"README.md 생성 완료: {readme_path}")
            
        except Exception as e:
            logger.error(f"README.md 생성 실패: {e}")
    
    def _generate_api_doc(self, documentation: PluginDocumentation, output_dir: Path):
        """API.md 생성"""
        try:
            template_path = self.template_dir / "api.md"
            with open(template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            
            content = template.render(
                plugin_name=documentation.plugin_name,
                api_endpoints=documentation.api_endpoints
            )
            
            api_path = output_dir / "API.md"
            with open(api_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"API.md 생성 완료: {api_path}")
            
        except Exception as e:
            logger.error(f"API.md 생성 실패: {e}")
    
    def _generate_examples_doc(self, documentation: PluginDocumentation, output_dir: Path):
        """examples.md 생성"""
        try:
            template_path = self.template_dir / "examples.md"
            with open(template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            
            content = template.render(
                plugin_name=documentation.plugin_name,
                examples=documentation.examples
            )
            
            examples_path = output_dir / "examples.md"
            with open(examples_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"examples.md 생성 완료: {examples_path}")
            
        except Exception as e:
            logger.error(f"examples.md 생성 실패: {e}")
    
    def _generate_changelog_doc(self, documentation: PluginDocumentation, output_dir: Path):
        """changelog.md 생성"""
        try:
            template_path = self.template_dir / "changelog.md"
            with open(template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            
            content = template.render(
                plugin_name=documentation.plugin_name,
                changelog=documentation.changelog
            )
            
            changelog_path = output_dir / "CHANGELOG.md"
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"CHANGELOG.md 생성 완료: {changelog_path}")
            
        except Exception as e:
            logger.error(f"CHANGELOG.md 생성 실패: {e}")
    
    def _generate_metadata(self, documentation: PluginDocumentation, output_dir: Path):
        """메타데이터 JSON 생성"""
        try:
            metadata = {
                'plugin_id': documentation.plugin_id,
                'plugin_name': documentation.plugin_name,
                'version': documentation.version,
                'description': documentation.description,
                'author': documentation.author,
                'generated_at': documentation.generated_at.isoformat() if documentation.generated_at else None,
                'files': [
                    'README.md',
                    'API.md',
                    'examples.md',
                    'CHANGELOG.md'
                ],
                'modules': [module.name for module in documentation.modules],
                'api_endpoints': len(documentation.api_endpoints),
                'examples': len(documentation.examples)
            }
            
            metadata_path = output_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"metadata.json 생성 완료: {metadata_path}")
            
        except Exception as e:
            logger.error(f"metadata.json 생성 실패: {e}")
    
    def generate_all_plugin_docs(self, plugins_dir: str):
        """모든 플러그인 문서 생성"""
        try:
            plugins_path = Path(plugins_dir)
            
            if not plugins_path.exists():
                logger.error(f"플러그인 디렉토리가 존재하지 않습니다: {plugins_dir}")
                return
            
            # 플러그인 디렉토리 찾기
            plugin_dirs = [d for d in plugins_path.iterdir() if d.is_dir()]
            
            for plugin_dir in plugin_dirs:
                try:
                    # 플러그인 설정 파일 찾기
                    config_file = plugin_dir / "config" / "plugin.json"
                    if config_file.exists():
                        # 문서 생성
                        self.generate_documentation(str(plugin_dir))
                        
                except Exception as e:
                    logger.error(f"플러그인 {plugin_dir.name} 문서 생성 실패: {e}")
            
            logger.info(f"모든 플러그인 문서 생성 완료: {len(plugin_dirs)}개")
            
        except Exception as e:
            logger.error(f"일괄 문서 생성 실패: {e}")

def main():
    """메인 함수"""
    try:
        # 문서 생성기 초기화
        generator = PluginDocumentationGenerator()
        
        # 샘플 플러그인 문서 생성
        sample_plugins = [
            {
                'path': 'plugins/analytics_plugin',
                'config': {
                    'id': 'analytics_plugin',
                    'name': 'Analytics Plugin',
                    'version': '1.2.0',
                    'description': '데이터 분석 및 시각화 플러그인',
                    'author': 'Plugin Developer'
                }
            },
            {
                'path': 'plugins/reporting_plugin',
                'config': {
                    'id': 'reporting_plugin',
                    'name': 'Reporting Plugin',
                    'version': '2.1.0',
                    'description': '보고서 생성 및 내보내기 플러그인',
                    'author': 'Plugin Developer'
                }
            }
        ]
        
        for plugin_info in sample_plugins:
            try:
                # 플러그인 디렉토리 생성
                plugin_path = Path(plugin_info['path'])
                plugin_path.mkdir(parents=True, exist_ok=True)
                
                # 샘플 Python 파일 생성
                sample_code = '''"""
샘플 플러그인 코드
"""

def analyze_data(data):
    """
    데이터를 분석합니다.
    
    Args:
        data: 분석할 데이터
        
    Returns:
        dict: 분석 결과
    """
    return {"status": "success", "data": data}

class DataProcessor:
    """데이터 처리 클래스"""
    
    def __init__(self):
        self.processed_count = 0
    
    def process(self, data):
        """데이터를 처리합니다"""
        self.processed_count += 1
        return {"processed": data, "count": self.processed_count}
'''
                
                # 메인 파일 생성
                main_file = plugin_path / "main.py"
                with open(main_file, 'w', encoding='utf-8') as f:
                    f.write(sample_code)
                
                # 설정 파일 생성
                config_dir = plugin_path / "config"
                config_dir.mkdir(exist_ok=True)
                
                config_file = config_dir / "plugin.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(plugin_info['config'], f, indent=2, ensure_ascii=False)
                
                # 문서 생성
                generator.generate_documentation(
                    str(plugin_path)
                )
                
                print(f"플러그인 문서 생성 완료: {plugin_info['config']['name']}")
                
            except Exception as e:
                logger.error(f"플러그인 {plugin_info['config']['name']} 문서 생성 실패: {e}")
        
        logger.info("문서화 자동화 시스템 테스트 완료")
        
    except Exception as e:
        logger.error(f"문서화 자동화 시스템 오류: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 