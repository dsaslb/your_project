import os
import json
import shutil
import zipfile
import hashlib
import logging
import schedule
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import tempfile

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BackupConfig:
    """백업 설정 클래스"""
    backup_dir: str
    max_backups: int = 30
    compression_level: int = 6
    encrypt_backups: bool = True
    retention_days: int = 90
    auto_backup_enabled: bool = True
    backup_schedule: str = "daily"  # daily, weekly, monthly
    backup_time: str = "02:00"  # 24시간 형식

@dataclass
class BackupJob:
    """백업 작업 정보"""
    job_id: str
    name: str
    source_paths: List[str]
    destination: str
    schedule: str
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    is_active: bool = True
    created_at: datetime = None

@dataclass
class BackupRecord:
    """백업 기록 정보"""
    backup_id: str
    job_id: str
    name: str
    file_path: str
    file_size: int
    checksum: str
    backup_type: str  # full, incremental
    status: str  # success, failed, in_progress
    start_time: datetime
    end_time: Optional[datetime]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class BackupManager:
    """백업 관리자 클래스"""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.backup_records: List[BackupRecord] = []
        self.is_running = False
        self.scheduler_thread = None
        
        # 백업 디렉토리 생성
        os.makedirs(config.backup_dir, exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 스케줄러 시작
        if config.auto_backup_enabled:
            self.start_scheduler()
    
    def init_database(self):
        """백업 데이터베이스 초기화"""
        db_path = os.path.join(self.config.backup_dir, 'backup.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 백업 작업 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_jobs (
                job_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                source_paths TEXT NOT NULL,
                destination TEXT NOT NULL,
                schedule TEXT NOT NULL,
                last_run TEXT,
                next_run TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 백업 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_records (
                backup_id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                backup_type TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                error_message TEXT,
                metadata TEXT,
                FOREIGN KEY (job_id) REFERENCES backup_jobs (job_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_backup_job(self, name: str, source_paths: List[str], 
                         destination: str, schedule: str = "daily") -> str:
        """백업 작업 생성"""
        job_id = self._generate_id()
        
        job = BackupJob(
            job_id=job_id,
            name=name,
            source_paths=source_paths,
            destination=destination,
            schedule=schedule,
            last_run=None,
            next_run=self._calculate_next_run(schedule),
            created_at=datetime.utcnow()
        )
        
        self.backup_jobs[job_id] = job
        self._save_job_to_db(job)
        
        logger.info(f"백업 작업 생성: {name} (ID: {job_id})")
        return job_id
    
    def _generate_id(self) -> str:
        """고유 ID 생성"""
        import uuid
        return str(uuid.uuid4())
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """다음 실행 시간 계산"""
        now = datetime.utcnow()
        
        if schedule == "daily":
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif schedule == "weekly":
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            days_ahead = 7 - next_run.weekday()
            next_run += timedelta(days=days_ahead)
        elif schedule == "monthly":
            next_run = now.replace(day=1, hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run
    
    def _save_job_to_db(self, job: BackupJob):
        """백업 작업을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.backup_dir, 'backup.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO backup_jobs 
            (job_id, name, source_paths, destination, schedule, last_run, next_run, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job.job_id,
            job.name,
            json.dumps(job.source_paths),
            job.destination,
            job.schedule,
            job.last_run.isoformat() if job.last_run else None,
            job.next_run.isoformat() if job.next_run else None,
            1 if job.is_active else 0,
            job.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def run_backup(self, job_id: str, backup_type: str = "full") -> str:
        """백업 실행"""
        if job_id not in self.backup_jobs:
            raise ValueError(f"백업 작업을 찾을 수 없습니다: {job_id}")
        
        job = self.backup_jobs[job_id]
        
        # 백업 기록 생성
        backup_id = self._generate_id()
        backup_record = BackupRecord(
            backup_id=backup_id,
            job_id=job_id,
            name=job.name,
            file_path="",
            file_size=0,
            checksum="",
            backup_type=backup_type,
            status="in_progress",
            start_time=datetime.utcnow(),
            metadata={"source_paths": job.source_paths}
        )
        
        self.backup_records.append(backup_record)
        
        try:
            # 백업 파일 생성
            backup_file = self._create_backup_file(job, backup_type)
            
            # 파일 정보 업데이트
            backup_record.file_path = backup_file
            backup_record.file_size = os.path.getsize(backup_file)
            backup_record.checksum = self._calculate_checksum(backup_file)
            backup_record.status = "success"
            backup_record.end_time = datetime.utcnow()
            
            # 작업 정보 업데이트
            job.last_run = datetime.utcnow()
            job.next_run = self._calculate_next_run(job.schedule)
            self._save_job_to_db(job)
            
            # 오래된 백업 정리
            self._cleanup_old_backups()
            
            logger.info(f"백업 완료: {job.name} (ID: {backup_id})")
            
        except Exception as e:
            backup_record.status = "failed"
            backup_record.error_message = str(e)
            backup_record.end_time = datetime.utcnow()
            logger.error(f"백업 실패: {job.name} - {e}")
        
        # 데이터베이스에 저장
        self._save_backup_record(backup_record)
        
        return backup_id
    
    def _create_backup_file(self, job: BackupJob, backup_type: str) -> str:
        """백업 파일 생성"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{job.name}_{backup_type}_{timestamp}.zip"
        backup_path = os.path.join(job.destination, filename)
        
        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            # 소스 파일들을 임시 디렉토리로 복사
            for source_path in job.source_paths:
                if os.path.exists(source_path):
                    dest_path = os.path.join(temp_dir, os.path.basename(source_path))
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
            
            # ZIP 파일 생성
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, 
                               compresslevel=self.config.compression_level) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
        
        return backup_path
    
    def _calculate_checksum(self, file_path: str) -> str:
        """파일 체크섬 계산"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _save_backup_record(self, record: BackupRecord):
        """백업 기록을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.backup_dir, 'backup.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO backup_records 
            (backup_id, job_id, name, file_path, file_size, checksum, backup_type, 
             status, start_time, end_time, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.backup_id,
            record.job_id,
            record.name,
            record.file_path,
            record.file_size,
            record.checksum,
            record.backup_type,
            record.status,
            record.start_time.isoformat(),
            record.end_time.isoformat() if record.end_time else None,
            record.error_message,
            json.dumps(record.metadata) if record.metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def restore_backup(self, backup_id: str, destination: str) -> bool:
        """백업에서 복구"""
        # 백업 기록 찾기
        backup_record = None
        for record in self.backup_records:
            if record.backup_id == backup_id:
                backup_record = record
                break
        
        if not backup_record:
            raise ValueError(f"백업 기록을 찾을 수 없습니다: {backup_id}")
        
        if not os.path.exists(backup_record.file_path):
            raise FileNotFoundError(f"백업 파일을 찾을 수 없습니다: {backup_record.file_path}")
        
        try:
            # 복구 디렉토리 생성
            os.makedirs(destination, exist_ok=True)
            
            # ZIP 파일 압축 해제
            with zipfile.ZipFile(backup_record.file_path, 'r') as zipf:
                zipf.extractall(destination)
            
            logger.info(f"복구 완료: {backup_record.name} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"복구 실패: {backup_record.name} - {e}")
            return False
    
    def _cleanup_old_backups(self):
        """오래된 백업 정리"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
        
        # 오래된 백업 파일 삭제
        for record in self.backup_records[:]:  # 복사본으로 반복
            if record.start_time < cutoff_date and record.status == "success":
                try:
                    if os.path.exists(record.file_path):
                        os.remove(record.file_path)
                        logger.info(f"오래된 백업 파일 삭제: {record.file_path}")
                    
                    # 기록에서 제거
                    self.backup_records.remove(record)
                    self._delete_backup_record(record.backup_id)
                    
                except Exception as e:
                    logger.error(f"백업 파일 삭제 실패: {record.file_path} - {e}")
    
    def _delete_backup_record(self, backup_id: str):
        """백업 기록 삭제"""
        db_path = os.path.join(self.config.backup_dir, 'backup.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM backup_records WHERE backup_id = ?', (backup_id,))
        
        conn.commit()
        conn.close()
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """백업 통계 조회"""
        total_backups = len(self.backup_records)
        successful_backups = len([r for r in self.backup_records if r.status == "success"])
        failed_backups = len([r for r in self.backup_records if r.status == "failed"])
        
        total_size = sum(r.file_size for r in self.backup_records if r.status == "success")
        
        # 최근 7일 통계
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_backups = [r for r in self.backup_records if r.start_time > week_ago]
        
        return {
            'total_backups': total_backups,
            'successful_backups': successful_backups,
            'failed_backups': failed_backups,
            'success_rate': (successful_backups / total_backups * 100) if total_backups > 0 else 0,
            'total_size_mb': total_size / (1024 * 1024),
            'recent_backups_7d': len(recent_backups),
            'active_jobs': len([j for j in self.backup_jobs.values() if j.is_active])
        }
    
    def get_backup_records(self, job_id: Optional[str] = None, 
                          status: Optional[str] = None, limit: int = 100) -> List[BackupRecord]:
        """백업 기록 조회"""
        records = self.backup_records
        
        if job_id:
            records = [r for r in records if r.job_id == job_id]
        if status:
            records = [r for r in records if r.status == status]
        
        # 최신 순으로 정렬
        records.sort(key=lambda x: x.start_time, reverse=True)
        return records[:limit]
    
    def start_scheduler(self):
        """백업 스케줄러 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 스케줄 설정
        for job in self.backup_jobs.values():
            if job.is_active:
                self._schedule_job(job)
        
        # 스케줄러 스레드 시작
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("백업 스케줄러가 시작되었습니다")
    
    def _schedule_job(self, job: BackupJob):
        """백업 작업 스케줄링"""
        if job.schedule == "daily":
            schedule.every().day.at(job.next_run.strftime("%H:%M")).do(
                self._execute_scheduled_backup, job.job_id
            )
        elif job.schedule == "weekly":
            schedule.every().week.at(job.next_run.strftime("%H:%M")).do(
                self._execute_scheduled_backup, job.job_id
            )
        elif job.schedule == "monthly":
            # 매월 1일 실행
            schedule.every().month.at(job.next_run.strftime("%H:%M")).do(
                self._execute_scheduled_backup, job.job_id
            )
    
    def _execute_scheduled_backup(self, job_id: str):
        """스케줄된 백업 실행"""
        try:
            self.run_backup(job_id)
        except Exception as e:
            logger.error(f"스케줄된 백업 실행 실패: {job_id} - {e}")
    
    def _run_scheduler(self):
        """스케줄러 실행"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    
    def stop_scheduler(self):
        """백업 스케줄러 중지"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("백업 스케줄러가 중지되었습니다")
    
    def test_backup(self, job_id: str) -> bool:
        """백업 테스트 실행"""
        try:
            backup_id = self.run_backup(job_id, "test")
            
            # 백업 파일 검증
            backup_record = next((r for r in self.backup_records if r.backup_id == backup_id), None)
            if backup_record and backup_record.status == "success":
                # 체크섬 검증
                current_checksum = self._calculate_checksum(backup_record.file_path)
                if current_checksum == backup_record.checksum:
                    logger.info(f"백업 테스트 성공: {backup_record.name}")
                    return True
            
            logger.error(f"백업 테스트 실패: {job_id}")
            return False
            
        except Exception as e:
            logger.error(f"백업 테스트 오류: {job_id} - {e}")
            return False 