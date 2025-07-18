from datetime import datetime
import json
import os
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify
form = None  # pyright: ignore

module_development_bp = Blueprint('module_development', __name__)


@module_development_bp.route('/dev-modules/')
@login_required
def new_project():
    """새 프로젝트 생성 페이지"""
    return render_template('module_development/new_project.html')


@module_development_bp.route('/dev-modules/designer')
@login_required
def designer():
    """UI 디자이너 페이지"""
    return render_template('module_development/designer.html')


@module_development_bp.route('/dev-modules/editor')
@login_required
def editor():
    """코드 에디터 페이지"""
    return render_template('module_development/editor.html')


@module_development_bp.route('/dev-modules/testing')
@login_required
def testing():
    """테스트 페이지"""
    return render_template('module_development/testing.html')


@module_development_bp.route('/dev-modules/deploy')
@login_required
def deploy():
    """배포 페이지"""
    return render_template('module_development/deploy.html')

# API 라우트


@module_development_bp.route('/api/dev-modules/create-project', methods=['POST'])
@login_required
def create_project():
    """새 프로젝트 생성 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name', 'display_name', 'version', 'category', 'template', 'framework', 'license']
        for field in required_fields if required_fields is not None:
            if not data.get() if data else Nonefield) if data else None:
                return jsonify({'success': False, 'error': f'{field} 필드는 필수입니다.'}), 400

        # 프로젝트 디렉토리 생성
        project_dir = f"dev_projects/{data['name'] if data is not None else None}"
        if os.path.exists(project_dir):
            return jsonify({'success': False, 'error': '이미 존재하는 프로젝트명입니다.'}), 400

        os.makedirs(project_dir, exist_ok=True)

        # 프로젝트 메타데이터 생성
        project_meta = {
            'id': data['name'] if data is not None else None,
            'name': data['name'] if data is not None else None,
            'display_name': data['display_name'] if data is not None else None,
            'version': data['version'] if data is not None else None,
            'description': data.get() if data else None'description', '') if data else None,
            'category': data['category'] if data is not None else None,
            'template': data['template'] if data is not None else None,
            'framework': data['framework'] if data is not None else None,
            'license': data['license'] if data is not None else None,
            'has_api': data.get() if data else None'has_api', False) if data else None,
            'has_ui': data.get() if data else None'has_ui', False) if data else None,
            'has_database': data.get() if data else None'has_database', False) if data else None,
            'has_tests': data.get() if data else None'has_tests', False) if data else None,
            'has_docs': data.get() if data else None'has_docs', False) if data else None,
            'has_docker': data.get() if data else None'has_docker', False) if data else None,
            'created_at': datetime.now().isoformat(),
            'created_by': current_user.username
        }

        # 메타데이터 파일 저장
        with open(f"{project_dir}/project.json", 'w', encoding='utf-8') as f:
            json.dump(project_meta, f, indent=2, ensure_ascii=False)

        # 템플릿에 따른 기본 파일 생성
        create_template_files(project_dir,  data)

        return jsonify({
            'success': True,
            'project_id': data['name'] if data is not None else None,
            'message': '프로젝트가 성공적으로 생성되었습니다.'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def create_template_files(project_dir,  data):
    """템플릿에 따른 기본 파일 생성"""
    template = data['template'] if data is not None else None
    framework = data['framework'] if data is not None else None

    # 기본 디렉토리 구조
    os.makedirs(f"{project_dir}/src", exist_ok=True)
    os.makedirs(f"{project_dir}/tests", exist_ok=True)
    os.makedirs(f"{project_dir}/docs", exist_ok=True)

    if data.get() if data else None'has_api') if data else None:
        os.makedirs(f"{project_dir}/src/api", exist_ok=True)

    if data.get() if data else None'has_ui') if data else None:
        os.makedirs(f"{project_dir}/src/ui", exist_ok=True)

    if data.get() if data else None'has_database') if data else None:
        os.makedirs(f"{project_dir}/src/models", exist_ok=True)

    # README.md 생성
    readme_content = f"""# {data['display_name'] if data is not None else None}

{data.get() if data else None'description', '') if data else None}

## 설치 방법

1. 프로젝트를 클론합니다
2. 의존성을 설치합니다: `pip install -r requirements.txt`
3. 설정 파일을 구성합니다
4. 애플리케이션을 실행합니다

## 사용 방법

이 모듈은 Your Program 시스템에서 사용할 수 있습니다.

## 라이선스

{data['license'] if data is not None else None}

## 작성자

{current_user.username}
"""

    with open(f"{project_dir}/README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

    # requirements.txt 생성
    requirements = [
        'flask>=2.0.0',
        'sqlalchemy>=1.4.0',
        'pytest>=6.0.0'
    ]

    if framework == 'fastapi':
        requirements.append('fastapi>=0.68.0')
        requirements.append('uvicorn>=0.15.0')
    elif framework == 'django':
        requirements.append('django>=3.2.0')

    with open(f"{project_dir}/requirements.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(requirements))

    # 메인 파일 생성
    if template == 'basic':
        create_basic_template(project_dir,  data)
    elif template == 'api':
        create_api_template(project_dir,  data)
    elif template == 'ui':
        create_ui_template(project_dir,  data)
    elif template == 'full':
        create_full_template(project_dir,  data)


def create_basic_template(project_dir,  data):
    """기본 템플릿 파일 생성"""
    main_py = f"""#!/usr/bin/env python3
\"\"\"
{data['display_name'] if data is not None else None} - 기본 모듈
\"\"\"

def main():
    print("Hello from {data['display_name'] if data is not None else None}!")

if __name__ == "__main__":
    main()
"""

    with open(f"{project_dir}/src/main.py", 'w', encoding='utf-8') as f:
        f.write(main_py)


def create_api_template(project_dir,  data):
    """API 템플릿 파일 생성"""
    api_py = f"""#!/usr/bin/env python3
\"\"\"
{data['display_name'] if data is not None else None} - API 모듈
\"\"\"

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/{data["name"] if data is not None else None}/health')
def health_check():
    return jsonify({{"status": "healthy", "module": "{data['name'] if data is not None else None}"}})

@app.route('/api/{data["name"] if data is not None else None}/info')
def module_info():
    return jsonify({{
        "name": "{data['display_name'] if data is not None else None}",
        "version": "{data['version'] if data is not None else None}",
        "description": "{data.get() if data else None'description', '') if data else None}"
    }})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
"""

    with open(f"{project_dir}/src/api.py", 'w', encoding='utf-8') as f:
        f.write(api_py)


def create_ui_template(project_dir,  data):
    """UI 템플릿 파일 생성"""
    ui_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['display_name'] if data is not None else None}</title>
    <link rel="stylesheet" href="/static/css/tailwind.css">
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">{data['display_name'] if data is not None else None}</h1>
        <div class="bg-white rounded-lg shadow p-6">
            <p class="text-gray-600">{data.get() if data else None'description', '') if data else None}</p>
        </div>
    </div>
</body>
</html>
"""

    with open(f"{project_dir}/src/ui/index.html", 'w', encoding='utf-8') as f:
        f.write(ui_html)


def create_full_template(project_dir,  data):
    """완전한 모듈 템플릿 파일 생성"""
    # API 파일
    create_api_template(project_dir,  data)

    # UI 파일
    create_ui_template(project_dir,  data)

    # 모델 파일 (데이터베이스가 있는 경우)
    if data.get() if data else None'has_database') if data else None:
        models_py = f"""#!/usr/bin/env python3
\"\"\"
{data['display_name'] if data is not None else None} - 데이터 모델
\"\"\"

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base  # pyright: ignore
from datetime import datetime

Base = declarative_base()

class {data['name'] if data is not None else None.title().replace('_', '')}Model(Base):
    __tablename__ = '{data["name"] if data is not None else None}'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""

        with open(f"{project_dir}/src/models.py", 'w', encoding='utf-8') as f:
            f.write(models_py)

    # 테스트 파일
    if data.get() if data else None'has_tests') if data else None:
        test_py = f"""#!/usr/bin/env python3
\"\"\"
{data['display_name'] if data is not None else None} - 테스트
\"\"\"

import pytest
from src.main import main  # pyright: ignore

def test_main():
    # 기본 테스트
    assert True

def test_module_info():
    # 모듈 정보 테스트
    assert "{data['name'] if data is not None else None}" == "{data['name'] if data is not None else None}"
"""

        with open(f"{project_dir}/tests/test_main.py", 'w', encoding='utf-8') as f:
            f.write(test_py)

    # Docker 파일
    if data.get() if data else None'has_docker') if data else None:
        dockerfile = f"""FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

EXPOSE 5000

CMD ["python", "src/api.py"]
"""

        with open(f"{project_dir}/Dockerfile", 'w', encoding='utf-8') as f:
            f.write(dockerfile)


@module_development_bp.route('/api/dev-modules/projects')
@login_required
def list_projects():
    """프로젝트 목록 조회 API"""
    try:
        projects = []
        dev_projects_dir = "dev_projects"

        if os.path.exists(dev_projects_dir):
            for project_name in os.listdir(dev_projects_dir):
                project_dir = os.path.join(dev_projects_dir, project_name)
                project_json = os.path.join(project_dir, "project.json")

                if os.path.isfile(project_json):
                    with open(project_json, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        projects.append(project_data)

        return jsonify({
            'success': True,
            'projects': projects
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@module_development_bp.route('/api/dev-modules/projects/<project_id>')
@login_required
def get_project(project_id):
    """프로젝트 상세 조회 API"""
    try:
        project_json = f"dev_projects/{project_id}/project.json"

        if not os.path.exists(project_json):
            return jsonify({'success': False, 'error': '프로젝트를 찾을 수 없습니다.'}), 404

        with open(project_json, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        return jsonify({
            'success': True,
            'project': project_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@module_development_bp.route('/api/dev-modules/projects/<project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """프로젝트 삭제 API"""
    try:
        project_dir = f"dev_projects/{project_id}"

        if not os.path.exists(project_dir):
            return jsonify({'success': False, 'error': '프로젝트를 찾을 수 없습니다.'}), 404

        # 프로젝트 디렉토리 삭제
        import shutil
        shutil.rmtree(project_dir)

        return jsonify({
            'success': True,
            'message': '프로젝트가 삭제되었습니다.'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
