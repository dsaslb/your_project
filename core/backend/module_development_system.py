#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모듈 개발 모드 시스템
실제 SaaS/노코드 툴 수준의 개발·테스트·배포 시스템
"""

import os
import json
import sqlite3
import shutil
import zipfile
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
import time

class ModuleDevelopmentSystem:
    def __init__(self, sandbox_path: str = "sandbox", production_path: str = "production"):
        self.sandbox_path = Path(sandbox_path)
        self.production_path = Path(production_path)
        self.sandbox_path.mkdir(exist_ok=True)
        self.production_path.mkdir(exist_ok=True)
        
        self.init_sandbox_database()
        self.init_component_library()
        self.create_sample_projects()
    
    def init_sandbox_database(self):
        """샌드박스 데이터베이스 초기화"""
        db_path = self.sandbox_path / "sandbox.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 개발 프로젝트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS development_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                module_type TEXT NOT NULL,
                status TEXT DEFAULT 'development',
                version TEXT DEFAULT '1.0.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT NOT NULL,
                settings TEXT,
                preview_data TEXT
            )
        ''')
        
        # 컴포넌트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                component_id TEXT NOT NULL,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                position_x INTEGER DEFAULT 0,
                position_y INTEGER DEFAULT 0,
                width INTEGER DEFAULT 200,
                height INTEGER DEFAULT 100,
                properties TEXT,
                styles TEXT,
                parent_id TEXT,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES development_projects (project_id)
            )
        ''')
        
        # 페이지 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                page_id TEXT NOT NULL,
                name TEXT NOT NULL,
                route TEXT NOT NULL,
                layout TEXT DEFAULT 'default',
                components TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES development_projects (project_id)
            )
        ''')
        
        # 버전 관리 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                version_id TEXT NOT NULL,
                version_name TEXT NOT NULL,
                description TEXT,
                snapshot_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES development_projects (project_id)
            )
        ''')
        
        # 배포 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                deployment_id TEXT NOT NULL,
                version_id TEXT NOT NULL,
                environment TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                deployed_at TIMESTAMP,
                deployed_by TEXT NOT NULL,
                rollback_available BOOLEAN DEFAULT 1,
                FOREIGN KEY (project_id) REFERENCES development_projects (project_id)
            )
        ''')
        
        # 테스트 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                data_type TEXT NOT NULL,
                data_name TEXT NOT NULL,
                data_content TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES development_projects (project_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_component_library(self):
        """컴포넌트 라이브러리 초기화"""
        self.component_library = {
            'basic': [
                {
                    'type': 'button',
                    'name': '버튼',
                    'icon': '🔘',
                    'default_properties': {
                        'text': '버튼',
                        'variant': 'primary',
                        'size': 'medium'
                    },
                    'default_styles': {
                        'backgroundColor': '#3498db',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'padding': '8px 16px',
                        'cursor': 'pointer'
                    }
                },
                {
                    'type': 'card',
                    'name': '카드',
                    'icon': '🃏',
                    'default_properties': {
                        'title': '카드 제목',
                        'content': '카드 내용'
                    },
                    'default_styles': {
                        'backgroundColor': 'white',
                        'border': '1px solid #ddd',
                        'borderRadius': '8px',
                        'padding': '16px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }
                },
                {
                    'type': 'form',
                    'name': '폼',
                    'icon': '📝',
                    'default_properties': {
                        'title': '폼 제목',
                        'fields': []
                    },
                    'default_styles': {
                        'backgroundColor': 'white',
                        'border': '1px solid #ddd',
                        'borderRadius': '8px',
                        'padding': '20px'
                    }
                },
                {
                    'type': 'input',
                    'name': '입력 필드',
                    'icon': '📝',
                    'default_properties': {
                        'placeholder': '입력하세요',
                        'type': 'text',
                        'label': '라벨'
                    },
                    'default_styles': {
                        'border': '1px solid #ddd',
                        'borderRadius': '4px',
                        'padding': '8px 12px',
                        'width': '100%'
                    }
                },
                {
                    'type': 'table',
                    'name': '테이블',
                    'icon': '📊',
                    'default_properties': {
                        'headers': ['컬럼1', '컬럼2', '컬럼3'],
                        'data': [['데이터1', '데이터2', '데이터3']]
                    },
                    'default_styles': {
                        'width': '100%',
                        'borderCollapse': 'collapse',
                        'border': '1px solid #ddd'
                    }
                }
            ],
            'advanced': [
                {
                    'type': 'chart',
                    'name': '차트',
                    'icon': '📈',
                    'default_properties': {
                        'type': 'line',
                        'data': {'labels': ['1월', '2월', '3월'], 'values': [10, 20, 15]}
                    },
                    'default_styles': {
                        'width': '100%',
                        'height': '300px'
                    }
                },
                {
                    'type': 'calendar',
                    'name': '캘린더',
                    'icon': '📅',
                    'default_properties': {
                        'view': 'month',
                        'events': []
                    },
                    'default_styles': {
                        'width': '100%',
                        'height': '400px'
                    }
                },
                {
                    'type': 'modal',
                    'name': '모달',
                    'icon': '🪟',
                    'default_properties': {
                        'title': '모달 제목',
                        'content': '모달 내용',
                        'show': False
                    },
                    'default_styles': {
                        'position': 'fixed',
                        'top': '50%',
                        'left': '50%',
                        'transform': 'translate(-50%, -50%)',
                        'backgroundColor': 'white',
                        'padding': '20px',
                        'borderRadius': '8px',
                        'boxShadow': '0 4px 20px rgba(0,0,0,0.3)'
                    }
                }
            ]
        }
    
    def create_project(self, name: str, description: str, module_type: str, created_by: str) -> Dict:
        """새 개발 프로젝트 생성"""
        project_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO development_projects 
            (project_id, name, description, module_type, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, name, description, module_type, created_by))
        
        # 프로젝트 디렉토리 생성
        project_dir = self.sandbox_path / project_id
        project_dir.mkdir(exist_ok=True)
        
        # 기본 파일 생성
        self.create_project_files(project_dir, name, module_type)
        
        conn.commit()
        conn.close()
        
        return {
            'project_id': project_id,
            'name': name,
            'status': 'development',
            'created_at': datetime.now().isoformat()
        }
    
    def create_project_files(self, project_dir: Path, name: str, module_type: str):
        """프로젝트 기본 파일 생성"""
        # package.json
        package_json = {
            'name': name.lower().replace(' ', '-'),
            'version': '1.0.0',
            'description': f'{name} 모듈',
            'type': module_type,
            'main': 'index.js',
            'scripts': {
                'dev': 'python -m flask run --port 5002',
                'build': 'python build.py',
                'test': 'python test.py'
            },
            'dependencies': {
                'flask': '^2.0.0',
                'sqlite3': '^3.0.0'
            }
        }
        
        with open(project_dir / 'package.json', 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)
        
        # 기본 Python 파일
        main_py = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name} 모듈
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    return jsonify({{'message': 'Hello from {name}!'}})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
'''
        
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(main_py)
        
        # templates 디렉토리
        templates_dir = project_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)
        
        # 기본 HTML 템플릿
        index_html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{name} 모듈</h1>
        <p>이 페이지는 {name} 모듈의 메인 페이지입니다.</p>
        <div id="app">
            <!-- 여기에 컴포넌트들이 렌더링됩니다 -->
        </div>
    </div>
    
    <script>
        // API 호출 예시
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {{
                console.log(data);
            }});
    </script>
</body>
</html>
'''
        
        with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(index_html)
    
    def get_projects(self, user_id: str) -> List[Dict]:
        """사용자의 프로젝트 목록 조회"""
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT project_id, name, description, module_type, status, version, 
                   created_at, updated_at
            FROM development_projects 
            WHERE created_by = ?
            ORDER BY updated_at DESC
        ''', (user_id,))
        
        projects = []
        for row in cursor.fetchall():
            projects.append({
                'project_id': row[0],
                'name': row[1],
                'description': row[2],
                'module_type': row[3],
                'status': row[4],
                'version': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            })
        
        conn.close()
        return projects
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """프로젝트 상세 정보 조회"""
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT project_id, name, description, module_type, status, version, 
                   created_at, updated_at, settings, preview_data
            FROM development_projects 
            WHERE project_id = ?
        ''', (project_id,))
        
        row = cursor.fetchone()
        if row:
            project = {
                'project_id': row[0],
                'name': row[1],
                'description': row[2],
                'module_type': row[3],
                'status': row[4],
                'version': row[5],
                'created_at': row[6],
                'updated_at': row[7],
                'settings': json.loads(row[8]) if row[8] else {},
                'preview_data': json.loads(row[9]) if row[9] else {}
            }
            
            # 컴포넌트 목록 조회
            cursor.execute('''
                SELECT component_id, type, name, position_x, position_y, 
                       width, height, properties, styles, parent_id, order_index
                FROM components 
                WHERE project_id = ?
                ORDER BY order_index
            ''', (project_id,))
            
            components = []
            for comp_row in cursor.fetchall():
                components.append({
                    'component_id': comp_row[0],
                    'type': comp_row[1],
                    'name': comp_row[2],
                    'position_x': comp_row[3],
                    'position_y': comp_row[4],
                    'width': comp_row[5],
                    'height': comp_row[6],
                    'properties': json.loads(comp_row[7]) if comp_row[7] else {},
                    'styles': json.loads(comp_row[8]) if comp_row[8] else {},
                    'parent_id': comp_row[9],
                    'order_index': comp_row[10]
                })
            
            project['components'] = components
            
            conn.close()
            return project
        
        conn.close()
        return None
    
    def add_component(self, project_id: str, component_data: Dict) -> Dict:
        """컴포넌트 추가"""
        component_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO components 
            (project_id, component_id, type, name, position_x, position_y, 
             width, height, properties, styles, parent_id, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            component_id,
            component_data['type'],
            component_data['name'],
            component_data.get('position_x', 0),
            component_data.get('position_y', 0),
            component_data.get('width', 200),
            component_data.get('height', 100),
            json.dumps(component_data.get('properties', {})),
            json.dumps(component_data.get('styles', {})),
            component_data.get('parent_id'),
            component_data.get('order_index', 0)
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'component_id': component_id,
            'success': True
        }
    
    def update_component(self, project_id: str, component_id: str, updates: Dict) -> Dict:
        """컴포넌트 업데이트"""
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        # 업데이트할 필드들
        update_fields = []
        params = []
        
        for field, value in updates.items():
            if field in ['position_x', 'position_y', 'width', 'height', 'order_index']:
                update_fields.append(f"{field} = ?")
                params.append(value)
            elif field in ['properties', 'styles']:
                update_fields.append(f"{field} = ?")
                params.append(json.dumps(value))
            elif field in ['type', 'name', 'parent_id']:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if update_fields:
            params.extend([project_id, component_id])
            query = f'''
                UPDATE components 
                SET {', '.join(update_fields)}
                WHERE project_id = ? AND component_id = ?
            '''
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            return {'success': True}
        
        conn.close()
        return {'success': False, 'error': '업데이트할 필드가 없습니다.'}
    
    def delete_component(self, project_id: str, component_id: str) -> Dict:
        """컴포넌트 삭제"""
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM components 
            WHERE project_id = ? AND component_id = ?
        ''', (project_id, component_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def create_version(self, project_id: str, version_name: str, description: str, created_by: str) -> Dict:
        """버전 스냅샷 생성"""
        version_id = str(uuid.uuid4())
        
        # 현재 프로젝트 상태 스냅샷
        project = self.get_project(project_id)
        if not project:
            return {'success': False, 'error': '프로젝트를 찾을 수 없습니다.'}
        
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO versions 
            (project_id, version_id, version_name, description, snapshot_data, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            version_id,
            version_name,
            description,
            json.dumps(project),
            created_by
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'version_id': version_id,
            'success': True
        }
    
    def get_versions(self, project_id: str) -> List[Dict]:
        """프로젝트 버전 목록 조회"""
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version_id, version_name, description, created_at, created_by
            FROM versions 
            WHERE project_id = ?
            ORDER BY created_at DESC
        ''', (project_id,))
        
        versions = []
        for row in cursor.fetchall():
            versions.append({
                'version_id': row[0],
                'version_name': row[1],
                'description': row[2],
                'created_at': row[3],
                'created_by': row[4]
            })
        
        conn.close()
        return versions
    
    def rollback_version(self, project_id: str, version_id: str) -> Dict:
        """버전 롤백"""
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        # 버전 스냅샷 조회
        cursor.execute('''
            SELECT snapshot_data FROM versions 
            WHERE project_id = ? AND version_id = ?
        ''', (project_id, version_id))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'success': False, 'error': '버전을 찾을 수 없습니다.'}
        
        snapshot = json.loads(row[0])
        
        # 현재 컴포넌트 삭제
        cursor.execute('DELETE FROM components WHERE project_id = ?', (project_id,))
        
        # 스냅샷에서 컴포넌트 복원
        for component in snapshot.get('components', []):
            cursor.execute('''
                INSERT INTO components 
                (project_id, component_id, type, name, position_x, position_y, 
                 width, height, properties, styles, parent_id, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                component['component_id'],
                component['type'],
                component['name'],
                component['position_x'],
                component['position_y'],
                component['width'],
                component['height'],
                json.dumps(component['properties']),
                json.dumps(component['styles']),
                component['parent_id'],
                component['order_index']
            ))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def deploy_project(self, project_id: str, version_id: str, environment: str, deployed_by: str) -> Dict:
        """프로젝트 배포"""
        deployment_id = str(uuid.uuid4())
        
        # 프로젝트 정보 조회
        project = self.get_project(project_id)
        if not project:
            return {'success': False, 'error': '프로젝트를 찾을 수 없습니다.'}
        
        # 배포 패키지 생성
        package_path = self.create_deployment_package(project_id, project)
        
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deployments 
            (project_id, deployment_id, version_id, environment, status, deployed_at, deployed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            deployment_id,
            version_id,
            environment,
            'deployed',
            datetime.now().isoformat(),
            deployed_by
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'deployment_id': deployment_id,
            'package_path': str(package_path),
            'success': True
        }
    
    def create_deployment_package(self, project_id: str, project: Dict) -> Path:
        """배포 패키지 생성"""
        project_dir = self.sandbox_path / project_id
        package_path = self.production_path / f"{project['name']}_{project_id}.zip"
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)
        
        return package_path
    
    def generate_test_data(self, project_id: str, data_type: str) -> Dict:
        """테스트 데이터 생성"""
        test_data = {
            'users': [
                {'id': 1, 'name': '김철수', 'email': 'kim@test.com', 'role': 'user'},
                {'id': 2, 'name': '이영희', 'email': 'lee@test.com', 'role': 'admin'},
                {'id': 3, 'name': '박민수', 'email': 'park@test.com', 'role': 'user'}
            ],
            'products': [
                {'id': 1, 'name': '상품 A', 'price': 10000, 'category': '전자제품'},
                {'id': 2, 'name': '상품 B', 'price': 20000, 'category': '의류'},
                {'id': 3, 'name': '상품 C', 'price': 15000, 'category': '식품'}
            ],
            'orders': [
                {'id': 1, 'user_id': 1, 'product_id': 1, 'quantity': 2, 'total': 20000},
                {'id': 2, 'user_id': 2, 'product_id': 2, 'quantity': 1, 'total': 20000},
                {'id': 3, 'user_id': 3, 'product_id': 3, 'quantity': 3, 'total': 45000}
            ]
        }
        
        if data_type in test_data:
            conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_data (project_id, data_type, data_name, data_content)
                VALUES (?, ?, ?, ?)
            ''', (
                project_id,
                data_type,
                f'{data_type}_sample',
                json.dumps(test_data[data_type])
            ))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'data': test_data[data_type]}
        
        return {'success': False, 'error': '지원하지 않는 데이터 타입입니다.'}
    
    def get_component_library(self) -> Dict:
        """컴포넌트 라이브러리 반환"""
        return self.component_library
    
    def get_deployment_statistics(self, user_id: str) -> Dict:
        """배포 통계 조회"""
        conn = sqlite3.connect(self.sandbox_path / "sandbox.db")
        cursor = conn.cursor()
        
        # 전체 프로젝트 수
        cursor.execute('''
            SELECT COUNT(*) FROM development_projects WHERE created_by = ?
        ''', (user_id,))
        total_projects = cursor.fetchone()[0]
        
        # 상태별 프로젝트 수
        cursor.execute('''
            SELECT status, COUNT(*) FROM development_projects 
            WHERE created_by = ? GROUP BY status
        ''', (user_id,))
        status_counts = dict(cursor.fetchall())
        
        # 최근 배포
        cursor.execute('''
            SELECT d.deployment_id, p.name, d.environment, d.deployed_at
            FROM deployments d
            JOIN development_projects p ON d.project_id = p.project_id
            WHERE p.created_by = ?
            ORDER BY d.deployed_at DESC
            LIMIT 5
        ''', (user_id,))
        
        recent_deployments = []
        for row in cursor.fetchall():
            recent_deployments.append({
                'deployment_id': row[0],
                'project_name': row[1],
                'environment': row[2],
                'deployed_at': row[3]
            })
        
        conn.close()
        
        return {
            'total_projects': total_projects,
            'status_counts': status_counts,
            'recent_deployments': recent_deployments
        }

    def create_sample_projects(self):
        """샘플 프로젝트 생성"""
        sample_projects = [
            {
                'name': '출퇴근 관리 시스템',
                'description': '직원들의 출퇴근 시간을 관리하는 모듈',
                'module_type': 'attendance',
                'status': 'development',
                'created_by': 'default_user'
            },
            {
                'name': '재고 관리 대시보드',
                'description': '실시간 재고 현황을 모니터링하는 대시보드',
                'module_type': 'inventory',
                'status': 'deployed',
                'created_by': 'default_user'
            },
            {
                'name': '고객 피드백 시스템',
                'description': '고객 의견을 수집하고 분석하는 시스템',
                'module_type': 'feedback',
                'status': 'development',
                'created_by': 'default_user'
            }
        ]
        
        for project_data in sample_projects:
            try:
                # 프로젝트가 이미 존재하는지 확인
                existing_projects = self.get_projects('default_user')
                project_exists = any(p['name'] == project_data['name'] for p in existing_projects)
                
                if not project_exists:
                    self.create_project(
                        project_data['name'],
                        project_data['description'],
                        project_data['module_type'],
                        project_data['created_by']
                    )
            except Exception as e:
                print(f"샘플 프로젝트 생성 실패: {e}")

# 전역 인스턴스
module_development_system = ModuleDevelopmentSystem()
dev_system = module_development_system  # 호환성을 위한 별칭 