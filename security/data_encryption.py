"""
데이터 암호화 시스템
전송 중/저장 시 데이터 암호화를 위한 고급 보안 시스템
"""
import os
import base64
import hashlib
import hmac
import secrets
import logging
from typing import Dict, Any, Optional, Union, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json
import pickle
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataEncryption:
    """데이터 암호화 시스템 클래스"""
    
    def __init__(self):
        """초기화"""
        # 마스터 키 생성 또는 로드
        self.master_key = self._load_or_generate_master_key()
        
        # 대칭키 암호화 (Fernet)
        self.fernet = Fernet(self.master_key)
        
        # 비대칭키 암호화 (RSA)
        self.rsa_private_key = self._load_or_generate_rsa_keys()
        self.rsa_public_key = self.rsa_private_key.public_key()
        
        # 키 관리
        self.key_rotation_interval = 30  # 30일
        self.last_key_rotation = self._load_last_rotation_date()
        
        # 암호화된 데이터 저장소
        self.encrypted_data_store = {}
        
        logger.info("데이터 암호화 시스템 초기화 완료")
    
    def _load_or_generate_master_key(self) -> bytes:
        """마스터 키 로드 또는 생성"""
        try:
            key_file = "security/master_key.key"
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # 새 마스터 키 생성
                key = Fernet.generate_key()
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(key)
                logger.info("새 마스터 키 생성 완료")
                return key
        except Exception as e:
            logger.error(f"마스터 키 로드/생성 오류: {str(e)}")
            # 임시 키 생성
            return Fernet.generate_key()
    
    def _load_or_generate_rsa_keys(self) -> rsa.RSAPrivateKey:
        """RSA 키 로드 또는 생성"""
        try:
            private_key_file = "security/private_key.pem"
            if os.path.exists(private_key_file):
                with open(private_key_file, 'rb') as f:
                    return serialization.load_pem_private_key(
                        f.read(),
                        password=None,
                        backend=default_backend()
                    )
            else:
                # 새 RSA 키 생성
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend()
                )
                
                # 개인키 저장
                os.makedirs(os.path.dirname(private_key_file), exist_ok=True)
                with open(private_key_file, 'wb') as f:
                    f.write(private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                
                # 공개키 저장
                public_key_file = "security/public_key.pem"
                with open(public_key_file, 'wb') as f:
                    f.write(private_key.public_key().public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
                
                logger.info("새 RSA 키 생성 완료")
                return private_key
        except Exception as e:
            logger.error(f"RSA 키 로드/생성 오류: {str(e)}")
            # 임시 키 생성
            return rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
    
    def _load_last_rotation_date(self) -> datetime:
        """마지막 키 회전 날짜 로드"""
        try:
            rotation_file = "security/last_rotation.txt"
            if os.path.exists(rotation_file):
                with open(rotation_file, 'r') as f:
                    date_str = f.read().strip()
                    return datetime.fromisoformat(date_str)
            return datetime.now()
        except Exception as e:
            logger.error(f"회전 날짜 로드 오류: {str(e)}")
            return datetime.now()
    
    def _save_rotation_date(self):
        """회전 날짜 저장"""
        try:
            rotation_file = "security/last_rotation.txt"
            os.makedirs(os.path.dirname(rotation_file), exist_ok=True)
            with open(rotation_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            logger.error(f"회전 날짜 저장 오류: {str(e)}")
    
    def encrypt_symmetric(self, data: Union[str, bytes, dict]) -> Dict[str, Any]:
        """대칭키 암호화 (Fernet)"""
        try:
            # 데이터를 바이트로 변환
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, dict):
                data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
            else:
                data_bytes = data
            
            # 암호화
            encrypted_data = self.fernet.encrypt(data_bytes)
            
            # 메타데이터 추가
            result = {
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
                'algorithm': 'fernet',
                'timestamp': datetime.now().isoformat(),
                'data_type': type(data).__name__
            }
            
            return result
        except Exception as e:
            logger.error(f"대칭키 암호화 오류: {str(e)}")
            raise
    
    def decrypt_symmetric(self, encrypted_data: Dict[str, Any]) -> Union[str, bytes, dict]:
        """대칭키 복호화 (Fernet)"""
        try:
            # 암호화된 데이터 디코딩
            encrypted_bytes = base64.b64decode(encrypted_data['encrypted_data'])
            
            # 복호화
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # 원본 데이터 타입으로 복원
            data_type = encrypted_data.get('data_type', 'str')
            if data_type == 'dict':
                return json.loads(decrypted_bytes.decode('utf-8'))
            elif data_type == 'str':
                return decrypted_bytes.decode('utf-8')
            else:
                return decrypted_bytes
        except Exception as e:
            logger.error(f"대칭키 복호화 오류: {str(e)}")
            raise
    
    def encrypt_asymmetric(self, data: Union[str, bytes]) -> Dict[str, Any]:
        """비대칭키 암호화 (RSA)"""
        try:
            # 데이터를 바이트로 변환
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # RSA 암호화 (작은 데이터용)
            encrypted_data = self.rsa_public_key.encrypt(
                data_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            result = {
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
                'algorithm': 'rsa',
                'timestamp': datetime.now().isoformat(),
                'data_type': type(data).__name__
            }
            
            return result
        except Exception as e:
            logger.error(f"비대칭키 암호화 오류: {str(e)}")
            raise
    
    def decrypt_asymmetric(self, encrypted_data: Dict[str, Any]) -> Union[str, bytes]:
        """비대칭키 복호화 (RSA)"""
        try:
            # 암호화된 데이터 디코딩
            encrypted_bytes = base64.b64decode(encrypted_data['encrypted_data'])
            
            # RSA 복호화
            decrypted_bytes = self.rsa_private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # 원본 데이터 타입으로 복원
            data_type = encrypted_data.get('data_type', 'str')
            if data_type == 'str':
                return decrypted_bytes.decode('utf-8')
            else:
                return decrypted_bytes
        except Exception as e:
            logger.error(f"비대칭키 복호화 오류: {str(e)}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """파일 암호화"""
        try:
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            # 파일 읽기
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # 암호화
            encrypted_data = self.encrypt_symmetric(file_data)
            
            # 암호화된 파일 저장
            with open(output_path, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            logger.info(f"파일 암호화 완료: {file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"파일 암호화 오류: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """파일 복호화"""
        try:
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '.decrypted')
            
            # 암호화된 파일 읽기
            with open(encrypted_file_path, 'r') as f:
                encrypted_data = json.load(f)
            
            # 복호화
            decrypted_data = self.decrypt_symmetric(encrypted_data)
            
            # 복호화된 파일 저장
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"파일 복호화 완료: {encrypted_file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"파일 복호화 오류: {str(e)}")
            raise
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """비밀번호 해싱 (PBKDF2)"""
        try:
            if salt is None:
                salt = secrets.token_hex(16)
            
            # PBKDF2 해싱
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000  # 반복 횟수
            )
            
            return base64.b64encode(key).decode('utf-8'), salt
        except Exception as e:
            logger.error(f"비밀번호 해싱 오류: {str(e)}")
            raise
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """비밀번호 검증"""
        try:
            new_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(hashed_password, new_hash)
        except Exception as e:
            logger.error(f"비밀번호 검증 오류: {str(e)}")
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """보안 토큰 생성"""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            logger.error(f"토큰 생성 오류: {str(e)}")
            raise
    
    def encrypt_database_field(self, field_value: str) -> str:
        """데이터베이스 필드 암호화"""
        try:
            encrypted_data = self.encrypt_symmetric(field_value)
            return json.dumps(encrypted_data)
        except Exception as e:
            logger.error(f"데이터베이스 필드 암호화 오류: {str(e)}")
            raise
    
    def decrypt_database_field(self, encrypted_field: str) -> str:
        """데이터베이스 필드 복호화"""
        try:
            encrypted_data = json.loads(encrypted_field)
            return self.decrypt_symmetric(encrypted_data)
        except Exception as e:
            logger.error(f"데이터베이스 필드 복호화 오류: {str(e)}")
            raise
    
    def encrypt_api_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """API 페이로드 암호화"""
        try:
            # 민감한 필드만 암호화
            sensitive_fields = ['password', 'token', 'secret', 'key', 'credit_card']
            encrypted_payload = payload.copy()
            
            for field in sensitive_fields:
                if field in encrypted_payload:
                    encrypted_payload[field] = self.encrypt_database_field(str(encrypted_payload[field]))
            
            return encrypted_payload
        except Exception as e:
            logger.error(f"API 페이로드 암호화 오류: {str(e)}")
            raise
    
    def decrypt_api_payload(self, encrypted_payload: Dict[str, Any]) -> Dict[str, Any]:
        """API 페이로드 복호화"""
        try:
            # 민감한 필드만 복호화
            sensitive_fields = ['password', 'token', 'secret', 'key', 'credit_card']
            decrypted_payload = encrypted_payload.copy()
            
            for field in sensitive_fields:
                if field in decrypted_payload:
                    decrypted_payload[field] = self.decrypt_database_field(decrypted_payload[field])
            
            return decrypted_payload
        except Exception as e:
            logger.error(f"API 페이로드 복호화 오류: {str(e)}")
            raise
    
    def rotate_keys(self):
        """키 회전"""
        try:
            # 키 회전 필요 여부 확인
            if datetime.now() - self.last_key_rotation < timedelta(days=self.key_rotation_interval):
                return False
            
            logger.info("키 회전 시작")
            
            # 새 마스터 키 생성
            new_master_key = Fernet.generate_key()
            new_fernet = Fernet(new_master_key)
            
            # 기존 암호화된 데이터 재암호화
            for key, encrypted_data in self.encrypted_data_store.items():
                try:
                    # 기존 키로 복호화
                    decrypted_data = self.decrypt_symmetric(encrypted_data)
                    
                    # 새 키로 재암호화
                    new_encrypted_data = new_fernet.encrypt(decrypted_data)
                    self.encrypted_data_store[key] = {
                        'encrypted_data': base64.b64encode(new_encrypted_data).decode('utf-8'),
                        'algorithm': 'fernet',
                        'timestamp': datetime.now().isoformat(),
                        'data_type': encrypted_data.get('data_type', 'str')
                    }
                except Exception as e:
                    logger.error(f"키 회전 중 데이터 재암호화 오류: {str(e)}")
            
            # 새 키로 업데이트
            self.master_key = new_master_key
            self.fernet = new_fernet
            
            # 마스터 키 파일 업데이트
            key_file = "security/master_key.key"
            with open(key_file, 'wb') as f:
                f.write(new_master_key)
            
            # 회전 날짜 업데이트
            self.last_key_rotation = datetime.now()
            self._save_rotation_date()
            
            logger.info("키 회전 완료")
            return True
        except Exception as e:
            logger.error(f"키 회전 오류: {str(e)}")
            return False
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """암호화 시스템 상태 조회"""
        try:
            return {
                'master_key_exists': bool(self.master_key),
                'rsa_keys_exist': bool(self.rsa_private_key),
                'last_key_rotation': self.last_key_rotation.isoformat(),
                'days_since_rotation': (datetime.now() - self.last_key_rotation).days,
                'key_rotation_interval': self.key_rotation_interval,
                'encrypted_data_count': len(self.encrypted_data_store)
            }
        except Exception as e:
            logger.error(f"암호화 상태 조회 오류: {str(e)}")
            return {}

# 전역 인스턴스
encryption_system = DataEncryption()

if __name__ == '__main__':
    # 테스트 코드
    print("데이터 암호화 시스템 테스트")
    
    # 대칭키 암호화 테스트
    test_data = "Hello, World!"
    encrypted = encryption_system.encrypt_symmetric(test_data)
    decrypted = encryption_system.decrypt_symmetric(encrypted)
    print(f"대칭키 암호화: {test_data} -> {decrypted}")
    
    # 비대칭키 암호화 테스트
    encrypted_rsa = encryption_system.encrypt_asymmetric(test_data)
    decrypted_rsa = encryption_system.decrypt_asymmetric(encrypted_rsa)
    print(f"비대칭키 암호화: {test_data} -> {decrypted_rsa}")
    
    # 비밀번호 해싱 테스트
    password = "my_password"
    hashed, salt = encryption_system.hash_password(password)
    verified = encryption_system.verify_password(password, hashed, salt)
    print(f"비밀번호 해싱: {password} -> {verified}")
    
    # 토큰 생성 테스트
    token = encryption_system.generate_secure_token()
    print(f"보안 토큰: {token}")
    
    print("데이터 암호화 시스템 테스트 완료") 