import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class CustomizationType(Enum):
    """커스터마이즈 타입"""
    OVERRIDE = "override"  # 완전 덮어쓰기
    EXTEND = "extend"      # 확장
    HIDE = "hide"          # 숨김
    OPTIONAL = "optional"  # 옵션화

@dataclass
class CustomizationRule:
    """커스터마이즈 규칙"""
    plugin_name: str
    target_type: str  # 'menu', 'route', 'config', 'field'
    target_path: str  # 대상 경로 (예: 'menus.0.title', 'config.auto_order')
    customization_type: CustomizationType
    value: Any
    conditions: Dict[str, Any]  # 적용 조건 (업종, 브랜드 등)
    created_at: str
    updated_at: str
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None

@dataclass
class CustomizationRequest:
    """커스터마이즈 요청"""
    id: str
    plugin_name: str
    rule: CustomizationRule
    requester: str
    request_reason: str
    status: str  # 'pending', 'approved', 'rejected'
    created_at: str
    updated_at: str
    reviewer: Optional[str] = None
    review_comment: Optional[str] = None

class PluginCustomizationManager:
    """플러그인 커스터마이즈 관리자"""
    
    def __init__(self, base_dir: str = "customizations"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # 커스터마이즈 파일 경로
        self.rules_file = self.base_dir / "rules.json"
        self.requests_file = self.base_dir / "requests.json"
        self.history_file = self.base_dir / "history.json"
        
        # 메모리 캐시
        self._rules_cache: List[CustomizationRule] = []
        self._requests_cache: List[CustomizationRequest] = []
        self._history_cache: List[Dict] = []
        
        # 초기 로드
        self._load_data()
    
    def _load_data(self):
        """데이터 로드"""
        # 규칙 로드
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    self._rules_cache = [CustomizationRule(**rule) for rule in rules_data]
            except Exception as e:
                print(f"규칙 로드 실패: {e}")
                self._rules_cache = []
        
        # 요청 로드
        if self.requests_file.exists():
            try:
                with open(self.requests_file, 'r', encoding='utf-8') as f:
                    requests_data = json.load(f)
                    self._requests_cache = [CustomizationRequest(**req) for req in requests_data]
            except Exception as e:
                print(f"요청 로드 실패: {e}")
                self._requests_cache = []
        
        # 히스토리 로드
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._history_cache = json.load(f)
            except Exception as e:
                print(f"히스토리 로드 실패: {e}")
                self._history_cache = []
    
    def _save_data(self):
        """데이터 저장"""
        # 규칙 저장
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(rule) for rule in self._rules_cache], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"규칙 저장 실패: {e}")
        
        # 요청 저장
        try:
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(req) for req in self._requests_cache], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"요청 저장 실패: {e}")
        
        # 히스토리 저장
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"히스토리 저장 실패: {e}")
    
    def _add_to_history(self, action: str, data: Dict):
        """히스토리에 추가"""
        history_entry = {
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self._history_cache.append(history_entry)
        
        # 히스토리 크기 제한 (최근 1000개)
        if len(self._history_cache) > 1000:
            self._history_cache = self._history_cache[-1000:]
    
    def create_customization_rule(self, rule: CustomizationRule) -> bool:
        """커스터마이즈 규칙 생성"""
        try:
            # 중복 검사
            existing_rule = self._find_existing_rule(rule)
            if existing_rule:
                return self.update_customization_rule(existing_rule, rule)
            
            self._rules_cache.append(rule)
            self._save_data()
            
            self._add_to_history("create_rule", asdict(rule))
            return True
            
        except Exception as e:
            print(f"규칙 생성 실패: {e}")
            return False
    
    def update_customization_rule(self, old_rule: CustomizationRule, new_rule: CustomizationRule) -> bool:
        """커스터마이즈 규칙 업데이트"""
        try:
            index = self._rules_cache.index(old_rule)
            self._rules_cache[index] = new_rule
            self._save_data()
            
            self._add_to_history("update_rule", {
                "old": asdict(old_rule),
                "new": asdict(new_rule)
            })
            return True
            
        except Exception as e:
            print(f"규칙 업데이트 실패: {e}")
            return False
    
    def delete_customization_rule(self, rule: CustomizationRule) -> bool:
        """커스터마이즈 규칙 삭제"""
        try:
            if rule in self._rules_cache:
                self._rules_cache.remove(rule)
                self._save_data()
                
                self._add_to_history("delete_rule", asdict(rule))
                return True
            return False
            
        except Exception as e:
            print(f"규칙 삭제 실패: {e}")
            return False
    
    def _find_existing_rule(self, rule: CustomizationRule) -> Optional[CustomizationRule]:
        """기존 규칙 찾기"""
        for existing_rule in self._rules_cache:
            if (existing_rule.plugin_name == rule.plugin_name and
                existing_rule.target_type == rule.target_type and
                existing_rule.target_path == rule.target_path):
                return existing_rule
        return None
    
    def get_customization_rules(self, 
                               plugin_name: Optional[str] = None,
                               target_type: Optional[str] = None,
                               conditions: Optional[Dict] = None) -> List[CustomizationRule]:
        """커스터마이즈 규칙 조회"""
        rules = self._rules_cache.copy()
        
        # 필터링
        if plugin_name:
            rules = [r for r in rules if r.plugin_name == plugin_name]
        
        if target_type:
            rules = [r for r in rules if r.target_type == target_type]
        
        if conditions:
            rules = [r for r in rules if self._check_conditions(r.conditions, conditions)]
        
        return rules
    
    def _check_conditions(self, rule_conditions: Dict, user_conditions: Dict) -> bool:
        """조건 검사"""
        for key, value in rule_conditions.items():
            if key not in user_conditions:
                return False
            if user_conditions[key] != value:
                return False
        return True
    
    def apply_customizations(self, plugin_config: Dict, 
                           industry: str, brand: str, 
                           branch: Optional[str] = None) -> Dict:
        """플러그인 설정에 커스터마이즈 적용"""
        customized_config = plugin_config.copy()
        conditions = {"industry": industry, "brand": brand}
        if branch:
            conditions["branch"] = branch
        
        # 승인된 규칙만 적용
        approved_rules = [r for r in self._rules_cache if r.approved]
        
        for rule in approved_rules:
            if not self._check_conditions(rule.conditions, conditions):
                continue
            
            try:
                customized_config = self._apply_rule(customized_config, rule)
            except Exception as e:
                print(f"규칙 적용 실패: {rule.target_path} - {e}")
        
        return customized_config
    
    def _apply_rule(self, config: Dict, rule: CustomizationRule) -> Dict:
        """개별 규칙 적용"""
        if rule.customization_type == CustomizationType.OVERRIDE:
            return self._apply_override(config, rule)
        elif rule.customization_type == CustomizationType.EXTEND:
            return self._apply_extend(config, rule)
        elif rule.customization_type == CustomizationType.HIDE:
            return self._apply_hide(config, rule)
        elif rule.customization_type == CustomizationType.OPTIONAL:
            return self._apply_optional(config, rule)
        
        return config
    
    def _apply_override(self, config: Dict, rule: CustomizationRule) -> Dict:
        """덮어쓰기 적용"""
        path_parts = rule.target_path.split('.')
        current = config
        
        # 경로 탐색
        for part in path_parts[:-1]:
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        
        # 값 설정
        last_part = path_parts[-1]
        if last_part.isdigit():
            current[int(last_part)] = rule.value
        else:
            current[last_part] = rule.value
        
        return config
    
    def _apply_extend(self, config: Dict, rule: CustomizationRule) -> Dict:
        """확장 적용"""
        path_parts = rule.target_path.split('.')
        current = config
        
        # 경로 탐색
        for part in path_parts[:-1]:
            if part.isdigit():
                current = current[int(part)]
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # 값 확장
        last_part = path_parts[-1]
        if isinstance(rule.value, dict) and isinstance(current.get(last_part), dict):
            current[last_part].update(rule.value)
        elif isinstance(rule.value, list) and isinstance(current.get(last_part), list):
            current[last_part].extend(rule.value)
        else:
            current[last_part] = rule.value
        
        return config
    
    def _apply_hide(self, config: Dict, rule: CustomizationRule) -> Dict:
        """숨김 적용"""
        path_parts = rule.target_path.split('.')
        current = config
        
        # 경로 탐색
        for part in path_parts[:-1]:
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        
        # 항목 제거
        last_part = path_parts[-1]
        if last_part.isdigit():
            current.pop(int(last_part), None)
        else:
            current.pop(last_part, None)
        
        return config
    
    def _apply_optional(self, config: Dict, rule: CustomizationRule) -> Dict:
        """옵션화 적용"""
        # 옵션화는 설정 스키마에 optional 플래그를 추가하는 방식
        path_parts = rule.target_path.split('.')
        current = config
        
        # 경로 탐색
        for part in path_parts[:-1]:
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        
        # optional 플래그 추가
        last_part = path_parts[-1]
        if last_part.isdigit():
            if isinstance(current[int(last_part)], dict):
                current[int(last_part)]['optional'] = True
        else:
            if isinstance(current.get(last_part), dict):
                current[last_part]['optional'] = True
        
        return config
    
    def create_customization_request(self, 
                                   plugin_name: str,
                                   rule: CustomizationRule,
                                   requester: str,
                                   request_reason: str) -> str:
        """커스터마이즈 요청 생성"""
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{plugin_name}"
        
        request = CustomizationRequest(
            id=request_id,
            plugin_name=plugin_name,
            rule=rule,
            requester=requester,
            request_reason=request_reason,
            status="pending",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self._requests_cache.append(request)
        self._save_data()
        
        self._add_to_history("create_request", asdict(request))
        return request_id
    
    def approve_customization_request(self, request_id: str, reviewer: str, comment: str = "") -> bool:
        """커스터마이즈 요청 승인"""
        request = self._find_request_by_id(request_id)
        if not request:
            return False
        
        request.status = "approved"
        request.reviewer = reviewer
        request.review_comment = comment
        request.updated_at = datetime.now().isoformat()
        
        # 규칙 승인
        request.rule.approved = True
        request.rule.approved_by = reviewer
        request.rule.approved_at = datetime.now().isoformat()
        
        # 규칙에 추가
        self._rules_cache.append(request.rule)
        
        self._save_data()
        
        self._add_to_history("approve_request", {
            "request_id": request_id,
            "reviewer": reviewer,
            "comment": comment
        })
        return True
    
    def reject_customization_request(self, request_id: str, reviewer: str, comment: str = "") -> bool:
        """커스터마이즈 요청 거부"""
        request = self._find_request_by_id(request_id)
        if not request:
            return False
        
        request.status = "rejected"
        request.reviewer = reviewer
        request.review_comment = comment
        request.updated_at = datetime.now().isoformat()
        
        self._save_data()
        
        self._add_to_history("reject_request", {
            "request_id": request_id,
            "reviewer": reviewer,
            "comment": comment
        })
        return True
    
    def _find_request_by_id(self, request_id: str) -> Optional[CustomizationRequest]:
        """요청 ID로 요청 찾기"""
        for request in self._requests_cache:
            if request.id == request_id:
                return request
        return None
    
    def get_customization_requests(self, 
                                 status: Optional[str] = None,
                                 plugin_name: Optional[str] = None) -> List[CustomizationRequest]:
        """커스터마이즈 요청 조회"""
        requests = self._requests_cache.copy()
        
        if status:
            requests = [r for r in requests if r.status == status]
        
        if plugin_name:
            requests = [r for r in requests if r.plugin_name == plugin_name]
        
        return requests
    
    def get_customization_history(self, 
                                action: Optional[str] = None,
                                limit: int = 100) -> List[Dict]:
        """커스터마이즈 히스토리 조회"""
        history = self._history_cache.copy()
        
        if action:
            history = [h for h in history if h["action"] == action]
        
        return history[-limit:] 