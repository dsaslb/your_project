import logging
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sqlite3
import os
import json
from typing import Optional
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
계약 생성기 모듈
계약 템플릿 생성, 계약 관리, 계약 상태 추적 등의 기능을 제공합니다.
"""


# 로깅 설정
logger = logging.getLogger(__name__)


class ContractGenerator:
    """계약 생성 및 관리 시스템"""

    def __init__(self, db_path="data/contracts.db"):
        """계약 생성기 초기화"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """계약 데이터베이스 초기화"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 계약 템플릿 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contract_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        template_content TEXT NOT NULL,
                        variables TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 계약 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contracts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_id INTEGER,
                        contract_number TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        status TEXT DEFAULT 'draft',
                        parties TEXT,
                        start_date DATE,
                        end_date DATE,
                        created_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (template_id) REFERENCES contract_templates (id)
                    )
                ''')

                # 계약 변수 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contract_variables (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        contract_id INTEGER,
                        variable_name TEXT NOT NULL,
                        variable_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (contract_id) REFERENCES contracts (id)
                    )
                ''')

                # 계약 이력 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contract_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        contract_id INTEGER,
                        action TEXT NOT NULL,
                        description TEXT,
                        performed_by TEXT,
                        performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (contract_id) REFERENCES contracts (id)
                    )
                ''')

                conn.commit()

            # 기본 템플릿 생성
            self.create_default_templates()

            logger.info("계약 데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"계약 데이터베이스 초기화 실패: {e}")

    def create_default_templates(self):
        """기본 계약 템플릿 생성"""
        try:
            templates = [
                {
                    "name": "기본 고용 계약서",
                    "category": "employment",
                    "template_content": """
계약서

계약자: {employer_name}
피계약자: {employee_name}
계약기간: {start_date} ~ {end_date}

1. 근무 조건
   - 근무시간: {work_hours}
   - 급여: {salary}
   - 근무지: {work_location}

2. 의무사항
   - 성실한 근무 의무
   - 비밀유지 의무
   - 회사 규정 준수

3. 계약 해지
   - 사전 통지 기간: {notice_period}

계약자 서명: _________________
피계약자 서명: _________________
날짜: {contract_date}
                    """,
                    "variables": json.dumps([
                        "employer_name", "employee_name", "start_date", "end_date",
                        "work_hours", "salary", "work_location", "notice_period", "contract_date"
                    ])
                },
                {
                    "name": "서비스 제공 계약서",
                    "category": "service",
                    "template_content": """
서비스 제공 계약서

서비스 제공자: {provider_name}
서비스 수요자: {client_name}
계약기간: {start_date} ~ {end_date}

1. 서비스 내용
   - 서비스명: {service_name}
   - 서비스 범위: {service_scope}
   - 서비스 비용: {service_cost}

2. 서비스 제공 조건
   - 제공 방식: {delivery_method}
   - 품질 기준: {quality_standards}

3. 지급 조건
   - 지급 방식: {payment_method}
   - 지급 기한: {payment_terms}

서비스 제공자 서명: _________________
서비스 수요자 서명: _________________
날짜: {contract_date}
                    """,
                    "variables": json.dumps([
                        "provider_name", "client_name", "start_date", "end_date",
                        "service_name", "service_scope", "service_cost",
                        "delivery_method", "quality_standards", "payment_method", "payment_terms", "contract_date"
                    ])
                }
            ]

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if templates is not None:
                    for template in templates:
                        cursor.execute('''
                            INSERT OR IGNORE INTO contract_templates 
                            (name, category, template_content, variables)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            template["name"] if template is not None else None,
                            template["category"] if template is not None else None,
                            template["template_content"] if template is not None else None,
                            template["variables"] if template is not None else None
                        ))

                conn.commit()

            logger.info("기본 계약 템플릿 생성 완료")

        except Exception as e:
            logger.error(f"기본 템플릿 생성 실패: {e}")

    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """계약 템플릿 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if category:
                    cursor.execute('''
                        SELECT id, name, category, template_content, variables, created_at, updated_at
                        FROM contract_templates
                        WHERE category = ?
                        ORDER BY name
                    ''', (category,))
                else:
                    cursor.execute('''
                        SELECT id, name, category, template_content, variables, created_at, updated_at
                        FROM contract_templates
                        ORDER BY category, name
                    ''')

                templates = []
                for row in cursor.fetchall():
                    templates.append({
                        "id": row[0] if row is not None else None,
                        "name": row[1] if row is not None else None,
                        "category": row[2] if row is not None else None,
                        "template_content": row[3] if row is not None else None,
                        "variables": json.loads(row[4] if row is not None and row[4] is not None else '[]'),
                        "created_at": row[5] if row is not None else None,
                        "updated_at": row[6] if row is not None else None
                    })

                return templates

        except Exception as e:
            logger.error(f"템플릿 조회 실패: {e}")
            return []

    def create_template(self, name: str, category: str, template_content: str, variables: List[str]) -> bool:
        """새 계약 템플릿 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO contract_templates (name, category, template_content, variables)
                    VALUES (?, ?, ?, ?)
                ''', (name, category, template_content, json.dumps(variables)))

                conn.commit()
                logger.info(f"템플릿 생성 완료: {name}")
                return True

        except Exception as e:
            logger.error(f"템플릿 생성 실패: {e}")
            return False

    def generate_contract(self, template_id: int, variables: Dict[str, str], title: str) -> Optional[Dict[str, Any]]:
        """계약 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 템플릿 조회
                cursor.execute('''
                    SELECT template_content, variables
                    FROM contract_templates
                    WHERE id = ?
                ''', (template_id,))

                template_row = cursor.fetchone()
                if not template_row:
                    logger.error(f"템플릿을 찾을 수 없음: {template_id}")
                    return None

                template_content = template_row[0] if template_row is not None else None
                template_variables = json.loads(template_row[1] if template_row is not None and template_row[1] is not None else '[]')

                # 변수 치환
                content = template_content if template_content is not None else ''
                if variables is not None:
                    for var_name, var_value in variables.items():
                        content = content.replace(f"{{{var_name}}}", str(var_value))

                # 계약 번호 생성
                contract_number = f"CONTRACT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

                # 계약 저장
                cursor.execute('''
                    INSERT INTO contracts (template_id, contract_number, title, content, parties, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    template_id,
                    contract_number,
                    title,
                    content,
                    json.dumps(variables.get('parties', {}) if variables else {}),
                    variables.get('created_by', 'system') if variables else 'system'
                ))

                contract_id = cursor.lastrowid

                # 변수 저장
                if variables is not None:
                    for var_name, var_value in variables.items():
                        cursor.execute('''
                            INSERT INTO contract_variables (contract_id, variable_name, variable_value)
                            VALUES (?, ?, ?)
                        ''', (contract_id, var_name, str(var_value)))

                # 이력 저장
                cursor.execute('''
                    INSERT INTO contract_history (contract_id, action, description, performed_by)
                    VALUES (?, ?, ?, ?)
                ''', (contract_id, "생성", "계약 생성", variables.get('created_by', 'system') if variables else 'system'))

                conn.commit()

                logger.info(f"계약 생성 완료: {contract_number}")

                return {
                    "id": contract_id,
                    "contract_number": contract_number,
                    "title": title,
                    "content": content,
                    "status": "draft"
                }

        except Exception as e:
            logger.error(f"계약 생성 실패: {e}")
            return None

    def get_contracts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """계약 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if status:
                    cursor.execute('''
                        SELECT id, contract_number, title, status, created_at, updated_at
                        FROM contracts
                        WHERE status = ?
                        ORDER BY created_at DESC
                    ''', (status,))
                else:
                    cursor.execute('''
                        SELECT id, contract_number, title, status, created_at, updated_at
                        FROM contracts
                        ORDER BY created_at DESC
                    ''')

                contracts = []
                for row in cursor.fetchall():
                    contracts.append({
                        "id": row[0] if row is not None else None,
                        "contract_number": row[1] if row is not None else None,
                        "title": row[2] if row is not None else None,
                        "status": row[3] if row is not None else None,
                        "created_at": row[4] if row is not None else None,
                        "updated_at": row[5] if row is not None else None
                    })

                return contracts

        except Exception as e:
            logger.error(f"계약 조회 실패: {e}")
            return []

    def get_contract(self,  contract_id: int) -> Optional[Dict[str, Any]]:
        """계약 상세 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT id, contract_number, title, content, status, parties, 
                           start_date, end_date, created_by, created_at, updated_at
                    FROM contracts
                    WHERE id = ?
                ''', (contract_id,))

                contract_row = cursor.fetchone()
                if not contract_row:
                    return None

                # 변수 조회
                cursor.execute('''
                    SELECT variable_name, variable_value
                    FROM contract_variables
                    WHERE contract_id = ?
                ''', (contract_id,))

                variables = {}
                for var_row in cursor.fetchall():
                    variables[var_row[0] if variables is not None else None] = var_row[1] if var_row is not None else None

                # 이력 조회
                cursor.execute('''
                    SELECT action, description, performed_by, performed_at
                    FROM contract_history
                    WHERE contract_id = ?
                    ORDER BY performed_at DESC
                ''', (contract_id,))

                history = []
                for hist_row in cursor.fetchall():
                    history.append({
                        "action": hist_row[0] if hist_row is not None else None,
                        "description": hist_row[1] if hist_row is not None else None,
                        "performed_by": hist_row[2] if hist_row is not None else None,
                        "performed_at": hist_row[3] if hist_row is not None else None
                    })

                return {
                    "id": contract_row[0] if contract_row is not None else None,
                    "contract_number": contract_row[1] if contract_row is not None else None,
                    "title": contract_row[2] if contract_row is not None else None,
                    "content": contract_row[3] if contract_row is not None else None,
                    "status": contract_row[4] if contract_row is not None else None,
                    "parties": json.loads(contract_row[5] if contract_row is not None and contract_row[5] is not None else '{}'),
                    "start_date": contract_row[6] if contract_row is not None else None,
                    "end_date": contract_row[7] if contract_row is not None else None,
                    "created_by": contract_row[8] if contract_row is not None else None,
                    "created_at": contract_row[9] if contract_row is not None else None,
                    "updated_at": contract_row[10] if contract_row is not None else None,
                    "variables": variables,
                    "history": history
                }

        except Exception as e:
            logger.error(f"계약 상세 조회 실패: {e}")
            return None

    def update_contract_status(self,  contract_id: int,  status: str,  updated_by: str) -> bool:
        """계약 상태 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE contracts
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, contract_id))

                # 이력 저장
                cursor.execute('''
                    INSERT INTO contract_history (contract_id, action, description, performed_by)
                    VALUES (?, ?, ?, ?)
                ''', (contract_id, "상태변경", f"상태를 {status}로 변경", updated_by))

                conn.commit()

                logger.info(f"계약 상태 업데이트 완료: {contract_id} -> {status}")
                return True

        except Exception as e:
            logger.error(f"계약 상태 업데이트 실패: {e}")
            return False


# Flask Blueprint 생성
contract_generator_bp = Blueprint('contract_generator', __name__)

# 전역 인스턴스
contract_generator = ContractGenerator()

# API 라우트


@contract_generator_bp.route('/api/contracts/templates', methods=['GET'])
def get_templates_api():
    """계약 템플릿 목록 API"""
    try:
        category = request.args.get('category')
        templates = contract_generator.get_templates(category)

        return jsonify({
            "success": True,
            "data": templates
        })
    except Exception as e:
        logger.error(f"템플릿 목록 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@contract_generator_bp.route('/api/contracts/templates', methods=['POST'])
def create_template_api():
    """계약 템플릿 생성 API"""
    try:
        data = request.get_json()

        required_fields = ['name', 'category', 'template_content', 'variables']
        if required_fields is not None:
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"필수 필드 누락: {field}"
                    }), 400

        success = contract_generator.create_template(
            data['name'] if data is not None else None,
            data['category'] if data is not None else None,
            data['template_content'] if data is not None else None,
            data['variables'] if data is not None else None
        )

        if success:
            return jsonify({
                "success": True,
                "message": "템플릿이 생성되었습니다."
            })
        else:
            return jsonify({
                "success": False,
                "error": "템플릿 생성에 실패했습니다."
            }), 500

    except Exception as e:
        logger.error(f"템플릿 생성 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@contract_generator_bp.route('/api/contracts/generate', methods=['POST'])
def generate_contract_api():
    """계약 생성 API"""
    try:
        data = request.get_json()

        required_fields = ['template_id', 'variables', 'title']
        if required_fields is not None:
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"필수 필드 누락: {field}"
                    }), 400

        contract = contract_generator.generate_contract(
            data['template_id'] if data is not None else None,
            data['variables'] if data is not None else None,
            data['title'] if data is not None else None
        )

        if contract:
            return jsonify({
                "success": True,
                "data": contract
            })
        else:
            return jsonify({
                "success": False,
                "error": "계약 생성에 실패했습니다."
            }), 500

    except Exception as e:
        logger.error(f"계약 생성 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@contract_generator_bp.route('/api/contracts', methods=['GET'])
def get_contracts_api():
    """계약 목록 API"""
    try:
        status = request.args.get('status')
        contracts = contract_generator.get_contracts(status)

        return jsonify({
            "success": True,
            "data": contracts
        })
    except Exception as e:
        logger.error(f"계약 목록 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@contract_generator_bp.route('/api/contracts/<int:contract_id>', methods=['GET'])
def get_contract_api(contract_id):
    """계약 상세 API"""
    try:
        contract = contract_generator.get_contract(contract_id)

        if contract:
            return jsonify({
                "success": True,
                "data": contract
            })
        else:
            return jsonify({
                "success": False,
                "error": "계약을 찾을 수 없습니다."
            }), 404

    except Exception as e:
        logger.error(f"계약 상세 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@contract_generator_bp.route('/api/contracts/<int:contract_id>/status', methods=['PUT'])
def update_contract_status_api(contract_id):
    """계약 상태 업데이트 API"""
    try:
        data = request.get_json()

        if 'status' not in data:
            return jsonify({
                "success": False,
                "error": "상태 정보가 필요합니다."
            }), 400

        updated_by = data.get('updated_by', 'system') if data else 'system'

        success = contract_generator.update_contract_status(
            contract_id,
            str(data['status']) if data and 'status' in data else '',
            updated_by
        )

        if success:
            return jsonify({
                "success": True,
                "message": "계약 상태가 업데이트되었습니다."
            })
        else:
            return jsonify({
                "success": False,
                "error": "계약 상태 업데이트에 실패했습니다."
            }), 500

    except Exception as e:
        logger.error(f"계약 상태 업데이트 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@contract_generator_bp.route('/api/contracts/statistics', methods=['GET'])
def get_contract_statistics_api():
    """계약 통계 API"""
    try:
        with sqlite3.connect(contract_generator.db_path) as conn:
            cursor = conn.cursor()

            # 전체 계약 수
            cursor.execute('SELECT COUNT(*) FROM contracts')
            total_contracts = cursor.fetchone()[0]

            # 상태별 계약 수
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM contracts 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())

            # 카테고리별 템플릿 수
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM contract_templates 
                GROUP BY category
            ''')
            category_counts = dict(cursor.fetchall())

            # 최근 생성된 계약
            cursor.execute('''
                SELECT COUNT(*) 
                FROM contracts 
                WHERE created_at >= date('now', '-7 days')
            ''')
            recent_contracts = cursor.fetchone()[0]

            return jsonify({
                "success": True,
                "data": {
                    "total_contracts": total_contracts,
                    "status_counts": status_counts,
                    "category_counts": category_counts,
                    "recent_contracts": recent_contracts
                }
            })

    except Exception as e:
        logger.error(f"계약 통계 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
