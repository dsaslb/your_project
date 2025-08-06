"""
Swagger API 문서화 설정
RESTful API 자동 문서화 및 테스트 인터페이스
"""

from flask import Blueprint, jsonify, request, current_app
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Swagger UI 설정
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

def create_swagger_config(app):
    """Swagger 설정 생성"""
    
    # Swagger UI 블루프린트 생성
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "멀티테넌시 관리 시스템 API",
            'deepLinking': True,
            'displayOperationId': True,
            'defaultModelsExpandDepth': 2,
            'defaultModelExpandDepth': 2,
            'docExpansion': 'list',
            'filter': True,
            'showExtensions': True,
            'showCommonExtensions': True,
            'syntaxHighlight.theme': 'monokai'
        }
    )
    
    # Swagger JSON 생성
    swagger_spec = generate_swagger_spec()
    
    # 정적 파일로 Swagger JSON 저장
    static_dir = os.path.join(app.root_path, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    swagger_file = os.path.join(static_dir, 'swagger.json')
    with open(swagger_file, 'w', encoding='utf-8') as f:
        json.dump(swagger_spec, f, ensure_ascii=False, indent=2)
    
    # 블루프린트 등록
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return swaggerui_blueprint

def generate_swagger_spec() -> Dict[str, Any]:
    """Swagger 스펙 생성"""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "멀티테넌시 관리 시스템 API",
            "description": "업종-브랜드-매장-직원 계층 구조를 지원하는 멀티테넌시 관리 시스템 API",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@example.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "개발 서버"
            },
            {
                "url": "https://api.example.com",
                "description": "프로덕션 서버"
            }
        ],
        "security": [
            {
                "bearerAuth": []
            },
            {
                "apiKeyAuth": []
            }
        ],
        "paths": {
            "/api/auth/login": {
                "post": {
                    "tags": ["인증"],
                    "summary": "사용자 로그인",
                    "description": "사용자 인증 및 JWT 토큰 발급",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LoginRequest"
                                },
                                "example": {
                                    "username": "admin",
                                    "password": "password123"
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
                                        "$ref": "#/components/schemas/LoginResponse"
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "인증 실패",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/staff/list": {
                "get": {
                    "tags": ["직원 관리"],
                    "summary": "직원 목록 조회",
                    "description": "페이지네이션을 지원하는 직원 목록 조회",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "페이지 번호",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 1,
                                "minimum": 1
                            }
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "페이지당 항목 수",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "description": "검색어",
                            "required": False,
                            "schema": {
                                "type": "string"
                            }
                        },
                        {
                            "name": "role",
                            "in": "query",
                            "description": "역할 필터",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["admin", "brand_admin", "store_admin", "employee"]
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "직원 목록 조회 성공",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/StaffListResponse"
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "권한 없음",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/staff/create": {
                "post": {
                    "tags": ["직원 관리"],
                    "summary": "직원 생성",
                    "description": "새로운 직원 계정 생성",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/StaffCreateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "직원 생성 성공",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/StaffResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "잘못된 요청",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/admin/dashboard-stats": {
                "get": {
                    "tags": ["관리자"],
                    "summary": "대시보드 통계",
                    "description": "관리자 대시보드용 통계 데이터",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "통계 데이터 조회 성공",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DashboardStatsResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/health": {
                "get": {
                    "tags": ["시스템"],
                    "summary": "시스템 상태 확인",
                    "description": "애플리케이션 및 데이터베이스 상태 확인",
                    "responses": {
                        "200": {
                            "description": "시스템 정상",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthResponse"
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
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT 토큰을 사용한 인증"
                },
                "apiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API 키를 사용한 인증"
                }
            },
            "schemas": {
                "LoginRequest": {
                    "type": "object",
                    "required": ["username", "password"],
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "사용자명",
                            "example": "admin"
                        },
                        "password": {
                            "type": "string",
                            "description": "비밀번호",
                            "example": "password123"
                        }
                    }
                },
                "LoginResponse": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean",
                            "example": True
                        },
                        "message": {
                            "type": "string",
                            "example": "로그인 성공"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "token": {
                                    "type": "string",
                                    "description": "JWT 토큰"
                                },
                                "user": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        }
                    }
                },
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "사용자 ID"
                        },
                        "username": {
                            "type": "string",
                            "description": "사용자명"
                        },
                        "email": {
                            "type": "string",
                            "description": "이메일"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["admin", "brand_admin", "store_admin", "employee"],
                            "description": "사용자 역할"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "inactive", "pending"],
                            "description": "계정 상태"
                        }
                    }
                },
                "StaffCreateRequest": {
                    "type": "object",
                    "required": ["username", "email", "password", "name"],
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "사용자명"
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "이메일"
                        },
                        "password": {
                            "type": "string",
                            "minLength": 8,
                            "description": "비밀번호"
                        },
                        "name": {
                            "type": "string",
                            "description": "실명"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["admin", "brand_admin", "store_admin", "employee"],
                            "default": "employee"
                        },
                        "branch_id": {
                            "type": "integer",
                            "description": "소속 매장 ID"
                        }
                    }
                },
                "StaffResponse": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean"
                        },
                        "message": {
                            "type": "string"
                        },
                        "data": {
                            "$ref": "#/components/schemas/User"
                        }
                    }
                },
                "StaffListResponse": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "staff": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                },
                                "pagination": {
                                    "$ref": "#/components/schemas/Pagination"
                                }
                            }
                        }
                    }
                },
                "Pagination": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "현재 페이지"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "페이지당 항목 수"
                        },
                        "total": {
                            "type": "integer",
                            "description": "전체 항목 수"
                        },
                        "pages": {
                            "type": "integer",
                            "description": "전체 페이지 수"
                        }
                    }
                },
                "DashboardStatsResponse": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean"
                        },
                        "data": {
                            "type": "object",
                            "properties": {
                                "total_users": {
                                    "type": "integer",
                                    "description": "전체 사용자 수"
                                },
                                "total_brands": {
                                    "type": "integer",
                                    "description": "전체 브랜드 수"
                                },
                                "total_stores": {
                                    "type": "integer",
                                    "description": "전체 매장 수"
                                },
                                "active_sessions": {
                                    "type": "integer",
                                    "description": "활성 세션 수"
                                }
                            }
                        }
                    }
                },
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["healthy", "unhealthy"],
                            "description": "시스템 상태"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "확인 시간"
                        },
                        "services": {
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "enum": ["healthy", "unhealthy"]
                                },
                                "redis": {
                                    "type": "string",
                                    "enum": ["healthy", "unhealthy"]
                                }
                            }
                        }
                    }
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "object",
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "description": "에러 코드"
                                },
                                "message": {
                                    "type": "string",
                                    "description": "에러 메시지"
                                },
                                "details": {
                                    "type": "string",
                                    "description": "상세 정보"
                                },
                                "timestamp": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            }
                        }
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
                "name": "직원 관리",
                "description": "직원 계정 관리 API"
            },
            {
                "name": "관리자",
                "description": "관리자 전용 API"
            },
            {
                "name": "시스템",
                "description": "시스템 상태 및 모니터링 API"
            }
        ]
    } 