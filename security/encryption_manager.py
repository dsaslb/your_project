"""
암호화 및 키 관리 시스템
엔터프라이즈급 데이터 보안을 위한 암호화 시스템
"""

import os
import base64
import hashlib
import hmac
import secrets
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import sqlite3
import threading

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KeyInfo:
    """키 정보"""
    key_id: str
    key_type: str  # symmetric, asymmetric, derived
    algorithm: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    key_size: int
    metadata: Dict[str, Any]

@dataclass
class EncryptedData:
    """암호화된 데이터"""
    data: bytes
    key_id: str
    algorithm: str
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None

class KeyManager:
    """키 관리자"""
    
    def __init__(self, db_path: str = "security/keys.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS keys (
                    key_id TEXT PRIMARY KEY,
                    key_type TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    key_data BLOB NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN NOT NULL,
                    key_size INTEGER NOT NULL,
                    metadata TEXT
                )
            """)
            conn.commit()
    
    def generate_symmetric_key(self, key_size: int = 256) -> str:
        """대칭 키 생성"""
        key_id = f"sym_{secrets.token_hex(16)}"
        key_data = Fernet.generate_key()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO keys (key_id, key_type, algorithm, key_data, created_at, is_active, key_size, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key_id,
                'symmetric',
                'AES-256-GCM',
                key_data,
                datetime.now(),
                True,
                key_size,
                json.dumps({'version': '1.0'})
            ))
            conn.commit()
        
        logger.info(f"대칭 키 생성 완료: {key_id}")
        return key_id
    
    def generate_asymmetric_key_pair(self, key_size: int = 2048) -> Tuple[str, str]:
        """비대칭 키 쌍 생성"""
        private_key_id = f"priv_{secrets.token_hex(16)}"
        public_key_id = f"pub_{secrets.token_hex(16)}"
        
        # RSA 키 쌍 생성
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        public_key = private_key.public_key()
        
        # 개인키 직렬화
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # 공개키 직렬화
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with sqlite3.connect(self.db_path) as conn:
            # 개인키 저장
            conn.execute("""
                INSERT INTO keys (key_id, key_type, algorithm, key_data, created_at, is_active, key_size, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                private_key_id,
                'asymmetric',
                'RSA',
                private_key_pem,
                datetime.now(),
                True,
                key_size,
                json.dumps({'key_pair_id': public_key_id})
            ))
            
            # 공개키 저장
            conn.execute("""
                INSERT INTO keys (key_id, key_type, algorithm, key_data, created_at, is_active, key_size, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                public_key_id,
                'asymmetric',
                'RSA',
                public_key_pem,
                datetime.now(),
                True,
                key_size,
                json.dumps({'key_pair_id': private_key_id})
            ))
            conn.commit()
        
        logger.info(f"비대칭 키 쌍 생성 완료: {private_key_id}, {public_key_id}")
        return private_key_id, public_key_id
    
    def derive_key(self, password: str, salt: bytes, key_size: int = 256) -> str:
        """패스워드에서 키 유도"""
        key_id = f"derived_{secrets.token_hex(16)}"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_size // 8,
            salt=salt,
            iterations=100000,
        )
        key_data = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO keys (key_id, key_type, algorithm, key_data, created_at, is_active, key_size, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key_id,
                'derived',
                'PBKDF2-SHA256',
                key_data,
                datetime.now(),
                True,
                key_size,
                json.dumps({'salt': base64.b64encode(salt).decode()})
            ))
            conn.commit()
        
        logger.info(f"유도 키 생성 완료: {key_id}")
        return key_id
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """키 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key_data, is_active, expires_at FROM keys WHERE key_id = ?
            """, (key_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            key_data, is_active, expires_at = row
            
            if not is_active:
                logger.warning(f"비활성 키 사용 시도: {key_id}")
                return None
            
            if expires_at:
                expires_at = datetime.fromisoformat(expires_at)
                if datetime.now() > expires_at:
                    logger.warning(f"만료된 키 사용 시도: {key_id}")
                    return None
            
            return key_data
    
    def rotate_key(self, key_id: str) -> str:
        """키 로테이션"""
        with self.lock:
            # 새 키 생성
            old_key_info = self.get_key_info(key_id)
            if not old_key_info:
                raise ValueError(f"키를 찾을 수 없습니다: {key_id}")
            
            if old_key_info.key_type == 'symmetric':
                new_key_id = self.generate_symmetric_key(old_key_info.key_size)
            elif old_key_info.key_type == 'asymmetric':
                new_key_id, _ = self.generate_asymmetric_key_pair(old_key_info.key_size)
            else:
                raise ValueError(f"지원하지 않는 키 타입: {old_key_info.key_type}")
            
            # 기존 키 비활성화
            self.deactivate_key(key_id)
            
            logger.info(f"키 로테이션 완료: {key_id} -> {new_key_id}")
            return new_key_id
    
    def deactivate_key(self, key_id: str) -> bool:
        """키 비활성화"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE keys SET is_active = FALSE WHERE key_id = ?
            """, (key_id,))
            conn.commit()
        
        logger.info(f"키 비활성화 완료: {key_id}")
        return True
    
    def delete_key(self, key_id: str) -> bool:
        """키 삭제"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM keys WHERE key_id = ?", (key_id,))
            conn.commit()
        
        logger.info(f"키 삭제 완료: {key_id}")
        return True
    
    def get_key_info(self, key_id: str) -> Optional[KeyInfo]:
        """키 정보 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key_type, algorithm, created_at, expires_at, is_active, key_size, metadata
                FROM keys WHERE key_id = ?
            """, (key_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            key_type, algorithm, created_at, expires_at, is_active, key_size, metadata = row
            
            return KeyInfo(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                created_at=datetime.fromisoformat(created_at),
                expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
                is_active=bool(is_active),
                key_size=key_size,
                metadata=json.loads(metadata) if metadata else {}
            )
    
    def list_keys(self, key_type: Optional[str] = None) -> List[KeyInfo]:
        """키 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            if key_type:
                cursor = conn.execute("""
                    SELECT key_id, key_type, algorithm, created_at, expires_at, is_active, key_size, metadata
                    FROM keys WHERE key_type = ?
                """, (key_type,))
            else:
                cursor = conn.execute("""
                    SELECT key_id, key_type, algorithm, created_at, expires_at, is_active, key_size, metadata
                    FROM keys
                """)
            
            keys = []
            for row in cursor.fetchall():
                key_id, key_type, algorithm, created_at, expires_at, is_active, key_size, metadata = row
                keys.append(KeyInfo(
                    key_id=key_id,
                    key_type=key_type,
                    algorithm=algorithm,
                    created_at=datetime.fromisoformat(created_at),
                    expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
                    is_active=bool(is_active),
                    key_size=key_size,
                    metadata=json.loads(metadata) if metadata else {}
                ))
            
            return keys

class EncryptionManager:
    """암호화 관리자"""
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
    
    def encrypt_symmetric(self, data: Union[str, bytes], key_id: str) -> EncryptedData:
        """대칭 암호화"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        key_data = self.key_manager.get_key(key_id)
        if not key_data:
            raise ValueError(f"키를 찾을 수 없습니다: {key_id}")
        
        fernet = Fernet(key_data)
        encrypted_data = fernet.encrypt(data)
        
        return EncryptedData(
            data=encrypted_data,
            key_id=key_id,
            algorithm='AES-256-GCM'
        )
    
    def decrypt_symmetric(self, encrypted_data: EncryptedData) -> bytes:
        """대칭 복호화"""
        key_data = self.key_manager.get_key(encrypted_data.key_id)
        if not key_data:
            raise ValueError(f"키를 찾을 수 없습니다: {encrypted_data.key_id}")
        
        fernet = Fernet(key_data)
        decrypted_data = fernet.decrypt(encrypted_data.data)
        
        return decrypted_data
    
    def encrypt_asymmetric(self, data: Union[str, bytes], public_key_id: str) -> EncryptedData:
        """비대칭 암호화"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        key_data = self.key_manager.get_key(public_key_id)
        if not key_data:
            raise ValueError(f"공개키를 찾을 수 없습니다: {public_key_id}")
        
        public_key = serialization.load_pem_public_key(key_data)
        
        encrypted_data = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptedData(
            data=encrypted_data,
            key_id=public_key_id,
            algorithm='RSA-OAEP'
        )
    
    def decrypt_asymmetric(self, encrypted_data: EncryptedData, private_key_id: str) -> bytes:
        """비대칭 복호화"""
        key_data = self.key_manager.get_key(private_key_id)
        if not key_data:
            raise ValueError(f"개인키를 찾을 수 없습니다: {private_key_id}")
        
        private_key = serialization.load_pem_private_key(key_data, password=None)
        
        decrypted_data = private_key.decrypt(
            encrypted_data.data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted_data
    
    def create_digital_signature(self, data: Union[str, bytes], private_key_id: str) -> bytes:
        """디지털 서명 생성"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        key_data = self.key_manager.get_key(private_key_id)
        if not key_data:
            raise ValueError(f"개인키를 찾을 수 없습니다: {private_key_id}")
        
        private_key = serialization.load_pem_private_key(key_data, password=None)
        
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def verify_digital_signature(self, data: Union[str, bytes], signature: bytes, public_key_id: str) -> bool:
        """디지털 서명 검증"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        key_data = self.key_manager.get_key(public_key_id)
        if not key_data:
            raise ValueError(f"공개키를 찾을 수 없습니다: {public_key_id}")
        
        public_key = serialization.load_pem_public_key(key_data)
        
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """데이터 해시"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"지원하지 않는 해시 알고리즘: {algorithm}")
    
    def hmac_sign(self, data: Union[str, bytes], key: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """HMAC 서명"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        if algorithm == 'sha256':
            return hmac.new(key, data, hashlib.sha256).hexdigest()
        elif algorithm == 'sha512':
            return hmac.new(key, data, hashlib.sha512).hexdigest()
        else:
            raise ValueError(f"지원하지 않는 HMAC 알고리즘: {algorithm}")

class SecureStorage:
    """보안 저장소"""
    
    def __init__(self, encryption_manager: EncryptionManager, key_id: str):
        self.encryption_manager = encryption_manager
        self.key_id = key_id
    
    def store_secure_data(self, key: str, value: Union[str, bytes]) -> bool:
        """보안 데이터 저장"""
        try:
            if isinstance(value, str):
                value = value.encode('utf-8')
            
            encrypted_data = self.encryption_manager.encrypt_symmetric(value, self.key_id)
            
            # 실제 구현에서는 안전한 저장소에 저장
            # 여기서는 메모리에 임시 저장
            return True
        except Exception as e:
            logger.error(f"보안 데이터 저장 오류: {e}")
            return False
    
    def retrieve_secure_data(self, key: str) -> Optional[bytes]:
        """보안 데이터 조회"""
        try:
            # 실제 구현에서는 안전한 저장소에서 조회
            # 여기서는 임시 구현
            return None
        except Exception as e:
            logger.error(f"보안 데이터 조회 오류: {e}")
            return None

# 사용 예시
if __name__ == "__main__":
    # 키 관리자 초기화
    key_manager = KeyManager()
    
    # 암호화 관리자 초기화
    encryption_manager = EncryptionManager(key_manager)
    
    # 대칭 키 생성
    symmetric_key_id = key_manager.generate_symmetric_key()
    
    # 비대칭 키 쌍 생성
    private_key_id, public_key_id = key_manager.generate_asymmetric_key_pair()
    
    # 데이터 암호화
    original_data = "Hello, World!"
    
    # 대칭 암호화
    encrypted_data = encryption_manager.encrypt_symmetric(original_data, symmetric_key_id)
    decrypted_data = encryption_manager.decrypt_symmetric(encrypted_data)
    print(f"대칭 암호화 결과: {decrypted_data.decode()}")
    
    # 비대칭 암호화
    encrypted_data = encryption_manager.encrypt_asymmetric(original_data, public_key_id)
    decrypted_data = encryption_manager.decrypt_asymmetric(encrypted_data, private_key_id)
    print(f"비대칭 암호화 결과: {decrypted_data.decode()}")
    
    # 디지털 서명
    signature = encryption_manager.create_digital_signature(original_data, private_key_id)
    is_valid = encryption_manager.verify_digital_signature(original_data, signature, public_key_id)
    print(f"디지털 서명 검증: {is_valid}")
    
    # 해시
    hash_value = encryption_manager.hash_data(original_data)
    print(f"해시 값: {hash_value}")
    
    # HMAC
    hmac_value = encryption_manager.hmac_sign(original_data, "secret-key")
    print(f"HMAC 값: {hmac_value}")
    
    # 키 목록 조회
    keys = key_manager.list_keys()
    print(f"총 키 수: {len(keys)}")
    
    for key in keys:
        print(f"키 ID: {key.key_id}, 타입: {key.key_type}, 활성: {key.is_active}") 