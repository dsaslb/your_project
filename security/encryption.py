"""
데이터 암호화 및 보안 정책 시스템
"""

import base64
import hashlib
import hmac
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets
import time

logger = logging.getLogger(__name__)

class EncryptionType(Enum):
    """암호화 타입"""
    SYMMETRIC = "symmetric"      # 대칭키 암호화
    ASYMMETRIC = "asymmetric"    # 비대칭키 암호화
    HASH = "hash"               # 해시
    HMAC = "hmac"               # HMAC

class DataSensitivity(Enum):
    """데이터 민감도"""
    PUBLIC = "public"           # 공개 데이터
    INTERNAL = "internal"       # 내부 데이터
    CONFIDENTIAL = "confidential"  # 기밀 데이터
    RESTRICTED = "restricted"   # 제한 데이터

@dataclass
class EncryptionKey:
    """암호화 키"""
    key_id: str
    key_type: str
    key_data: bytes
    created_at: str
    expires_at: Optional[str]
    is_active: bool
    metadata: Dict[str, Any]

@dataclass
class EncryptedData:
    """암호화된 데이터"""
    data: bytes
    key_id: str
    algorithm: str
    iv: Optional[bytes]
    tag: Optional[bytes]
    metadata: Dict[str, Any]

class DataEncryption:
    """데이터 암호화 시스템"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'master_key': None,  # 마스터 키 (환경변수에서 로드)
            'key_rotation_days': 90,
            'encryption_algorithm': 'AES-256-GCM',
            'hash_algorithm': 'SHA-256',
            'key_storage_path': 'security/keys/',
            'backup_keys': True
        }
        
        # 마스터 키 로드
        self.master_key = self._load_master_key()
        
        # 키 관리
        self.keys = {}
        self._load_keys()
        
        # 암호화 엔진 초기화
        self._init_encryption_engines()
        
        # 보안 정책
        self.security_policies = self._init_security_policies()
    
    def _load_master_key(self) -> bytes:
        """마스터 키 로드"""
        # 환경변수에서 마스터 키 로드
        master_key = os.getenv('MASTER_ENCRYPTION_KEY')
        if master_key:
            return base64.urlsafe_b64decode(master_key)
        
        # 파일에서 마스터 키 로드
        master_key_file = 'security/master.key'
        if os.path.exists(master_key_file):
            with open(master_key_file, 'rb') as f:
                return f.read()
        
        # 새 마스터 키 생성
        new_master_key = Fernet.generate_key()
        
        # 디렉토리 생성
        os.makedirs('security', exist_ok=True)
        
        # 마스터 키 저장
        with open(master_key_file, 'wb') as f:
            f.write(new_master_key)
        
        logger.warning("새 마스터 키가 생성되었습니다. 환경변수 MASTER_ENCRYPTION_KEY에 설정하세요.")
        return new_master_key
    
    def _load_keys(self):
        """암호화 키 로드"""
        try:
            key_dir = self.config['key_storage_path']
            if not os.path.exists(key_dir):
                os.makedirs(key_dir, exist_ok=True)
                return
            
            for filename in os.listdir(key_dir):
                if filename.endswith('.key'):
                    key_path = os.path.join(key_dir, filename)
                    with open(key_path, 'rb') as f:
                        key_data = json.loads(f.read().decode())
                        
                        key = EncryptionKey(
                            key_id=key_data['key_id'],
                            key_type=key_data['key_type'],
                            key_data=base64.b64decode(key_data['key_data']),
                            created_at=key_data['created_at'],
                            expires_at=key_data.get('expires_at'),
                            is_active=key_data['is_active'],
                            metadata=key_data.get('metadata', {})
                        )
                        
                        self.keys[key.key_id] = key
            
        except Exception as e:
            logger.error(f"암호화 키 로드 실패: {e}")
    
    def _init_encryption_engines(self):
        """암호화 엔진 초기화"""
        # 대칭키 암호화 엔진
        self.symmetric_engine = Fernet(self.master_key)
        
        # 비대칭키 쌍 생성
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
    
    def _init_security_policies(self) -> Dict[str, Any]:
        """보안 정책 초기화"""
        return {
            'data_classification': {
                'public': {
                    'encryption_required': False,
                    'access_control': 'minimal',
                    'audit_level': 'basic'
                },
                'internal': {
                    'encryption_required': True,
                    'encryption_type': 'symmetric',
                    'access_control': 'role_based',
                    'audit_level': 'standard'
                },
                'confidential': {
                    'encryption_required': True,
                    'encryption_type': 'asymmetric',
                    'access_control': 'strict',
                    'audit_level': 'detailed'
                },
                'restricted': {
                    'encryption_required': True,
                    'encryption_type': 'asymmetric',
                    'access_control': 'maximum',
                    'audit_level': 'comprehensive'
                }
            },
            'key_management': {
                'rotation_interval_days': self.config['key_rotation_days'],
                'backup_required': self.config['backup_keys'],
                'key_size_minimum': 256,
                'algorithm_requirements': ['AES-256-GCM', 'RSA-2048']
            }
        }
    
    def generate_key(self, key_type: str = 'symmetric', metadata: Dict[str, Any] = None) -> str:
        """암호화 키 생성"""
        try:
            key_id = f"key_{int(time.time())}_{secrets.token_hex(8)}"
            
            if key_type == 'symmetric':
                key_data = Fernet.generate_key()
            elif key_type == 'asymmetric':
                # 비대칭키는 별도로 관리
                key_data = secrets.token_bytes(32)
            else:
                raise ValueError(f"지원하지 않는 키 타입: {key_type}")
            
            # 만료 시간 설정
            expires_at = None
            if self.config['key_rotation_days']:
                expires_at = time.strftime('%Y-%m-%d %H:%M:%S', 
                                         time.localtime(time.time() + self.config['key_rotation_days'] * 24 * 3600))
            
            # 키 객체 생성
            key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                key_data=key_data,
                created_at=time.strftime('%Y-%m-%d %H:%M:%S'),
                expires_at=expires_at,
                is_active=True,
                metadata=metadata or {}
            )
            
            # 키 저장
            self.keys[key_id] = key
            self._save_key(key)
            
            logger.info(f"암호화 키 생성 완료: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"암호화 키 생성 실패: {e}")
            raise
    
    def _save_key(self, key: EncryptionKey):
        """키 저장"""
        try:
            key_dir = self.config['key_storage_path']
            os.makedirs(key_dir, exist_ok=True)
            
            key_data = {
                'key_id': key.key_id,
                'key_type': key.key_type,
                'key_data': base64.b64encode(key.key_data).decode(),
                'created_at': key.created_at,
                'expires_at': key.expires_at,
                'is_active': key.is_active,
                'metadata': key.metadata
            }
            
            key_path = os.path.join(key_dir, f"{key.key_id}.key")
            with open(key_path, 'w') as f:
                json.dump(key_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"키 저장 실패: {e}")
    
    def encrypt_data(self, data: Union[str, bytes], 
                    sensitivity: DataSensitivity = DataSensitivity.CONFIDENTIAL,
                    key_id: Optional[str] = None) -> EncryptedData:
        """데이터 암호화"""
        try:
            # 데이터를 바이트로 변환
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # 민감도에 따른 암호화 정책 적용
            policy = self.security_policies['data_classification'][sensitivity.value]
            
            if not policy['encryption_required']:
                # 암호화 불필요한 경우
                return EncryptedData(
                    data=data_bytes,
                    key_id='none',
                    algorithm='none',
                    iv=None,
                    tag=None,
                    metadata={'sensitivity': sensitivity.value}
                )
            
            # 키 선택
            if key_id and key_id in self.keys:
                key = self.keys[key_id]
            else:
                # 새 키 생성
                key_type = policy.get('encryption_type', 'symmetric')
                key_id = self.generate_key(key_type)
                key = self.keys[key_id]
            
            # 암호화 수행
            if key.key_type == 'symmetric':
                return self._encrypt_symmetric(data_bytes, key)
            elif key.key_type == 'asymmetric':
                return self._encrypt_asymmetric(data_bytes, key)
            else:
                raise ValueError(f"지원하지 않는 암호화 타입: {key.key_type}")
            
        except Exception as e:
            logger.error(f"데이터 암호화 실패: {e}")
            raise
    
    def _encrypt_symmetric(self, data: bytes, key: EncryptionKey) -> EncryptedData:
        """대칭키 암호화"""
        try:
            # AES-256-GCM 암호화
            iv = os.urandom(12)  # 96비트 IV
            cipher = Cipher(algorithms.AES(key.key_data), modes.GCM(iv))
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            return EncryptedData(
                data=ciphertext,
                key_id=key.key_id,
                algorithm='AES-256-GCM',
                iv=iv,
                tag=encryptor.tag,
                metadata={'encryption_type': 'symmetric'}
            )
            
        except Exception as e:
            logger.error(f"대칭키 암호화 실패: {e}")
            raise
    
    def _encrypt_asymmetric(self, data: bytes, key: EncryptionKey) -> EncryptedData:
        """비대칭키 암호화"""
        try:
            # RSA 암호화 (작은 데이터용)
            if len(data) > 190:  # RSA-2048 제한
                # 대용량 데이터는 하이브리드 암호화
                return self._encrypt_hybrid(data, key)
            
            ciphertext = self.public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return EncryptedData(
                data=ciphertext,
                key_id=key.key_id,
                algorithm='RSA-2048-OAEP',
                iv=None,
                tag=None,
                metadata={'encryption_type': 'asymmetric'}
            )
            
        except Exception as e:
            logger.error(f"비대칭키 암호화 실패: {e}")
            raise
    
    def _encrypt_hybrid(self, data: bytes, key: EncryptionKey) -> EncryptedData:
        """하이브리드 암호화 (대용량 데이터용)"""
        try:
            # 임시 대칭키 생성
            temp_key = os.urandom(32)
            
            # 데이터를 대칭키로 암호화
            iv = os.urandom(12)
            cipher = Cipher(algorithms.AES(temp_key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # 임시 키를 공개키로 암호화
            encrypted_key = self.public_key.encrypt(
                temp_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # 암호화된 키와 데이터를 결합
            combined_data = len(encrypted_key).to_bytes(4, 'big') + encrypted_key + ciphertext
            
            return EncryptedData(
                data=combined_data,
                key_id=key.key_id,
                algorithm='RSA-AES-HYBRID',
                iv=iv,
                tag=encryptor.tag,
                metadata={'encryption_type': 'hybrid'}
            )
            
        except Exception as e:
            logger.error(f"하이브리드 암호화 실패: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """데이터 복호화"""
        try:
            if encrypted_data.algorithm == 'none':
                return encrypted_data.data
            
            # 키 조회
            if encrypted_data.key_id not in self.keys:
                raise ValueError(f"키를 찾을 수 없습니다: {encrypted_data.key_id}")
            
            key = self.keys[encrypted_data.key_id]
            
            # 복호화 수행
            if key.key_type == 'symmetric':
                return self._decrypt_symmetric(encrypted_data, key)
            elif key.key_type == 'asymmetric':
                return self._decrypt_asymmetric(encrypted_data, key)
            else:
                raise ValueError(f"지원하지 않는 복호화 타입: {key.key_type}")
            
        except Exception as e:
            logger.error(f"데이터 복호화 실패: {e}")
            raise
    
    def _decrypt_symmetric(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """대칭키 복호화"""
        try:
            if encrypted_data.algorithm == 'AES-256-GCM':
                cipher = Cipher(algorithms.AES(key.key_data), modes.GCM(encrypted_data.iv, encrypted_data.tag))
                decryptor = cipher.decryptor()
                
                plaintext = decryptor.update(encrypted_data.data) + decryptor.finalize()
                return plaintext
            else:
                raise ValueError(f"지원하지 않는 대칭키 알고리즘: {encrypted_data.algorithm}")
            
        except Exception as e:
            logger.error(f"대칭키 복호화 실패: {e}")
            raise
    
    def _decrypt_asymmetric(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """비대칭키 복호화"""
        try:
            if encrypted_data.algorithm == 'RSA-2048-OAEP':
                plaintext = self.private_key.decrypt(
                    encrypted_data.data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                return plaintext
            elif encrypted_data.algorithm == 'RSA-AES-HYBRID':
                return self._decrypt_hybrid(encrypted_data, key)
            else:
                raise ValueError(f"지원하지 않는 비대칭키 알고리즘: {encrypted_data.algorithm}")
            
        except Exception as e:
            logger.error(f"비대칭키 복호화 실패: {e}")
            raise
    
    def _decrypt_hybrid(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """하이브리드 복호화"""
        try:
            # 암호화된 키 길이 추출
            key_length = int.from_bytes(encrypted_data.data[:4], 'big')
            
            # 암호화된 키 추출
            encrypted_key = encrypted_data.data[4:4+key_length]
            
            # 키 복호화
            temp_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # 데이터 복호화
            ciphertext = encrypted_data.data[4+key_length:]
            cipher = Cipher(algorithms.AES(temp_key), modes.GCM(encrypted_data.iv, encrypted_data.tag))
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
            
        except Exception as e:
            logger.error(f"하이브리드 복호화 실패: {e}")
            raise
    
    def hash_data(self, data: Union[str, bytes], salt: Optional[bytes] = None) -> Dict[str, bytes]:
        """데이터 해시"""
        try:
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # 솔트 생성
            if salt is None:
                salt = os.urandom(16)
            
            # 해시 생성
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                data_bytes,
                salt,
                100000  # 반복 횟수
            )
            
            return {
                'hash': hash_obj,
                'salt': salt,
                'algorithm': 'PBKDF2-SHA256'
            }
            
        except Exception as e:
            logger.error(f"데이터 해시 실패: {e}")
            raise
    
    def verify_hash(self, data: Union[str, bytes], hash_data: Dict[str, bytes]) -> bool:
        """해시 검증"""
        try:
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # 해시 재계산
            calculated_hash = hashlib.pbkdf2_hmac(
                'sha256',
                data_bytes,
                hash_data['salt'],
                100000
            )
            
            # 해시 비교
            return hmac.compare_digest(calculated_hash, hash_data['hash'])
            
        except Exception as e:
            logger.error(f"해시 검증 실패: {e}")
            return False
    
    def create_hmac(self, data: Union[str, bytes], key: bytes) -> bytes:
        """HMAC 생성"""
        try:
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            return hmac.new(key, data_bytes, hashlib.sha256).digest()
            
        except Exception as e:
            logger.error(f"HMAC 생성 실패: {e}")
            raise
    
    def verify_hmac(self, data: Union[str, bytes], key: bytes, hmac_value: bytes) -> bool:
        """HMAC 검증"""
        try:
            calculated_hmac = self.create_hmac(data, key)
            return hmac.compare_digest(calculated_hmac, hmac_value)
            
        except Exception as e:
            logger.error(f"HMAC 검증 실패: {e}")
            return False
    
    def rotate_keys(self) -> List[str]:
        """키 로테이션"""
        try:
            rotated_keys = []
            current_time = time.time()
            
            for key_id, key in list(self.keys.items()):
                # 만료된 키 확인
                if key.expires_at:
                    expires_timestamp = time.mktime(time.strptime(key.expires_at, '%Y-%m-%d %H:%M:%S'))
                    if current_time > expires_timestamp:
                        # 새 키 생성
                        new_key_id = self.generate_key(key.key_type, key.metadata)
                        rotated_keys.append((key_id, new_key_id))
                        
                        # 기존 키 비활성화
                        key.is_active = False
                        self._save_key(key)
            
            logger.info(f"키 로테이션 완료: {len(rotated_keys)}개 키")
            return [new_id for _, new_id in rotated_keys]
            
        except Exception as e:
            logger.error(f"키 로테이션 실패: {e}")
            return []
    
    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """키 정보 조회"""
        if key_id not in self.keys:
            return None
        
        key = self.keys[key_id]
        return {
            'key_id': key.key_id,
            'key_type': key.key_type,
            'created_at': key.created_at,
            'expires_at': key.expires_at,
            'is_active': key.is_active,
            'metadata': key.metadata
        }
    
    def backup_keys(self, backup_path: str) -> bool:
        """키 백업"""
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            for key_id, key in self.keys.items():
                backup_file = os.path.join(backup_path, f"{key_id}.backup")
                
                backup_data = {
                    'key_id': key.key_id,
                    'key_type': key.key_type,
                    'key_data': base64.b64encode(key.key_data).decode(),
                    'created_at': key.created_at,
                    'expires_at': key.expires_at,
                    'is_active': key.is_active,
                    'metadata': key.metadata,
                    'backup_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2)
            
            logger.info(f"키 백업 완료: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"키 백업 실패: {e}")
            return False
    
    def restore_keys(self, backup_path: str) -> bool:
        """키 복원"""
        try:
            if not os.path.exists(backup_path):
                return False
            
            restored_count = 0
            for filename in os.listdir(backup_path):
                if filename.endswith('.backup'):
                    backup_file = os.path.join(backup_path, filename)
                    
                    with open(backup_file, 'r') as f:
                        backup_data = json.load(f)
                    
                    key = EncryptionKey(
                        key_id=backup_data['key_id'],
                        key_type=backup_data['key_type'],
                        key_data=base64.b64decode(backup_data['key_data']),
                        created_at=backup_data['created_at'],
                        expires_at=backup_data.get('expires_at'),
                        is_active=backup_data['is_active'],
                        metadata=backup_data.get('metadata', {})
                    )
                    
                    self.keys[key.key_id] = key
                    self._save_key(key)
                    restored_count += 1
            
            logger.info(f"키 복원 완료: {restored_count}개 키")
            return True
            
        except Exception as e:
            logger.error(f"키 복원 실패: {e}")
            return False

# 전역 암호화 시스템 인스턴스
data_encryption = DataEncryption() 