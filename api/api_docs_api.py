
from flask import Blueprint, request, jsonify, send_file, render_template_string
from api.documentation_generator import APIDocumentationGenerator
import os
import json
from datetime import datetime

# API 문서 생성기 초기화
docs_config = {
    "title": "비즈니스 관리 시스템 API",
    "version": "1.0.0",
    "description": "비즈니스 관리 시스템의 REST API 문서",
    "contact_name": "API Support",
    "contact_email": "support@example.com",
    "server_url": "http://localhost:5000",
    "output_dir": "data/api_docs",
    "enable_swagger_ui": True,
    "enable_redoc": True,
    "enable_postman": True,
    "enable_insomnia": True
}

# Blueprint 생성
api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')

# 전역 변수로 생성기 인스턴스 저장 (나중에 app으로 초기화)
docs_generator = None

def init_docs_generator(app):
    """Flask 앱으로 문서 생성기 초기화"""
    global docs_generator
    docs_generator = APIDocumentationGenerator(app)

@api_docs_bp.route('/health', methods=['GET'])
def health_check():
    """API 문서 시스템 상태 확인"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'API 문서 시스템이 정상적으로 작동합니다',
            'data': {
                'title': docs_config["title"],
                'version': docs_config["version"],
                'output_dir': docs_config["output_dir"]
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 문서 시스템 상태 확인 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/generate', methods=['POST'])
def generate_docs():
    """API 문서 생성"""
    try:
        if not docs_generator:
            return jsonify({
                'status': 'error',
                'message': '문서 생성기가 초기화되지 않았습니다'
            }), 500
        
        success = docs_generator.generate_all_docs()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'API 문서가 성공적으로 생성되었습니다',
                'data': {
                    'generated_at': datetime.now().isoformat(),
                    'output_dir': docs_config["output_dir"]
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'API 문서 생성에 실패했습니다'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 문서 생성 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/files', methods=['GET'])
def list_docs_files():
    """생성된 문서 파일 목록 조회"""
    try:
        if not os.path.exists(docs_config["output_dir"]):
            return jsonify({
                'status': 'success',
                'data': {
                    'files': [],
                    'message': '문서 디렉토리가 존재하지 않습니다'
                }
            }), 200
        
        files = []
        for filename in os.listdir(docs_config["output_dir"]):
            file_path = os.path.join(docs_config["output_dir"], filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': get_file_type(filename)
                })
        
        return jsonify({
            'status': 'success',
            'data': {
                'files': sorted(files, key=lambda x: x['name']),
                'total_count': len(files)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'문서 파일 목록 조회 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/files/<filename>', methods=['GET'])
def download_docs_file(filename):
    """문서 파일 다운로드"""
    try:
        file_path = os.path.join(docs_config["output_dir"], filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': '파일을 찾을 수 없습니다'
            }), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'파일 다운로드 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/openapi', methods=['GET'])
def get_openapi_spec():
    """OpenAPI 스펙 조회"""
    try:
        json_path = os.path.join(docs_config["output_dir"], "openapi.json")
        
        if not os.path.exists(json_path):
            return jsonify({
                'status': 'error',
                'message': 'OpenAPI 스펙이 생성되지 않았습니다. 먼저 문서를 생성해주세요.'
            }), 404
        
        with open(json_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        return jsonify(spec), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'OpenAPI 스펙 조회 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/swagger', methods=['GET'])
def swagger_ui():
    """Swagger UI 제공"""
    try:
        swagger_html = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API 문서 - Swagger UI</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
            <style>
                html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
                *, *:before, *:after { box-sizing: inherit; }
                body { margin:0; background: #fafafa; }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {
                    const ui = SwaggerUIBundle({
                        url: '/api/docs/openapi',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout"
                    });
                };
            </script>
        </body>
        </html>
        """
        
        return swagger_html, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Swagger UI 생성 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/redoc', methods=['GET'])
def redoc_ui():
    """ReDoc UI 제공"""
    try:
        redoc_html = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API 문서 - ReDoc</title>
            <style>
                body { margin: 0; padding: 0; }
            </style>
        </head>
        <body>
            <redoc spec-url="/api/docs/openapi"></redoc>
            <script src="https://unpkg.com/redoc@2.1.3/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        """
        
        return redoc_html, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ReDoc UI 생성 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/stats', methods=['GET'])
def get_docs_stats():
    """문서 생성 통계 조회"""
    try:
        if not docs_generator:
            return jsonify({
                'status': 'error',
                'message': '문서 생성기가 초기화되지 않았습니다'
            }), 500
        
        # 엔드포인트 통계
        docs_generator.scan_endpoints()
        endpoint_count = len(docs_generator.endpoints)
        
        # 태그별 통계
        tag_stats = {}
        for endpoint in docs_generator.endpoints:
            for tag in endpoint.tags:
                if tag not in tag_stats:
                    tag_stats[tag] = 0
                tag_stats[tag] += 1
        
        # 파일 통계
        file_count = 0
        total_size = 0
        if os.path.exists(docs_config["output_dir"]):
            for filename in os.listdir(docs_config["output_dir"]):
                file_path = os.path.join(docs_config["output_dir"], filename)
                if os.path.isfile(file_path):
                    file_count += 1
                    total_size += os.path.getsize(file_path)
        
        return jsonify({
            'status': 'success',
            'data': {
                'endpoint_count': endpoint_count,
                'tag_stats': tag_stats,
                'file_count': file_count,
                'total_size': total_size,
                'config': {
                    'title': docs_config["title"],
                    'version': docs_config["version"],
                    'output_dir': docs_config["output_dir"]
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'문서 통계 조회 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/config', methods=['GET'])
def get_docs_config():
    """문서 설정 조회"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'title': docs_config["title"],
                'version': docs_config["version"],
                'description': docs_config["description"],
                'contact_name': docs_config["contact_name"],
                'contact_email': docs_config["contact_email"],
                'server_url': docs_config["server_url"],
                'output_dir': docs_config["output_dir"],
                'enable_swagger_ui': docs_config["enable_swagger_ui"],
                'enable_redoc': docs_config["enable_redoc"],
                'enable_postman': docs_config["enable_postman"],
                'enable_insomnia': docs_config["enable_insomnia"]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 조회 실패: {str(e)}'
        }), 500

@api_docs_bp.route('/config', methods=['PUT'])
def update_docs_config():
    """문서 설정 업데이트"""
    try:
        data = request.get_json()
        
        # 설정 업데이트
        if 'title' in data:
            docs_config["title"] = data['title']
        if 'version' in data:
            docs_config["version"] = data['version']
        if 'description' in data:
            docs_config["description"] = data['description']
        if 'contact_name' in data:
            docs_config["contact_name"] = data['contact_name']
        if 'contact_email' in data:
            docs_config["contact_email"] = data['contact_email']
        if 'server_url' in data:
            docs_config["server_url"] = data['server_url']
        if 'enable_swagger_ui' in data:
            docs_config["enable_swagger_ui"] = data['enable_swagger_ui']
        if 'enable_redoc' in data:
            docs_config["enable_redoc"] = data['enable_redoc']
        if 'enable_postman' in data:
            docs_config["enable_postman"] = data['enable_postman']
        if 'enable_insomnia' in data:
            docs_config["enable_insomnia"] = data['enable_insomnia']
        
        return jsonify({
            'status': 'success',
            'message': '문서 설정이 업데이트되었습니다'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 업데이트 실패: {str(e)}'
        }), 500

def get_file_type(filename):
    """파일 타입 반환"""
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.json':
        return 'JSON'
    elif ext == '.yaml' or ext == '.yml':
        return 'YAML'
    elif ext == '.md':
        return 'Markdown'
    else:
        return 'Unknown' 