from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import json
import os
from datetime import datetime
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

# Swagger UI 설정
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "퀀텀 비즈니스 관리 시스템 API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# API 문서 데이터
api_documentation = {
    "openapi": "3.0.0",
    "info": {
        "title": "퀀텀 비즈니스 관리 시스템 API",
        "description": "비즈니스 관리를 위한 종합 API 시스템",
        "version": "1.0.0",
        "contact": {
            "name": "API 지원팀",
            "email": "support@quantum-business.com"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "개발 서버"
        },
        {
            "url": "https://api.quantum-business.com",
            "description": "프로덕션 서버"
        }
    ],
    "paths": {
        # 인증 관련 API
        "/api/auth/login": {
            "post": {
                "tags": ["인증"],
                "summary": "사용자 로그인",
                "description": "이메일과 비밀번호로 사용자 로그인",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {
                                        "type": "string",
                                        "format": "email",
                                        "example": "user@example.com"
                                    },
                                    "password": {
                                        "type": "string",
                                        "example": "password123"
                                    }
                                },
                                "required": ["email", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "로그인 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "token": {"type": "string"},
                                        "user": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "email": {"type": "string"},
                                                "role": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "인증 실패",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # 대시보드 API
        "/api/dashboard/stats": {
            "get": {
                "tags": ["대시보드"],
                "summary": "대시보드 통계 조회",
                "description": "대시보드에 표시할 주요 통계 정보 조회",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "통계 정보 조회 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "totalStores": {"type": "integer"},
                                        "activeOrders": {"type": "integer"},
                                        "lowStockItems": {"type": "integer"},
                                        "todaySales": {"type": "number"},
                                        "pendingTasks": {"type": "integer"},
                                        "notifications": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # 매장 관리 API
        "/api/stores": {
            "get": {
                "tags": ["매장 관리"],
                "summary": "매장 목록 조회",
                "description": "등록된 모든 매장 정보 조회",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "description": "페이지 번호",
                        "required": False,
                        "schema": {"type": "integer", "default": 1}
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "description": "페이지당 항목 수",
                        "required": False,
                        "schema": {"type": "integer", "default": 10}
                    },
                    {
                        "name": "search",
                        "in": "query",
                        "description": "검색어",
                        "required": False,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "매장 목록 조회 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "stores": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "address": {"type": "string"},
                                                    "phone": {"type": "string"},
                                                    "manager": {"type": "string"},
                                                    "status": {"type": "string"},
                                                    "sales": {"type": "number"},
                                                    "employees": {"type": "integer"}
                                                }
                                            }
                                        },
                                        "total": {"type": "integer"},
                                        "page": {"type": "integer"},
                                        "pages": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["매장 관리"],
                "summary": "새 매장 등록",
                "description": "새로운 매장 정보 등록",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "address": {"type": "string"},
                                    "phone": {"type": "string"},
                                    "manager": {"type": "string"},
                                    "description": {"type": "string"}
                                },
                                "required": ["name", "address", "phone", "manager"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "매장 등록 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"},
                                        "store": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # 재고 관리 API
        "/api/inventory": {
            "get": {
                "tags": ["재고 관리"],
                "summary": "재고 목록 조회",
                "description": "재고 현황 조회",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "category",
                        "in": "query",
                        "description": "카테고리 필터",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "status",
                        "in": "query",
                        "description": "상태 필터 (normal/low/out)",
                        "required": False,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "재고 목록 조회 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "category": {"type": "string"},
                                            "currentStock": {"type": "integer"},
                                            "minStock": {"type": "integer"},
                                            "maxStock": {"type": "integer"},
                                            "unit": {"type": "string"},
                                            "price": {"type": "number"},
                                            "status": {"type": "string"},
                                            "lastUpdated": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # 주문 관리 API
        "/api/orders": {
            "get": {
                "tags": ["주문 관리"],
                "summary": "주문 목록 조회",
                "description": "주문 현황 조회",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "description": "주문 상태 필터",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "store_id",
                        "in": "query",
                        "description": "매장 ID 필터",
                        "required": False,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "주문 목록 조회 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "orderNumber": {"type": "string"},
                                            "customerName": {"type": "string"},
                                            "items": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            },
                                            "totalAmount": {"type": "number"},
                                            "status": {"type": "string"},
                                            "orderTime": {"type": "string"},
                                            "storeName": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # 스케줄 관리 API
        "/api/schedules": {
            "get": {
                "tags": ["스케줄 관리"],
                "summary": "스케줄 목록 조회",
                "description": "직원 스케줄 조회",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "date",
                        "in": "query",
                        "description": "날짜 필터 (YYYY-MM-DD)",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "status",
                        "in": "query",
                        "description": "상태 필터",
                        "required": False,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "스케줄 목록 조회 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "employeeName": {"type": "string"},
                                            "date": {"type": "string"},
                                            "startTime": {"type": "string"},
                                            "endTime": {"type": "string"},
                                            "position": {"type": "string"},
                                            "status": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # 알림 API
        "/api/notifications": {
            "get": {
                "tags": ["알림"],
                "summary": "알림 목록 조회",
                "description": "사용자 알림 조회",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "type",
                        "in": "query",
                        "description": "알림 타입 필터",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "isRead",
                        "in": "query",
                        "description": "읽음 상태 필터",
                        "required": False,
                        "schema": {"type": "boolean"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "알림 목록 조회 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "title": {"type": "string"},
                                            "message": {"type": "string"},
                                            "type": {"type": "string"},
                                            "timestamp": {"type": "string"},
                                            "isRead": {"type": "boolean"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # 사용자 관리 API
        "/api/users": {
            "get": {
                "tags": ["사용자 관리"],
                "summary": "사용자 목록 조회",
                "description": "시스템 사용자 목록 조회",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "사용자 목록 조회 성공",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "email": {"type": "string"},
                                            "role": {"type": "string"},
                                            "status": {"type": "string"},
                                            "createdAt": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "schemas": {
            "Error": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "error_code": {"type": "string"}
                }
            },
            "Success": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        }
    },
    "tags": [
        {
            "name": "인증",
            "description": "사용자 인증 관련 API"
        },
        {
            "name": "대시보드",
            "description": "대시보드 관련 API"
        },
        {
            "name": "매장 관리",
            "description": "매장 정보 관리 API"
        },
        {
            "name": "재고 관리",
            "description": "재고 현황 관리 API"
        },
        {
            "name": "주문 관리",
            "description": "주문 처리 관리 API"
        },
        {
            "name": "스케줄 관리",
            "description": "직원 스케줄 관리 API"
        },
        {
            "name": "알림",
            "description": "시스템 알림 관리 API"
        },
        {
            "name": "사용자 관리",
            "description": "사용자 계정 관리 API"
        }
    ]
}

@app.route('/static/swagger.json')
def swagger_json():
    """Swagger JSON 파일 제공"""
    return jsonify(api_documentation)

@app.route('/api/docs/health')
def health_check():
    """API 문서 서버 상태 확인"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "API Documentation Server"
    })

@app.route('/api/docs/export')
def export_documentation():
    """API 문서 내보내기"""
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify(api_documentation)
    elif format_type == 'yaml':
        import yaml
        return yaml.dump(api_documentation, default_flow_style=False), 200, {'Content-Type': 'text/yaml'}
    else:
        return jsonify({"error": "지원하지 않는 형식입니다. json 또는 yaml을 사용하세요."}), 400

@app.route('/api/docs/version')
def get_version():
    """API 버전 정보"""
    return jsonify({
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "endpoints_count": len(api_documentation["paths"]),
        "tags_count": len(api_documentation["tags"])
    })

if __name__ == '__main__':
    # static 폴더 생성
    os.makedirs('static', exist_ok=True)
    
    # Swagger JSON 파일 저장
    with open('static/swagger.json', 'w', encoding='utf-8') as f:
        json.dump(api_documentation, f, ensure_ascii=False, indent=2)
    
    print("🚀 API 문서 서버 시작")
    print(f"📖 Swagger UI: http://localhost:5000{SWAGGER_URL}")
    print(f"📄 API 문서 JSON: http://localhost:5000/static/swagger.json")
    print(f"💚 상태 확인: http://localhost:5000/api/docs/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 