"""
Swagger API 문서화 설정
flask-smorest를 사용한 OpenAPI 3.0 스펙 생성
"""

from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields, validate

# API 스키마 정의
class UserSchema(Schema):
    """사용자 스키마"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    name = fields.Str(validate=validate.Length(max=100))
    role = fields.Str(validate=validate.OneOf(['admin', 'super_admin', 'brand_manager', 'store_manager', 'employee', 'teamlead']))
    status = fields.Str(validate=validate.OneOf(['pending', 'approved', 'rejected', 'inactive']))
    brand_id = fields.Int()
    branch_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class BrandSchema(Schema):
    """브랜드 스키마"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    industry_id = fields.Int(required=True)
    description = fields.Str(validate=validate.Length(max=500))
    website = fields.Url()
    contact_email = fields.Email()
    contact_phone = fields.Str(validate=validate.Length(max=20))
    address = fields.Str(validate=validate.Length(max=200))
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'pending']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class StoreSchema(Schema):
    """매장 스키마"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    brand_id = fields.Int(required=True)
    address = fields.Str(required=True, validate=validate.Length(max=200))
    phone = fields.Str(validate=validate.Length(max=20))
    manager_id = fields.Int()
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'pending']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class EmployeeSchema(Schema):
    """직원 스키마"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=100))
    role = fields.Str(validate=validate.OneOf(['manager', 'staff', 'kitchen', 'cashier']))
    status = fields.Str(validate=validate.OneOf(['active', 'break', 'off']))
    start_time = fields.Str()
    end_time = fields.Str()
    avatar = fields.Str()

class LoginSchema(Schema):
    """로그인 스키마"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6))

class LoginResponseSchema(Schema):
    """로그인 응답 스키마"""
    success = fields.Bool()
    message = fields.Str()
    token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(UserSchema)

class DashboardStatsSchema(Schema):
    """대시보드 통계 스키마"""
    total_users = fields.Int()
    total_brands = fields.Int()
    total_stores = fields.Int()
    total_orders = fields.Int()
    total_schedules = fields.Int()
    today_orders = fields.Int()
    today_schedules = fields.Int()
    weekly_orders = fields.Int()
    monthly_orders = fields.Int()
    total_revenue = fields.Int()
    low_stock_items = fields.Int()

class BrandStatsSchema(Schema):
    """브랜드 통계 스키마"""
    total_brands = fields.Int()
    active_brands = fields.Int()
    total_stores = fields.Int()
    total_employees = fields.Int()
    total_revenue = fields.Int()
    growth_rate = fields.Float()

class StoreStatsSchema(Schema):
    """매장 통계 스키마"""
    total_employees = fields.Int()
    active_employees = fields.Int()
    today_revenue = fields.Int()
    monthly_revenue = fields.Int()
    growth_rate = fields.Float()
    average_order_value = fields.Int()
    customer_satisfaction = fields.Float()
    pending_orders = fields.Int()
    low_stock_items = fields.Int()

class SystemStatusSchema(Schema):
    """시스템 상태 스키마"""
    status = fields.Str(validate=validate.OneOf(['online', 'offline', 'maintenance']))
    uptime = fields.Str()
    memory_usage = fields.Float()
    cpu_usage = fields.Float()
    disk_usage = fields.Float()
    active_connections = fields.Int()
    last_updated = fields.DateTime()

class SystemLogSchema(Schema):
    """시스템 로그 스키마"""
    id = fields.Int(dump_only=True)
    level = fields.Str(validate=validate.OneOf(['INFO', 'WARNING', 'ERROR', 'CRITICAL']))
    message = fields.Str()
    detail = fields.Str()
    timestamp = fields.DateTime()
    user_id = fields.Int()
    ip_address = fields.Str()

class AlertSchema(Schema):
    """알림 스키마"""
    id = fields.Int(dump_only=True)
    type = fields.Str(validate=validate.OneOf(['info', 'warning', 'error', 'critical']))
    title = fields.Str(required=True, validate=validate.Length(max=200))
    message = fields.Str(required=True, validate=validate.Length(max=1000))
    severity = fields.Str(validate=validate.OneOf(['low', 'medium', 'high', 'critical']))
    is_read = fields.Bool()
    created_at = fields.DateTime(dump_only=True)

class FeedbackSchema(Schema):
    """피드백 스키마"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    category = fields.Str(validate=validate.OneOf(['bug', 'feature', 'improvement', 'other']))
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high', 'urgent']))
    status = fields.Str(validate=validate.OneOf(['open', 'in_progress', 'resolved', 'closed']))
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class PluginSchema(Schema):
    """플러그인 스키마"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    version = fields.Str(required=True)
    description = fields.Str(validate=validate.Length(max=500))
    author = fields.Str(validate=validate.Length(max=100))
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'error']))
    is_enabled = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ModuleSchema(Schema):
    """모듈 스키마"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    version = fields.Str(required=True)
    description = fields.Str(validate=validate.Length(max=500))
    category = fields.Str(validate=validate.Length(max=50))
    is_installed = fields.Bool()
    is_enabled = fields.Bool()
    download_count = fields.Int()
    rating = fields.Float(validate=validate.Range(min=0, max=5))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class IndustrySchema(Schema):
    """업종 스키마"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=100))
    type = fields.Str(validate=validate.Length(max=50))
    brands_count = fields.Int()
    stores_count = fields.Int()
    employees_count = fields.Int()
    revenue = fields.Int()
    status = fields.Str(validate=validate.OneOf(['active', 'inactive']))
    last_updated = fields.DateTime()

# API 응답 스키마
class SuccessResponseSchema(Schema):
    """성공 응답 스키마"""
    success = fields.Bool(required=True)
    message = fields.Str()
    data = fields.Raw()

class ErrorResponseSchema(Schema):
    """에러 응답 스키마"""
    success = fields.Bool(required=True)
    error = fields.Str(required=True)
    code = fields.Str()
    details = fields.Raw()

# 페이지네이션 스키마
class PaginationSchema(Schema):
    """페이지네이션 스키마"""
    page = fields.Int(validate=validate.Range(min=1))
    per_page = fields.Int(validate=validate.Range(min=1, max=100))
    total = fields.Int()
    pages = fields.Int()
    has_next = fields.Bool()
    has_prev = fields.Bool()

# Swagger 설정
def create_swagger_config(app):
    """Swagger API 설정을 생성합니다."""

    # 이미 등록된 경우 중복 등록 방지
    if 'api-docs' in app.blueprints:
        return None
    # 기존 api-docs 관련 엔드포인트 제거 (혹시 남아있을 경우)
    for rule in list(app.url_map.iter_rules()):
        if rule.endpoint.startswith('api-docs.'):
            app.url_map._rules.remove(rule)
            app.view_functions.pop(rule.endpoint, None)

    app.config["API_TITLE"] = "Your Program API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["OPENAPI_REDOC_PATH"] = "/redoc"
    app.config["OPENAPI_REDOC_URL"] = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"

    api = Api(app, spec_kwargs={"title": "Your Program API", "version": "v1"})

    # 스키마 등록
    api.spec.components.schema("User", schema=UserSchema)
    api.spec.components.schema("Brand", schema=BrandSchema)
    api.spec.components.schema("Store", schema=StoreSchema)
    api.spec.components.schema("Employee", schema=EmployeeSchema)
    api.spec.components.schema("Login", schema=LoginSchema)
    api.spec.components.schema("LoginResponse", schema=LoginResponseSchema)
    api.spec.components.schema("DashboardStats", schema=DashboardStatsSchema)
    api.spec.components.schema("BrandStats", schema=BrandStatsSchema)
    api.spec.components.schema("StoreStats", schema=StoreStatsSchema)
    api.spec.components.schema("SystemStatus", schema=SystemStatusSchema)
    api.spec.components.schema("SystemLog", schema=SystemLogSchema)
    api.spec.components.schema("Alert", schema=AlertSchema)
    api.spec.components.schema("Feedback", schema=FeedbackSchema)
    api.spec.components.schema("Plugin", schema=PluginSchema)
    api.spec.components.schema("Module", schema=ModuleSchema)
    api.spec.components.schema("Industry", schema=IndustrySchema)
    api.spec.components.schema("SuccessResponse", schema=SuccessResponseSchema)
    api.spec.components.schema("ErrorResponse", schema=ErrorResponseSchema)
    api.spec.components.schema("Pagination", schema=PaginationSchema)

    return api

# 태그 정의
TAGS = {
    "auth": {
        "name": "인증",
        "description": "사용자 인증 및 권한 관리"
    },
    "admin": {
        "name": "관리자",
        "description": "시스템 관리자 기능"
    },
    "brands": {
        "name": "브랜드",
        "description": "브랜드 관리"
    },
    "stores": {
        "name": "매장",
        "description": "매장 관리"
    },
    "employees": {
        "name": "직원",
        "description": "직원 관리"
    },
    "users": {
        "name": "사용자",
        "description": "사용자 관리"
    },
    "plugins": {
        "name": "플러그인",
        "description": "플러그인 관리"
    },
    "modules": {
        "name": "모듈",
        "description": "모듈 마켓플레이스"
    },
    "feedback": {
        "name": "피드백",
        "description": "피드백 시스템"
    },
    "system": {
        "name": "시스템",
        "description": "시스템 모니터링 및 상태"
    },
    "dashboard": {
        "name": "대시보드",
        "description": "대시보드 및 통계"
    },
    "industries": {
        "name": "업종",
        "description": "업종 관리"
    }
} 