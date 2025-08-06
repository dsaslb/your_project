from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os
from backup.backup_manager import BackupManager, BackupConfig, BackupJob, BackupRecord

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 백업 API 블루프린트 생성
backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

# 백업 관리자 초기화
backup_config = BackupConfig(
    backup_dir="./backups",
    max_backups=30,
    compression_level=6,
    encrypt_backups=True,
    retention_days=90,
    auto_backup_enabled=True,
    backup_schedule="daily",
    backup_time="02:00"
)

backup_manager = BackupManager(backup_config)

@backup_bp.route('/jobs', methods=['GET'])
def get_backup_jobs():
    """백업 작업 목록 조회"""
    try:
        jobs = []
        for job in backup_manager.backup_jobs.values():
            jobs.append({
                'job_id': job.job_id,
                'name': job.name,
                'source_paths': job.source_paths,
                'destination': job.destination,
                'schedule': job.schedule,
                'last_run': job.last_run.isoformat() if job.last_run else None,
                'next_run': job.next_run.isoformat() if job.next_run else None,
                'is_active': job.is_active,
                'created_at': job.created_at.isoformat() if job.created_at else None
            })
        
        return jsonify({
            'jobs': jobs,
            'total_count': len(jobs)
        }), 200
        
    except Exception as e:
        logger.error(f"백업 작업 조회 오류: {e}")
        return jsonify({'error': '백업 작업 조회 중 오류가 발생했습니다'}), 500

@backup_bp.route('/jobs', methods=['POST'])
def create_backup_job():
    """백업 작업 생성"""
    try:
        data = request.get_json()
        name = data.get('name')
        source_paths = data.get('source_paths', [])
        destination = data.get('destination')
        schedule = data.get('schedule', 'daily')
        
        if not name or not source_paths or not destination:
            return jsonify({'error': '필수 필드가 누락되었습니다'}), 400
        
        # 소스 경로 유효성 검사
        for path in source_paths:
            if not os.path.exists(path):
                return jsonify({'error': f'소스 경로가 존재하지 않습니다: {path}'}), 400
        
        # 대상 디렉토리 생성
        os.makedirs(destination, exist_ok=True)
        
        job_id = backup_manager.create_backup_job(name, source_paths, destination, schedule)
        
        return jsonify({
            'message': '백업 작업이 생성되었습니다',
            'job_id': job_id
        }), 201
        
    except Exception as e:
        logger.error(f"백업 작업 생성 오류: {e}")
        return jsonify({'error': '백업 작업 생성 중 오류가 발생했습니다'}), 500

@backup_bp.route('/jobs/<job_id>', methods=['PUT'])
def update_backup_job(job_id):
    """백업 작업 수정"""
    try:
        if job_id not in backup_manager.backup_jobs:
            return jsonify({'error': '백업 작업을 찾을 수 없습니다'}), 404
        
        data = request.get_json()
        job = backup_manager.backup_jobs[job_id]
        
        # 업데이트 가능한 필드들
        if 'name' in data:
            job.name = data['name']
        if 'source_paths' in data:
            # 소스 경로 유효성 검사
            for path in data['source_paths']:
                if not os.path.exists(path):
                    return jsonify({'error': f'소스 경로가 존재하지 않습니다: {path}'}), 400
            job.source_paths = data['source_paths']
        if 'destination' in data:
            os.makedirs(data['destination'], exist_ok=True)
            job.destination = data['destination']
        if 'schedule' in data:
            job.schedule = data['schedule']
            job.next_run = backup_manager._calculate_next_run(data['schedule'])
        if 'is_active' in data:
            job.is_active = data['is_active']
        
        backup_manager._save_job_to_db(job)
        
        return jsonify({'message': '백업 작업이 업데이트되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"백업 작업 수정 오류: {e}")
        return jsonify({'error': '백업 작업 수정 중 오류가 발생했습니다'}), 500

@backup_bp.route('/jobs/<job_id>', methods=['DELETE'])
def delete_backup_job(job_id):
    """백업 작업 삭제"""
    try:
        if job_id not in backup_manager.backup_jobs:
            return jsonify({'error': '백업 작업을 찾을 수 없습니다'}), 404
        
        # 관련 백업 기록도 삭제
        backup_records = backup_manager.get_backup_records(job_id=job_id)
        for record in backup_records:
            if os.path.exists(record.file_path):
                os.remove(record.file_path)
            backup_manager._delete_backup_record(record.backup_id)
        
        # 작업 삭제
        del backup_manager.backup_jobs[job_id]
        
        # 데이터베이스에서 삭제
        db_path = os.path.join(backup_manager.config.backup_dir, 'backup.db')
        conn = backup_manager._get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM backup_jobs WHERE job_id = ?', (job_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '백업 작업이 삭제되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"백업 작업 삭제 오류: {e}")
        return jsonify({'error': '백업 작업 삭제 중 오류가 발생했습니다'}), 500

@backup_bp.route('/jobs/<job_id>/run', methods=['POST'])
def run_backup_job(job_id):
    """백업 작업 실행"""
    try:
        if job_id not in backup_manager.backup_jobs:
            return jsonify({'error': '백업 작업을 찾을 수 없습니다'}), 404
        
        data = request.get_json() or {}
        backup_type = data.get('backup_type', 'full')
        
        backup_id = backup_manager.run_backup(job_id, backup_type)
        
        return jsonify({
            'message': '백업이 시작되었습니다',
            'backup_id': backup_id
        }), 200
        
    except Exception as e:
        logger.error(f"백업 실행 오류: {e}")
        return jsonify({'error': '백업 실행 중 오류가 발생했습니다'}), 500

@backup_bp.route('/jobs/<job_id>/test', methods=['POST'])
def test_backup_job(job_id):
    """백업 작업 테스트"""
    try:
        if job_id not in backup_manager.backup_jobs:
            return jsonify({'error': '백업 작업을 찾을 수 없습니다'}), 404
        
        success = backup_manager.test_backup(job_id)
        
        if success:
            return jsonify({'message': '백업 테스트가 성공했습니다'}), 200
        else:
            return jsonify({'error': '백업 테스트가 실패했습니다'}), 400
        
    except Exception as e:
        logger.error(f"백업 테스트 오류: {e}")
        return jsonify({'error': '백업 테스트 중 오류가 발생했습니다'}), 500

@backup_bp.route('/records', methods=['GET'])
def get_backup_records():
    """백업 기록 조회"""
    try:
        # 쿼리 파라미터
        job_id = request.args.get('job_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 100))
        
        records = backup_manager.get_backup_records(
            job_id=job_id,
            status=status,
            limit=limit
        )
        
        record_list = []
        for record in records:
            record_list.append({
                'backup_id': record.backup_id,
                'job_id': record.job_id,
                'name': record.name,
                'file_path': record.file_path,
                'file_size': record.file_size,
                'file_size_mb': record.file_size / (1024 * 1024),
                'checksum': record.checksum,
                'backup_type': record.backup_type,
                'status': record.status,
                'start_time': record.start_time.isoformat(),
                'end_time': record.end_time.isoformat() if record.end_time else None,
                'error_message': record.error_message,
                'metadata': record.metadata
            })
        
        return jsonify({
            'records': record_list,
            'total_count': len(record_list)
        }), 200
        
    except Exception as e:
        logger.error(f"백업 기록 조회 오류: {e}")
        return jsonify({'error': '백업 기록 조회 중 오류가 발생했습니다'}), 500

@backup_bp.route('/records/<backup_id>/restore', methods=['POST'])
def restore_backup(backup_id):
    """백업에서 복구"""
    try:
        data = request.get_json()
        destination = data.get('destination')
        
        if not destination:
            return jsonify({'error': '복구 대상 경로가 필요합니다'}), 400
        
        success = backup_manager.restore_backup(backup_id, destination)
        
        if success:
            return jsonify({
                'message': '백업에서 복구가 완료되었습니다',
                'destination': destination
            }), 200
        else:
            return jsonify({'error': '백업 복구에 실패했습니다'}), 500
        
    except Exception as e:
        logger.error(f"백업 복구 오류: {e}")
        return jsonify({'error': '백업 복구 중 오류가 발생했습니다'}), 500

@backup_bp.route('/records/<backup_id>', methods=['DELETE'])
def delete_backup_record(backup_id):
    """백업 기록 삭제"""
    try:
        # 백업 기록 찾기
        backup_record = None
        for record in backup_manager.backup_records:
            if record.backup_id == backup_id:
                backup_record = record
                break
        
        if not backup_record:
            return jsonify({'error': '백업 기록을 찾을 수 없습니다'}), 404
        
        # 백업 파일 삭제
        if os.path.exists(backup_record.file_path):
            os.remove(backup_record.file_path)
        
        # 기록에서 제거
        backup_manager.backup_records.remove(backup_record)
        backup_manager._delete_backup_record(backup_id)
        
        return jsonify({'message': '백업 기록이 삭제되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"백업 기록 삭제 오류: {e}")
        return jsonify({'error': '백업 기록 삭제 중 오류가 발생했습니다'}), 500

@backup_bp.route('/stats', methods=['GET'])
def get_backup_stats():
    """백업 통계 조회"""
    try:
        stats = backup_manager.get_backup_stats()
        
        return jsonify({
            'total_backups': stats['total_backups'],
            'successful_backups': stats['successful_backups'],
            'failed_backups': stats['failed_backups'],
            'success_rate': round(stats['success_rate'], 2),
            'total_size_mb': round(stats['total_size_mb'], 2),
            'recent_backups_7d': stats['recent_backups_7d'],
            'active_jobs': stats['active_jobs']
        }), 200
        
    except Exception as e:
        logger.error(f"백업 통계 조회 오류: {e}")
        return jsonify({'error': '백업 통계 조회 중 오류가 발생했습니다'}), 500

@backup_bp.route('/scheduler/start', methods=['POST'])
def start_scheduler():
    """백업 스케줄러 시작"""
    try:
        backup_manager.start_scheduler()
        
        return jsonify({'message': '백업 스케줄러가 시작되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"스케줄러 시작 오류: {e}")
        return jsonify({'error': '스케줄러 시작 중 오류가 발생했습니다'}), 500

@backup_bp.route('/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """백업 스케줄러 중지"""
    try:
        backup_manager.stop_scheduler()
        
        return jsonify({'message': '백업 스케줄러가 중지되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"스케줄러 중지 오류: {e}")
        return jsonify({'error': '스케줄러 중지 중 오류가 발생했습니다'}), 500

@backup_bp.route('/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """스케줄러 상태 조회"""
    try:
        return jsonify({
            'is_running': backup_manager.is_running,
            'auto_backup_enabled': backup_manager.config.auto_backup_enabled,
            'backup_schedule': backup_manager.config.backup_schedule,
            'backup_time': backup_manager.config.backup_time
        }), 200
        
    except Exception as e:
        logger.error(f"스케줄러 상태 조회 오류: {e}")
        return jsonify({'error': '스케줄러 상태 조회 중 오류가 발생했습니다'}), 500

@backup_bp.route('/cleanup', methods=['POST'])
def cleanup_old_backups():
    """오래된 백업 정리"""
    try:
        backup_manager._cleanup_old_backups()
        
        return jsonify({'message': '오래된 백업이 정리되었습니다'}), 200
        
    except Exception as e:
        logger.error(f"백업 정리 오류: {e}")
        return jsonify({'error': '백업 정리 중 오류가 발생했습니다'}), 500

@backup_bp.route('/health', methods=['GET'])
def health_check():
    """백업 시스템 상태 확인"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'backup_manager': 'active',
            'scheduler_running': backup_manager.is_running,
            'backup_dir': backup_manager.config.backup_dir
        }), 200
        
    except Exception as e:
        logger.error(f"상태 확인 오류: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500 