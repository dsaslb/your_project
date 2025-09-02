"""
📤 프리사인드 업로드 API

증빙 사진, 문서 등의 대용량 파일을 S3/GCS에 직접 업로드하기 위한 프리사인드 URL 생성
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime, timedelta
import uuid
from utils.auth_decorators import auth_required

# 업로드 API 블루프린트
uploads_bp = Blueprint("uploads_api", __name__, url_prefix="/api/uploads")

# S3 설정
S3_BUCKET = os.getenv("S3_BUCKET", "your-bucket-name")
S3_REGION = os.getenv("S3_REGION", "ap-northeast-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# S3 클라이언트 초기화
s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=S3_REGION
    )

def validate_tenant_scope(required_scope=None):
    """테넌트 스코프 검증 데코레이터"""
    def decorator(f):
        @wraps(f)
        def wrap(*a, **kw):
            if required_scope == "branch" and not request.branch_id:
                return jsonify({"error": "branch_id required"}), 400
            if required_scope == "brand" and not request.brand_id:
                return jsonify({"error": "brand_id required"}), 400
            if required_scope == "industry" and not request.industry_id:
                return jsonify({"error": "industry_id required"}), 400
            return f(*a, **kw)
        return wrap
    return decorator

@uploads_bp.post("/presign")
@auth_required
@validate_tenant_scope("branch")
def presign():
    """프리사인드 업로드 URL 생성"""
    d = request.get_json() or {}
    
    if not s3_client:
        return jsonify({"error": "S3 not configured"}), 500
    
    # 파일 정보
    file_type = d.get("file_type", "image/jpeg")
    file_extension = d.get("file_extension", "jpg")
    max_size_mb = d.get("max_size_mb", 10)
    
    # 파일 키 생성 (테넌트 스코프 포함)
    file_key = f"proof/{request.industry_id}/{request.brand_id}/{request.branch_id}/{request.user_id}/{uuid.uuid4()}.{file_extension}"
    
    try:
        # 프리사인드 URL 생성
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': file_key,
                'ContentType': file_type,
                'Metadata': {
                    'user_id': str(request.user_id),
                    'branch_id': str(request.branch_id),
                    'brand_id': str(request.brand_id),
                    'industry_id': str(request.industry_id),
                    'uploaded_at': datetime.now().isoformat()
                }
            },
            ExpiresIn=3600,  # 1시간 유효
            HttpMethod='PUT'
        )
        
        # 공개 URL (업로드 완료 후 접근용)
        public_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_key}"
        
        return jsonify({
            "upload_url": presigned_url,
            "public_url": public_url,
            "file_key": file_key,
            "expires_in": 3600,
            "max_size_mb": max_size_mb,
            "content_type": file_type
        })
        
    except ClientError as e:
        print(f"S3 프리사인드 URL 생성 실패: {e}")
        return jsonify({"error": "presigned url generation failed"}), 500

@uploads_bp.post("/presign_multiple")
@auth_required
@validate_tenant_scope("branch")
def presign_multiple():
    """여러 파일을 위한 프리사인드 URL 일괄 생성"""
    d = request.get_json() or {}
    files = d.get("files", [])
    
    if not files or len(files) > 10:  # 최대 10개 파일
        return jsonify({"error": "invalid files array"}), 400
    
    if not s3_client:
        return jsonify({"error": "S3 not configured"}), 500
    
    presigned_urls = []
    
    for file_info in files:
        file_type = file_info.get("file_type", "image/jpeg")
        file_extension = file_info.get("file_extension", "jpg")
        
        # 파일 키 생성
        file_key = f"proof/{request.industry_id}/{request.brand_id}/{request.branch_id}/{request.user_id}/{uuid.uuid4()}.{file_extension}"
        
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': file_key,
                    'ContentType': file_type,
                    'Metadata': {
                        'user_id': str(request.user_id),
                        'branch_id': str(request.branch_id),
                        'brand_id': str(request.brand_id),
                        'industry_id': str(request.industry_id),
                        'uploaded_at': datetime.now().isoformat()
                    }
                },
                ExpiresIn=3600,
                HttpMethod='PUT'
            )
            
            public_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_key}"
            
            presigned_urls.append({
                "file_key": file_key,
                "upload_url": presigned_url,
                "public_url": public_url,
                "content_type": file_type,
                "expires_in": 3600
            })
            
        except ClientError as e:
            print(f"파일 {file_key} 프리사인드 URL 생성 실패: {e}")
            continue
    
    return jsonify({
        "urls": presigned_urls,
        "total": len(presigned_urls),
        "failed": len(files) - len(presigned_urls)
    })

@uploads_bp.delete("/file")
@auth_required
@validate_tenant_scope("branch")
def delete_file():
    """업로드된 파일 삭제"""
    d = request.get_json() or {}
    file_key = d.get("file_key")
    
    if not file_key:
        return jsonify({"error": "file_key required"}), 400
    
    if not s3_client:
        return jsonify({"error": "S3 not configured"}), 500
    
    try:
        # 파일 소유권 검증 (테넌트 스코프)
        if not file_key.startswith(f"proof/{request.industry_id}/{request.brand_id}/{request.branch_id}/{request.user_id}/"):
            return jsonify({"error": "unauthorized file access"}), 403
        
        # S3에서 파일 삭제
        s3_client.delete_object(Bucket=S3_BUCKET, Key=file_key)
        
        return jsonify({"ok": True, "deleted": file_key})
        
    except ClientError as e:
        print(f"파일 삭제 실패: {e}")
        return jsonify({"error": "file deletion failed"}), 500

@uploads_bp.get("/files")
@auth_required
@validate_tenant_scope("branch")
def list_files():
    """사용자의 업로드된 파일 목록 조회"""
    try:
        # S3에서 사용자 파일 목록 조회
        prefix = f"proof/{request.industry_id}/{request.brand_id}/{request.branch_id}/{request.user_id}/"
        
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=prefix,
            MaxKeys=100
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "url": f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{obj['Key']}"
                })
        
        return jsonify({
            "files": files,
            "total": len(files),
            "prefix": prefix
        })
        
    except ClientError as e:
        print(f"파일 목록 조회 실패: {e}")
        return jsonify({"error": "file listing failed"}), 500

@uploads_bp.post("/verify_upload")
@auth_required
@validate_tenant_scope("branch")
def verify_upload():
    """파일 업로드 완료 확인 및 메타데이터 저장"""
    d = request.get_json() or {}
    file_key = d.get("file_key")
    file_size = d.get("file_size")
    
    if not file_key or not file_size:
        return jsonify({"error": "file_key and file_size required"}), 400
    
    try:
        # S3에서 파일 존재 확인
        response = s3_client.head_object(Bucket=S3_BUCKET, Key=file_key)
        
        # 파일 크기 검증
        if response['ContentLength'] != file_size:
            return jsonify({"error": "file size mismatch"}), 400
        
        # 메타데이터 반환
        metadata = response.get('Metadata', {})
        
        return jsonify({
            "ok": True,
            "file_key": file_key,
            "file_size": response['ContentLength'],
            "content_type": response.get('ContentType'),
            "metadata": metadata,
            "url": f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_key}"
        })
        
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return jsonify({"error": "file not found"}), 404
        else:
            print(f"파일 검증 실패: {e}")
            return jsonify({"error": "file verification failed"}), 500
