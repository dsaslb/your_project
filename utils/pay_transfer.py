import requests
import json
from datetime import datetime
from extensions import db
from models import User, ActionLog
from utils.logger import log_action

class BankTransferAPI:
    """은행 자동이체 API 클래스"""
    
    def __init__(self, api_url=None, api_key=None):
        self.api_url = api_url or "https://api.bank.example.com/transfer"
        self.api_key = api_key or "your-api-key"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def transfer_salary(self, user, amount, description=""):
        """급여 이체 실행"""
        try:
            payload = {
                "recipient_name": user.name or user.username,
                "account_number": getattr(user, 'account_number', '0000000000'),
                "bank_code": getattr(user, 'bank_code', '001'),
                "amount": amount,
                "description": description or f"{user.name or user.username} 급여",
                "transfer_date": datetime.now().strftime("%Y-%m-%d"),
                "reference_id": f"PAY_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # 실제 API 호출 (현재는 가상)
            # response = requests.post(self.api_url, json=payload, headers=self.headers)
            # return response.status_code == 200
            
            # 가상 이체 (테스트용)
            print(f"[가상이체] {payload}")
            
            # 이체 로그 기록
            self._log_transfer(user.id, amount, payload['reference_id'], "SUCCESS")
            
            return True, "이체 성공"
            
        except Exception as e:
            error_msg = f"이체 실패: {str(e)}"
            self._log_transfer(user.id, amount, "", "FAILED", error_msg)
            return False, error_msg
    
    def _log_transfer(self, user_id, amount, reference_id, status, error_msg=""):
        """이체 로그 기록"""
        try:
            action_log = ActionLog(
                user_id=user_id,
                action=f"SALARY_TRANSFER_{status}",
                message=f"급여 {amount:,}원 이체 - {reference_id} - {error_msg}".strip()
            )
            db.session.add(action_log)
            db.session.commit()
        except Exception as e:
            print(f"이체 로그 기록 실패: {e}")

def transfer_salary(user, amount):
    # 실제 서비스라면 여기에 은행 API 연동
    # 아래는 가상 REST API(POST 방식) 예시
    api_url = "https://yourbank.example.com/api/transfer"
    payload = {
        "name": user.name or user.username,
        "account": user.account_number,   # User 모델에 추가 필요
        "amount": amount,
    }
    # 예: 인증 토큰이 필요한 경우 headers에 추가
    # headers = {"Authorization": "Bearer ..."}
    # r = requests.post(api_url, json=payload, headers=headers)
    # 아래는 테스트용(실제 이체X)
    print(f"[가상이체] {payload}")
    return True

def bulk_transfer_salary(users_data):
    """일괄 급여 이체"""
    api = BankTransferAPI()
    results = []
    
    for user_data in users_data:
        user = user_data['user']
        amount = user_data['salary']
        description = user_data.get('description', '')
        
        success, message = api.transfer_salary(user, amount, description)
        results.append({
            'user_id': user.id,
            'user_name': user.name or user.username,
            'amount': amount,
            'success': success,
            'message': message
        })
    
    return results

def validate_bank_account(user):
    """계좌 정보 검증"""
    required_fields = ['account_number', 'bank_code']
    missing_fields = []
    
    for field in required_fields:
        if not hasattr(user, field) or not getattr(user, field):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"계좌 정보 누락: {', '.join(missing_fields)}"
    
    return True, "계좌 정보 유효"

def get_transfer_history(user_id, limit=10):
    """이체 이력 조회"""
    try:
        return ActionLog.query.filter(
            ActionLog.user_id == user_id,
            ActionLog.action.like('SALARY_TRANSFER_%')
        ).order_by(ActionLog.created_at.desc()).limit(limit).all()
    except Exception as e:
        print(f"이체 이력 조회 실패: {e}")
        return []

# 가상 은행 API 시뮬레이션
class MockBankAPI:
    """테스트용 가상 은행 API"""
    
    def __init__(self):
        self.transfers = []
    
    def transfer(self, payload):
        """가상 이체 실행"""
        transfer_id = f"TRANS_{len(self.transfers) + 1:06d}"
        
        transfer_record = {
            'id': transfer_id,
            'timestamp': datetime.now().isoformat(),
            'payload': payload,
            'status': 'SUCCESS'
        }
        
        self.transfers.append(transfer_record)
        return {
            'success': True,
            'transfer_id': transfer_id,
            'message': '이체가 성공적으로 처리되었습니다.'
        }
    
    def get_transfer_history(self):
        """이체 이력 조회"""
        return self.transfers

# 글로벌 가상 API 인스턴스
mock_api = MockBankAPI() 