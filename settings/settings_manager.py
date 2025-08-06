import os
import json
import yaml
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SettingsConfig:
    """설정 관리자 설정 클래스"""
    data_dir: str
    config_file: str = "config.json"
    env_file: str = ".env"
    backup_dir: str = "backups"
    max_backups: int = 10
    auto_backup: bool = True
    validate_on_save: bool = True
    encrypt_sensitive: bool = True

@dataclass
class SettingItem:
    """설정 항목 정보"""
    key: str
    value: Any
    category: str
    description: str
    data_type: str  # string, number, boolean, json, array
    is_sensitive: bool = False
    is_required: bool = False
    default_value: Any = None
    validation_rules: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class SettingCategory:
    """설정 카테고리 정보"""
    name: str
    description: str
    icon: str
    settings: List[SettingItem]
    is_active: bool = True
    created_at: datetime = None

@dataclass
class SettingsBackup:
    """설정 백업 정보"""
    backup_id: str
    name: str
    description: str
    settings_data: Dict[str, Any]
    created_by: str
    created_at: datetime
    file_path: str
    file_size: int
    checksum: str

@dataclass
class SettingsChange:
    """설정 변경 이력"""
    change_id: str
    setting_key: str
    old_value: Any
    new_value: Any
    changed_by: str
    change_reason: str
    timestamp: datetime
    category: str

class SettingsManager:
    """시스템 설정 관리자 클래스"""
    
    def __init__(self, config: SettingsConfig):
        self.config = config
        self.settings: Dict[str, SettingItem] = {}
        self.categories: Dict[str, SettingCategory] = {}
        self.backups: List[SettingsBackup] = []
        self.changes: List[SettingsChange] = []
        
        # 설정 디렉토리 생성
        os.makedirs(config.data_dir, exist_ok=True)
        os.makedirs(os.path.join(config.data_dir, config.backup_dir), exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 기본 설정 생성
        self.create_default_settings()
        
        # 기존 설정 로드
        self.load_settings()
    
    def init_database(self):
        """설정 데이터베이스 초기화"""
        db_path = os.path.join(self.config.data_dir, 'settings.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 설정 항목 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                data_type TEXT NOT NULL,
                is_sensitive INTEGER DEFAULT 0,
                is_required INTEGER DEFAULT 0,
                default_value TEXT,
                validation_rules TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 설정 카테고리 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY,
                description TEXT,
                icon TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 설정 백업 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                backup_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                settings_data TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                checksum TEXT NOT NULL
            )
        ''')
        
        # 설정 변경 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS changes (
                change_id TEXT PRIMARY KEY,
                setting_key TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT NOT NULL,
                change_reason TEXT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_settings(self):
        """기본 설정 생성"""
        # 시스템 설정
        self.create_setting(
            key='app_name',
            value='퀀텀 비즈니스 관리 시스템',
            category='system',
            description='애플리케이션 이름',
            data_type='string',
            is_required=True
        )
        
        self.create_setting(
            key='app_version',
            value='1.0.0',
            category='system',
            description='애플리케이션 버전',
            data_type='string',
            is_required=True
        )
        
        self.create_setting(
            key='debug_mode',
            value=False,
            category='system',
            description='디버그 모드 활성화',
            data_type='boolean',
            default_value=False
        )
        
        # 데이터베이스 설정
        self.create_setting(
            key='db_host',
            value='localhost',
            category='database',
            description='데이터베이스 호스트',
            data_type='string',
            is_required=True
        )
        
        self.create_setting(
            key='db_port',
            value=5432,
            category='database',
            description='데이터베이스 포트',
            data_type='number',
            default_value=5432
        )
        
        # API 설정
        self.create_setting(
            key='api_host',
            value='localhost',
            category='api',
            description='API 서버 호스트',
            data_type='string',
            is_required=True
        )
        
        self.create_setting(
            key='api_port',
            value=5000,
            category='api',
            description='API 서버 포트',
            data_type='number',
            default_value=5000
        )
        
        # 보안 설정
        self.create_setting(
            key='jwt_secret',
            value='',
            category='security',
            description='JWT 시크릿 키',
            data_type='string',
            is_sensitive=True,
            is_required=True
        )
        
        self.create_setting(
            key='password_min_length',
            value=8,
            category='security',
            description='최소 비밀번호 길이',
            data_type='number',
            default_value=8,
            validation_rules={'min': 6, 'max': 50}
        )
    
    def create_setting(self, key: str, value: Any, category: str, description: str,
                      data_type: str, is_sensitive: bool = False, is_required: bool = False,
                      default_value: Any = None, validation_rules: Optional[Dict[str, Any]] = None) -> str:
        """설정 항목 생성"""
        # 값 검증
        if self.config.validate_on_save:
            validation_result = self.validate_setting_value(key, value, data_type, validation_rules)
            if not validation_result['valid']:
                raise ValueError(f"설정 값 검증 실패: {validation_result['message']}")
        
        setting = SettingItem(
            key=key,
            value=value,
            category=category,
            description=description,
            data_type=data_type,
            is_sensitive=is_sensitive,
            is_required=is_required,
            default_value=default_value,
            validation_rules=validation_rules,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.settings[key] = setting
        self._save_setting(setting)
        
        logger.info(f"설정 항목 생성: {key}")
        return key
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        if key in self.settings:
            return self.settings[key].value
        return default
    
    def set_setting(self, key: str, value: Any, changed_by: str = "system", change_reason: str = "") -> bool:
        """설정 값 변경"""
        if key not in self.settings:
            raise ValueError(f"설정 키를 찾을 수 없습니다: {key}")
        
        setting = self.settings[key]
        old_value = setting.value
        
        # 값 검증
        if self.config.validate_on_save:
            validation_result = self.validate_setting_value(key, value, setting.data_type, setting.validation_rules)
            if not validation_result['valid']:
                raise ValueError(f"설정 값 검증 실패: {validation_result['message']}")
        
        # 값 변경
        setting.value = value
        setting.updated_at = datetime.utcnow()
        
        # 변경 이력 기록
        change = SettingsChange(
            change_id=str(uuid.uuid4()),
            setting_key=key,
            old_value=old_value,
            new_value=value,
            changed_by=changed_by,
            change_reason=change_reason,
            timestamp=datetime.utcnow(),
            category=setting.category
        )
        
        self.changes.append(change)
        self._save_setting(setting)
        self._save_change(change)
        
        logger.info(f"설정 값 변경: {key} = {value}")
        return True
    
    def validate_setting_value(self, key: str, value: Any, data_type: str, validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """설정 값 검증"""
        try:
            # 데이터 타입 검증
            if data_type == 'string':
                if not isinstance(value, str):
                    return {'valid': False, 'message': '문자열 타입이어야 합니다'}
            elif data_type == 'number':
                if not isinstance(value, (int, float)):
                    return {'valid': False, 'message': '숫자 타입이어야 합니다'}
            elif data_type == 'boolean':
                if not isinstance(value, bool):
                    return {'valid': False, 'message': '불린 타입이어야 합니다'}
            elif data_type == 'json':
                try:
                    json.dumps(value)
                except:
                    return {'valid': False, 'message': '유효한 JSON 형식이어야 합니다'}
            elif data_type == 'array':
                if not isinstance(value, list):
                    return {'valid': False, 'message': '배열 타입이어야 합니다'}
            
            # 추가 검증 규칙
            if validation_rules:
                if 'min' in validation_rules and value < validation_rules['min']:
                    return {'valid': False, 'message': f'최소값 {validation_rules["min"]} 이상이어야 합니다'}
                
                if 'max' in validation_rules and value > validation_rules['max']:
                    return {'valid': False, 'message': f'최대값 {validation_rules["max"]} 이하여야 합니다'}
                
                if 'min_length' in validation_rules and len(str(value)) < validation_rules['min_length']:
                    return {'valid': False, 'message': f'최소 길이 {validation_rules["min_length"]} 이상이어야 합니다'}
                
                if 'max_length' in validation_rules and len(str(value)) > validation_rules['max_length']:
                    return {'valid': False, 'message': f'최대 길이 {validation_rules["max_length"]} 이하여야 합니다'}
                
                if 'pattern' in validation_rules:
                    if not re.match(validation_rules['pattern'], str(value)):
                        return {'valid': False, 'message': f'패턴 {validation_rules["pattern"]}과 일치해야 합니다'}
                
                if 'enum' in validation_rules and value not in validation_rules['enum']:
                    return {'valid': False, 'message': f'허용된 값 중 하나여야 합니다: {validation_rules["enum"]}'}
            
            return {'valid': True, 'message': '검증 성공'}
            
        except Exception as e:
            return {'valid': False, 'message': f'검증 중 오류 발생: {str(e)}'}
    
    def get_settings_by_category(self, category: str) -> List[SettingItem]:
        """카테고리별 설정 조회"""
        return [setting for setting in self.settings.values() if setting.category == category]
    
    def get_all_settings(self) -> Dict[str, Any]:
        """모든 설정 값 조회 (민감한 정보 제외)"""
        result = {}
        for key, setting in self.settings.items():
            if setting.is_sensitive:
                result[key] = '***' if setting.value else ''
            else:
                result[key] = setting.value
        return result
    
    def get_settings_stats(self) -> Dict[str, Any]:
        """설정 통계 조회"""
        total_settings = len(self.settings)
        sensitive_settings = len([s for s in self.settings.values() if s.is_sensitive])
        required_settings = len([s for s in self.settings.values() if s.is_required])
        
        category_stats = {}
        for category_name in set([s.category for s in self.settings.values()]):
            category_settings = self.get_settings_by_category(category_name)
            category_stats[category_name] = len(category_settings)
        
        return {
            'total_settings': total_settings,
            'sensitive_settings': sensitive_settings,
            'required_settings': required_settings,
            'categories': len(category_stats),
            'backups': len(self.backups),
            'changes_today': len([c for c in self.changes if c.timestamp.date() == datetime.utcnow().date()]),
            'category_stats': category_stats
        }
    
    def get_recent_changes(self, limit: int = 50) -> List[SettingsChange]:
        """최근 변경 이력 조회"""
        sorted_changes = sorted(self.changes, key=lambda x: x.timestamp, reverse=True)
        return sorted_changes[:limit]
    
    def load_settings(self):
        """설정 로드"""
        try:
            # 데이터베이스에서 설정 로드
            self._load_settings_from_db()
            self._load_changes_from_db()
            
            logger.info(f"설정 로드 완료: {len(self.settings)}개 항목")
            
        except Exception as e:
            logger.error(f"설정 로드 오류: {str(e)}")
    
    # 데이터베이스 저장 메서드들
    def _save_setting(self, setting: SettingItem):
        """설정을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'settings.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings 
            (key, value, category, description, data_type, is_sensitive, is_required, 
             default_value, validation_rules, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            setting.key,
            json.dumps(setting.value),
            setting.category,
            setting.description,
            setting.data_type,
            1 if setting.is_sensitive else 0,
            1 if setting.is_required else 0,
            json.dumps(setting.default_value) if setting.default_value is not None else None,
            json.dumps(setting.validation_rules) if setting.validation_rules else None,
            setting.created_at.isoformat(),
            setting.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_change(self, change: SettingsChange):
        """변경 이력을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'settings.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO changes 
            (change_id, setting_key, old_value, new_value, changed_by, change_reason, 
             timestamp, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            change.change_id,
            change.setting_key,
            json.dumps(change.old_value),
            json.dumps(change.new_value),
            change.changed_by,
            change.change_reason,
            change.timestamp.isoformat(),
            change.category
        ))
        
        conn.commit()
        conn.close()
    
    def _load_settings_from_db(self):
        """데이터베이스에서 설정 로드"""
        db_path = os.path.join(self.config.data_dir, 'settings.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM settings')
        rows = cursor.fetchall()
        
        for row in rows:
            setting = SettingItem(
                key=row[0],
                value=json.loads(row[1]),
                category=row[2],
                description=row[3],
                data_type=row[4],
                is_sensitive=bool(row[5]),
                is_required=bool(row[6]),
                default_value=json.loads(row[7]) if row[7] else None,
                validation_rules=json.loads(row[8]) if row[8] else None,
                created_at=datetime.fromisoformat(row[9]),
                updated_at=datetime.fromisoformat(row[10])
            )
            self.settings[setting.key] = setting
        
        conn.close()
    
    def _load_changes_from_db(self):
        """데이터베이스에서 변경 이력 로드"""
        db_path = os.path.join(self.config.data_dir, 'settings.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM changes ORDER BY timestamp DESC LIMIT 1000')
        rows = cursor.fetchall()
        
        for row in rows:
            change = SettingsChange(
                change_id=row[0],
                setting_key=row[1],
                old_value=json.loads(row[2]) if row[2] else None,
                new_value=json.loads(row[3]) if row[3] else None,
                changed_by=row[4],
                change_reason=row[5],
                timestamp=datetime.fromisoformat(row[6]),
                category=row[7]
            )
            self.changes.append(change)
        
        conn.close() 