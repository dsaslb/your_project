import sqlite3
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify
args = None  # pyright: ignore
"""
고도화된 플러그인 보안 모니터링 API
- 취약점 스캔, 악성코드 감지, 권한 모니터링, 보안 이벤트 추적, 자동 대응
"""


try:
    from core.backend.enhanced_security_monitor import enhanced_security_monitor
except ImportError:
    enhanced_security_monitor = None

# SQLite import for database operations

logger = logging.getLogger(__name__)

enhanced_security_bp = Blueprint('enhanced_security', __name__, url_prefix='/api/enhanced-security')


@enhanced_security_bp.route('/scan/start', methods=['POST'])
@login_required
def start_security_scan():
    """보안 스캔 시작"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        data = request.get_json() or {}
        plugin_id = data.get('plugin_id') if data else None  # 특정 플러그인 또는 None (전체 스캔)

        if plugin_id:
            # 특정 플러그인 스캔
            results = enhanced_security_monitor.scan_plugin(plugin_id)
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_id} 보안 스캔이 완료되었습니다.',
                'data': results
            })
        else:
            # 전체 플러그인 스캔
            enhanced_security_monitor.scan_all_plugins()
            return jsonify({
                'success': True,
                'message': '전체 플러그인 보안 스캔이 시작되었습니다.'
            })

    except Exception as e:
        logger.error(f"보안 스캔 시작 오류: {e}")
        return jsonify({'success': False, 'message': f'보안 스캔 시작 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/monitoring/start', methods=['POST'])
@login_required
def start_monitoring():
    """보안 모니터링 시작"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        success = enhanced_security_monitor.start_monitoring()

        if success:
            return jsonify({'success': True, 'message': '보안 모니터링이 시작되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '보안 모니터링 시작에 실패했습니다.'}), 500

    except Exception as e:
        logger.error(f"보안 모니터링 시작 오류: {e}")
        return jsonify({'success': False, 'message': f'보안 모니터링 시작 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/monitoring/stop', methods=['POST'])
@login_required
def stop_monitoring():
    """보안 모니터링 중지"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        enhanced_security_monitor.stop_monitoring()
        return jsonify({'success': True, 'message': '보안 모니터링이 중지되었습니다.'})

    except Exception as e:
        logger.error(f"보안 모니터링 중지 오류: {e}")
        return jsonify({'success': False, 'message': f'보안 모니터링 중지 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    """취약점 목록 조회"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        import sqlite3

        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        # 쿼리 파라미터
        plugin_id = request.args.get('plugin_id')
        severity = request.args.get('severity')
        status = request.args.get('status', 'open')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 쿼리 조건 구성
        conditions = []
        params = []

        if plugin_id:
            conditions.append("plugin_id = ?")
            params.append(plugin_id)

        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f'''
            SELECT id, plugin_id, severity, title, description, cve_id, cvss_score,
                   affected_component, remediation, discovered_at, status, false_positive_reason
            FROM vulnerabilities
            WHERE {where_clause}
            ORDER BY discovered_at DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])

        rows = cursor.fetchall()
        vulnerabilities = []
        if rows is not None:
            for row in rows:
                vulnerability = {
                    'id': row[0] if row is not None else None,
                    'plugin_id': row[1] if row is not None else None,
                    'severity': row[2] if row is not None else None,
                    'title': row[3] if row is not None else None,
                    'description': row[4] if row is not None else None,
                    'cve_id': row[5] if row is not None else None,
                    'cvss_score': row[6] if row is not None else None,
                    'affected_component': row[7] if row is not None else None,
                    'remediation': row[8] if row is not None else None,
                    'discovered_at': row[9] if row is not None else None,
                    'status': row[10] if row is not None else None,
                    'false_positive_reason': row[11] if row is not None else None
                }
                vulnerabilities.append(vulnerability)

        conn.close()
        return jsonify({'success': True, 'data': vulnerabilities})

    except Exception as e:
        logger.error(f"취약점 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'취약점 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/malware', methods=['GET'])
def get_malware_detections():
    """악성코드 감지 목록 조회"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        import sqlite3

        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        # 쿼리 파라미터
        plugin_id = request.args.get('plugin_id')
        malware_type = request.args.get('malware_type')
        status = request.args.get('status', 'detected')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 쿼리 조건 구성
        conditions = []
        params = []

        if plugin_id:
            conditions.append("plugin_id = ?")
            params.append(plugin_id)

        if malware_type:
            conditions.append("malware_type = ?")
            params.append(malware_type)

        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f'''
            SELECT id, plugin_id, file_path, malware_type, signature, confidence,
                   description, detected_at, status
            FROM malware_detections
            WHERE {where_clause}
            ORDER BY detected_at DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])

        rows = cursor.fetchall()
        malware_detections = []
        if rows is not None:
            for row in rows:
                detection = {
                    'id': row[0] if row is not None else None,
                    'plugin_id': row[1] if row is not None else None,
                    'file_path': row[2] if row is not None else None,
                    'malware_type': row[3] if row is not None else None,
                    'signature': row[4] if row is not None else None,
                    'confidence': row[5] if row is not None else None,
                    'description': row[6] if row is not None else None,
                    'detected_at': row[7] if row is not None else None,
                    'status': row[8] if row is not None else None
                }
                malware_detections.append(detection)

        conn.close()
        return jsonify({'success': True, 'data': malware_detections})

    except Exception as e:
        logger.error(f"악성코드 감지 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'악성코드 감지 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/events', methods=['GET'])
def get_security_events():
    """보안 이벤트 목록 조회"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        import sqlite3

        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        # 쿼리 파라미터
        plugin_id = request.args.get('plugin_id')
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        resolved = request.args.get('resolved')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 쿼리 조건 구성
        conditions = []
        params = []

        if plugin_id:
            conditions.append("plugin_id = ?")
            params.append(plugin_id)

        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)

        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        if resolved is not None:
            conditions.append("resolved = ?")
            params.append(resolved == 'true')

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f'''
            SELECT id, plugin_id, event_type, severity, description, source_ip,
                   user_id, timestamp, resolved, resolution_notes
            FROM security_events
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])

        rows = cursor.fetchall()
        security_events = []
        if rows is not None:
            for row in rows:
                event = {
                    'id': row[0] if row is not None else None,
                    'plugin_id': row[1] if row is not None else None,
                    'event_type': row[2] if row is not None else None,
                    'severity': row[3] if row is not None else None,
                    'description': row[4] if row is not None else None,
                    'source_ip': row[5] if row is not None else None,
                    'user_id': row[6] if row is not None else None,
                    'timestamp': row[7] if row is not None else None,
                    'resolved': row[8] if row is not None else None,
                    'resolution_notes': row[9] if row is not None else None
                }
                security_events.append(event)

        conn.close()
        return jsonify({'success': True, 'data': security_events})

    except Exception as e:
        logger.error(f"보안 이벤트 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'보안 이벤트 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/profiles', methods=['GET'])
def get_security_profiles():
    """플러그인 보안 프로필 목록 조회"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        import sqlite3

        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        # 쿼리 파라미터
        plugin_id = request.args.get('plugin_id')
        risk_level = request.args.get('risk_level')
        compliance_status = request.args.get('compliance_status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 쿼리 조건 구성
        conditions = []
        params = []

        if plugin_id:
            conditions.append("plugin_id = ?")
            params.append(plugin_id)

        if risk_level:
            conditions.append("risk_level = ?")
            params.append(risk_level)

        if compliance_status:
            conditions.append("compliance_status = ?")
            params.append(compliance_status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f'''
            SELECT plugin_id, risk_level, last_scan, vulnerabilities_count, malware_count,
                   security_events_count, permissions, network_access, file_access, api_calls,
                   security_score, compliance_status
            FROM plugin_security_profiles
            WHERE {where_clause}
            ORDER BY security_score ASC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])

        rows = cursor.fetchall()
        profiles = []
        if rows is not None:
            for row in rows:
                profile = {
                    'plugin_id': row[0] if row is not None else None,
                    'risk_level': row[1] if row is not None else None,
                    'last_scan': row[2] if row is not None else None,
                    'vulnerabilities_count': row[3] if row is not None else None,
                    'malware_count': row[4] if row is not None else None,
                    'security_events_count': row[5] if row is not None else None,
                    'permissions': row[6] if row is not None else None,
                    'network_access': row[7] if row is not None else None,
                    'file_access': row[8] if row is not None else None,
                    'api_calls': row[9] if row is not None else None,
                    'security_score': row[10] if row is not None else None,
                    'compliance_status': row[11] if row is not None else None
                }
                profiles.append(profile)

        conn.close()
        return jsonify({'success': True, 'data': profiles})

    except Exception as e:
        logger.error(f"보안 프로필 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'보안 프로필 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/summary', methods=['GET'])
def get_security_summary():
    """보안 요약 정보 조회"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        summary = enhanced_security_monitor.get_security_summary()
        return jsonify({'success': True, 'data': summary})

    except Exception as e:
        logger.error(f"보안 요약 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'보안 요약 조회 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/vulnerabilities/<vuln_id>/status', methods=['PUT'])
@login_required
def update_vulnerability_status(vuln_id: str):
    """취약점 상태 업데이트"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        data = request.get_json()
        status = data.get('status') if data else None
        false_positive_reason = data.get('false_positive_reason', '') if data else None

        if not status:
            return jsonify({'success': False, 'message': '상태가 필요합니다.'}), 400

        import sqlite3
        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE vulnerabilities 
            SET status = ?, false_positive_reason = ?
            WHERE id = ?
        ''', (status, false_positive_reason, vuln_id))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': '취약점을 찾을 수 없습니다.'}), 404

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '취약점 상태가 업데이트되었습니다.'})

    except Exception as e:
        logger.error(f"취약점 상태 업데이트 오류: {e}")
        return jsonify({'success': False, 'message': f'취약점 상태 업데이트 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/malware/<detection_id>/quarantine', methods=['POST'])
@login_required
def quarantine_malware(detection_id: str):
    """악성코드 격리"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        import sqlite3
        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        # 악성코드 감지 정보 조회
        cursor.execute('SELECT file_path FROM malware_detections WHERE id = ?', (detection_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({'success': False, 'message': '악성코드 감지를 찾을 수 없습니다.'}), 404

        file_path = row[0] if row is not None else None

        # 파일 격리 (실제로는 안전한 격리 디렉토리로 이동)
        try:
            from pathlib import Path
            import shutil

            if file_path:
                source_path = Path(file_path)
                if source_path.exists():
                    # 격리 디렉토리 생성
                    quarantine_dir = Path("quarantine")
                    quarantine_dir.mkdir(exist_ok=True)

                    # 파일을 격리 디렉토리로 이동
                    quarantine_path = quarantine_dir / f"quarantined_{source_path.name}"
                    shutil.move(str(source_path), str(quarantine_path))

                    # 상태 업데이트
                    cursor.execute('''
                        UPDATE malware_detections 
                        SET status = 'quarantined'
                        WHERE id = ?
                    ''', (detection_id,))

                    conn.commit()
                    conn.close()

                    return jsonify({'success': True, 'message': '악성코드가 격리되었습니다.'})
                else:
                    conn.close()
                    return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'}), 404
            else:
                conn.close()
                return jsonify({'success': False, 'message': '파일 경로가 없습니다.'}), 404

        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': f'파일 격리 중 오류가 발생했습니다: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"악성코드 격리 오류: {e}")
        return jsonify({'success': False, 'message': f'악성코드 격리 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/events/<event_id>/resolve', methods=['POST'])
@login_required
def resolve_security_event(event_id: str):
    """보안 이벤트 해결"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        data = request.get_json() or {}
        resolution_notes = data.get('resolution_notes', '') if data else None

        import sqlite3
        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE security_events 
            SET resolved = TRUE, resolution_notes = ?
            WHERE id = ?
        ''', (resolution_notes, event_id))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': '보안 이벤트를 찾을 수 없습니다.'}), 404

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '보안 이벤트가 해결되었습니다.'})

    except Exception as e:
        logger.error(f"보안 이벤트 해결 오류: {e}")
        return jsonify({'success': False, 'message': f'보안 이벤트 해결 중 오류가 발생했습니다: {str(e)}'}), 500


@enhanced_security_bp.route('/scans', methods=['GET'])
def get_scan_history():
    """스캔 이력 조회"""
    if not enhanced_security_monitor:
        return jsonify({'success': False, 'message': '보안 모니터링 시스템을 사용할 수 없습니다.'}), 503

    try:
        import sqlite3

        conn = sqlite3.connect(enhanced_security_monitor.db_path)
        cursor = conn.cursor()

        # 쿼리 파라미터
        plugin_id = request.args.get('plugin_id')
        scan_type = request.args.get('scan_type')
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 쿼리 조건 구성
        conditions = []
        params = []

        if plugin_id:
            conditions.append("plugin_id = ?")
            params.append(plugin_id)

        if scan_type:
            conditions.append("scan_type = ?")
            params.append(scan_type)

        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f'''
            SELECT id, plugin_id, scan_type, started_at, completed_at, status,
                   findings_count, scan_duration
            FROM security_scans
            WHERE {where_clause}
            ORDER BY started_at DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])

        rows = cursor.fetchall()
        scans = []
        if rows is not None:
            for row in rows:
                scan = {
                    'id': row[0] if row is not None else None,
                    'plugin_id': row[1] if row is not None else None,
                    'scan_type': row[2] if row is not None else None,
                    'started_at': row[3] if row is not None else None,
                    'completed_at': row[4] if row is not None else None,
                    'status': row[5] if row is not None else None,
                    'findings_count': row[6] if row is not None else None,
                    'scan_duration': row[7] if row is not None else None
                }
                scans.append(scan)

        conn.close()
        return jsonify({'success': True, 'data': scans})

    except Exception as e:
        logger.error(f"스캔 이력 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'스캔 이력 조회 중 오류가 발생했습니다: {str(e)}'}), 500
