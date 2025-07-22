"""
Swagger/OpenAPI 자동 문서화 및 Swagger UI 엔드포인트
"""
from flask import Blueprint
from flasgger import Swagger

bp = Blueprint('swagger_docs', __name__)

def register_swagger(app):
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Your Program API",
            "description": "API 명세 및 테스트 UI (Swagger)",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http", "https"],
    }) 