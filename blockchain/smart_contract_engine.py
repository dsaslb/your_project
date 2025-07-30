"""
스마트 컨트랙트 엔진
Turing 완전한 스마트 컨트랙트 실행 환경, 가상 머신, 가스 시스템을 포함한 완전한 스마트 컨트랙트 플랫폼
"""

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import ast
import inspect
import sys
import traceback
from pathlib import Path
import sqlite3
import pickle
import hashlib
import secrets
from collections import defaultdict, deque

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractType(Enum):
    """컨트랙트 타입"""
    TOKEN = "token"
    NFT = "nft"
    DEFI = "defi"
    GOVERNANCE = "governance"
    ORACLE = "oracle"
    CUSTOM = "custom"

class ExecutionStatus(Enum):
    """실행 상태"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERTED = "reverted"

class GasType(Enum):
    """가스 타입"""
    COMPUTATION = "computation"
    STORAGE = "storage"
    MEMORY = "memory"
    NETWORK = "network"

@dataclass
class ContractState:
    """컨트랙트 상태"""
    contract_id: str
    variables: Dict[str, Any]
    mappings: Dict[str, Dict[str, Any]]
    arrays: Dict[str, List[Any]]
    events: List[Dict[str, Any]]
    last_updated: datetime

@dataclass
class ContractExecution:
    """컨트랙트 실행"""
    execution_id: str
    contract_id: str
    function_name: str
    parameters: Dict[str, Any]
    caller: str
    gas_used: int
    gas_limit: int
    execution_time: float
    status: ExecutionStatus
    result: Any
    error_message: str
    timestamp: datetime

@dataclass
class GasCost:
    """가스 비용"""
    operation: str
    cost: int
    gas_type: GasType
    description: str

class SmartContractEngine:
    """스마트 컨트랙트 엔진"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.contracts: Dict[str, SmartContract] = {}
        self.contract_states: Dict[str, ContractState] = {}
        self.executions: Dict[str, ContractExecution] = {}
        self.gas_costs: Dict[str, GasCost] = {}
        self.execution_queue = asyncio.Queue()
        self.is_running = False
        
        # 가상 머신 관련
        self.vm_memory: Dict[str, Any] = {}
        self.vm_stack: deque = deque()
        self.vm_registers: Dict[str, Any] = {}
        
        # 가스 시스템
        self._init_gas_costs()
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './smart_contracts.db'))
        self._init_database()
        
        # 기본 컨트랙트 템플릿
        self._load_contract_templates()
        
        logger.info("스마트 컨트랙트 엔진 초기화 완료")
    
    def _init_gas_costs(self):
        """가스 비용 초기화"""
        self.gas_costs = {
            # 기본 연산
            'ADD': GasCost('ADD', 3, GasType.COMPUTATION, '덧셈 연산'),
            'SUB': GasCost('SUB', 3, GasType.COMPUTATION, '뺄셈 연산'),
            'MUL': GasCost('MUL', 5, GasType.COMPUTATION, '곱셈 연산'),
            'DIV': GasCost('DIV', 5, GasType.COMPUTATION, '나눗셈 연산'),
            'MOD': GasCost('MOD', 5, GasType.COMPUTATION, '나머지 연산'),
            
            # 비교 연산
            'EQ': GasCost('EQ', 3, GasType.COMPUTATION, '같음 비교'),
            'LT': GasCost('LT', 3, GasType.COMPUTATION, '작음 비교'),
            'GT': GasCost('GT', 3, GasType.COMPUTATION, '큼 비교'),
            'LTE': GasCost('LTE', 3, GasType.COMPUTATION, '작거나 같음 비교'),
            'GTE': GasCost('GTE', 3, GasType.COMPUTATION, '크거나 같음 비교'),
            
            # 논리 연산
            'AND': GasCost('AND', 3, GasType.COMPUTATION, '논리 AND'),
            'OR': GasCost('OR', 3, GasType.COMPUTATION, '논리 OR'),
            'NOT': GasCost('NOT', 3, GasType.COMPUTATION, '논리 NOT'),
            
            # 메모리 연산
            'LOAD': GasCost('LOAD', 3, GasType.MEMORY, '메모리 로드'),
            'STORE': GasCost('STORE', 5, GasType.MEMORY, '메모리 저장'),
            'PUSH': GasCost('PUSH', 3, GasType.MEMORY, '스택 푸시'),
            'POP': GasCost('POP', 2, GasType.MEMORY, '스택 팝'),
            
            # 저장소 연산
            'SLOAD': GasCost('SLOAD', 200, GasType.STORAGE, '저장소 읽기'),
            'SSTORE': GasCost('SSTORE', 5000, GasType.STORAGE, '저장소 쓰기'),
            
            # 함수 호출
            'CALL': GasCost('CALL', 2600, GasType.COMPUTATION, '함수 호출'),
            'RETURN': GasCost('RETURN', 0, GasType.COMPUTATION, '함수 반환'),
            
            # 조건문
            'IF': GasCost('IF', 3, GasType.COMPUTATION, '조건문'),
            'ELSE': GasCost('ELSE', 3, GasType.COMPUTATION, 'else 문'),
            'LOOP': GasCost('LOOP', 3, GasType.COMPUTATION, '반복문'),
            
            # 이벤트
            'EMIT': GasCost('EMIT', 375, GasType.NETWORK, '이벤트 발생'),
            
            # 암호화
            'SHA256': GasCost('SHA256', 60, GasType.COMPUTATION, 'SHA256 해시'),
            'KECCAK256': GasCost('KECCAK256', 30, GasType.COMPUTATION, 'Keccak256 해시'),
        }
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 컨트랙트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contracts (
                    contract_id TEXT PRIMARY KEY,
                    name TEXT,
                    code TEXT,
                    owner TEXT,
                    address TEXT,
                    balance REAL,
                    contract_type TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 컨트랙트 상태 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contract_states (
                    contract_id TEXT PRIMARY KEY,
                    variables TEXT,
                    mappings TEXT,
                    arrays TEXT,
                    events TEXT,
                    last_updated TEXT,
                    FOREIGN KEY (contract_id) REFERENCES contracts (contract_id)
                )
            ''')
            
            # 실행 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    contract_id TEXT,
                    function_name TEXT,
                    parameters TEXT,
                    caller TEXT,
                    gas_used INTEGER,
                    gas_limit INTEGER,
                    execution_time REAL,
                    status TEXT,
                    result TEXT,
                    error_message TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (contract_id) REFERENCES contracts (contract_id)
                )
            ''')
            
            # 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    contract_id TEXT,
                    event_name TEXT,
                    event_data TEXT,
                    block_number INTEGER,
                    transaction_hash TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (contract_id) REFERENCES contracts (contract_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("스마트 컨트랙트 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_contract_templates(self):
        """컨트랙트 템플릿 로드"""
        self.contract_templates = {
            'token': self._get_token_template(),
            'nft': self._get_nft_template(),
            'defi': self._get_defi_template(),
            'governance': self._get_governance_template(),
            'oracle': self._get_oracle_template()
        }
    
    def _get_token_template(self) -> str:
        """토큰 컨트랙트 템플릿"""
        return '''
class TokenContract:
    def __init__(self):
        self.name = "MyToken"
        self.symbol = "MTK"
        self.decimals = 18
        self.total_supply = 1000000 * (10 ** 18)
        self.balances = {}
        self.allowances = {}
        self.owner = msg.sender
        
    def transfer(self, to, amount):
        require(self.balances[msg.sender] >= amount, "Insufficient balance")
        require(to != address(0), "Invalid recipient")
        
        self.balances[msg.sender] -= amount
        self.balances[to] += amount
        
        emit Transfer(msg.sender, to, amount)
        return True
        
    def approve(self, spender, amount):
        self.allowances[msg.sender][spender] = amount
        emit Approval(msg.sender, spender, amount)
        return True
        
    def transferFrom(self, from_addr, to, amount):
        require(self.balances[from_addr] >= amount, "Insufficient balance")
        require(self.allowances[from_addr][msg.sender] >= amount, "Insufficient allowance")
        
        self.balances[from_addr] -= amount
        self.balances[to] += amount
        self.allowances[from_addr][msg.sender] -= amount
        
        emit Transfer(from_addr, to, amount)
        return True
        
    def balanceOf(self, account):
        return self.balances.get(account, 0)
        
    def allowance(self, owner, spender):
        return self.allowances.get(owner, {}).get(spender, 0)
'''
    
    def _get_nft_template(self) -> str:
        """NFT 컨트랙트 템플릿"""
        return '''
class NFTContract:
    def __init__(self):
        self.name = "MyNFT"
        self.symbol = "MNFT"
        self.token_counter = 0
        self.tokens = {}
        self.owners = {}
        self.approvals = {}
        
    def mint(self, to, token_uri):
        self.token_counter += 1
        token_id = self.token_counter
        
        self.tokens[token_id] = {
            'owner': to,
            'token_uri': token_uri,
            'created_at': block.timestamp
        }
        self.owners[token_id] = to
        
        emit Transfer(address(0), to, token_id)
        return token_id
        
    def transfer(self, from_addr, to, token_id):
        require(self.owners[token_id] == from_addr, "Not owner")
        require(to != address(0), "Invalid recipient")
        
        self.owners[token_id] = to
        self.tokens[token_id]['owner'] = to
        
        emit Transfer(from_addr, to, token_id)
        
    def ownerOf(self, token_id):
        return self.owners[token_id]
        
    def tokenURI(self, token_id):
        return self.tokens[token_id]['token_uri']
'''
    
    def _get_defi_template(self) -> str:
        """DeFi 컨트랙트 템플릿"""
        return '''
class DeFiContract:
    def __init__(self):
        self.total_liquidity = 0
        self.reserves = {'token_a': 0, 'token_b': 0}
        self.liquidity_providers = {}
        self.fee_rate = 0.003  # 0.3%
        
    def addLiquidity(self, token_a_amount, token_b_amount):
        if self.total_liquidity == 0:
            liquidity = sqrt(token_a_amount * token_b_amount)
        else:
            liquidity = min(
                token_a_amount * self.total_liquidity / self.reserves['token_a'],
                token_b_amount * self.total_liquidity / self.reserves['token_b']
            )
        
        self.reserves['token_a'] += token_a_amount
        self.reserves['token_b'] += token_b_amount
        self.total_liquidity += liquidity
        self.liquidity_providers[msg.sender] = liquidity
        
        emit LiquidityAdded(msg.sender, token_a_amount, token_b_amount, liquidity)
        return liquidity
        
    def swap(self, token_in, amount_in, token_out):
        amount_out = self.getAmountOut(amount_in, token_in, token_out)
        
        self.reserves[token_in] += amount_in
        self.reserves[token_out] -= amount_out
        
        emit Swap(msg.sender, token_in, amount_in, token_out, amount_out)
        return amount_out
        
    def getAmountOut(self, amount_in, token_in, token_out):
        reserve_in = self.reserves[token_in]
        reserve_out = self.reserves[token_out]
        
        amount_in_with_fee = amount_in * (1 - self.fee_rate)
        amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)
        return amount_out
'''
    
    def _get_governance_template(self) -> str:
        """거버넌스 컨트랙트 템플릿"""
        return '''
class GovernanceContract:
    def __init__(self):
        self.proposals = {}
        self.votes = {}
        self.proposal_counter = 0
        self.voting_period = 7 * 24 * 3600  # 7일
        self.quorum = 1000  # 최소 투표 수
        
    def createProposal(self, description, actions):
        self.proposal_counter += 1
        proposal_id = self.proposal_counter
        
        self.proposals[proposal_id] = {
            'description': description,
            'actions': actions,
            'created_at': block.timestamp,
            'end_time': block.timestamp + self.voting_period,
            'creator': msg.sender,
            'for_votes': 0,
            'against_votes': 0,
            'executed': False
        }
        
        emit ProposalCreated(proposal_id, description, msg.sender)
        return proposal_id
        
    def vote(self, proposal_id, support):
        proposal = self.proposals[proposal_id]
        require(block.timestamp < proposal['end_time'], "Voting period ended")
        require(not self.votes.get(proposal_id, {}).get(msg.sender), "Already voted")
        
        weight = self.getVotingPower(msg.sender)
        if support:
            proposal['for_votes'] += weight
        else:
            proposal['against_votes'] += weight
            
        self.votes[proposal_id] = self.votes.get(proposal_id, {})
        self.votes[proposal_id][msg.sender] = support
        
        emit Voted(proposal_id, msg.sender, support, weight)
        
    def executeProposal(self, proposal_id):
        proposal = self.proposals[proposal_id]
        require(block.timestamp >= proposal['end_time'], "Voting period not ended")
        require(not proposal['executed'], "Already executed")
        require(proposal['for_votes'] > proposal['against_votes'], "Proposal failed")
        require(proposal['for_votes'] + proposal['against_votes'] >= self.quorum, "Quorum not met")
        
        # 제안 실행
        for action in proposal['actions']:
            self._executeAction(action)
        
        proposal['executed'] = True
        emit ProposalExecuted(proposal_id)
'''
    
    def _get_oracle_template(self) -> str:
        """오라클 컨트랙트 템플릿"""
        return '''
class OracleContract:
    def __init__(self):
        self.data = {}
        self.oracles = {}
        self.min_oracles = 3
        self.request_counter = 0
        self.requests = {}
        
    def addOracle(self, oracle_address):
        require(msg.sender == self.owner, "Only owner can add oracle")
        self.oracles[oracle_address] = True
        emit OracleAdded(oracle_address)
        
    def requestData(self, query):
        self.request_counter += 1
        request_id = self.request_counter
        
        self.requests[request_id] = {
            'query': query,
            'responses': {},
            'created_at': block.timestamp,
            'fulfilled': False
        }
        
        emit DataRequested(request_id, query, msg.sender)
        return request_id
        
    def submitData(self, request_id, data):
        require(self.oracles[msg.sender], "Not authorized oracle")
        require(not self.requests[request_id]['fulfilled'], "Request already fulfilled")
        
        self.requests[request_id]['responses'][msg.sender] = data
        
        # 충분한 응답이 있으면 집계
        if len(self.requests[request_id]['responses']) >= self.min_oracles:
            aggregated_data = self._aggregateData(request_id)
            self.data[request_id] = aggregated_data
            self.requests[request_id]['fulfilled'] = True
            
            emit DataFulfilled(request_id, aggregated_data)
            
    def getData(self, request_id):
        require(self.requests[request_id]['fulfilled'], "Data not available")
        return self.data[request_id]
        
    def _aggregateData(self, request_id):
        responses = list(self.requests[request_id]['responses'].values())
        # 간단한 평균 집계 (실제로는 더 복잡한 로직 필요)
        return sum(responses) / len(responses)
'''
    
    def deploy_contract(self, name: str, code: str, owner: str, 
                       contract_type: ContractType = ContractType.CUSTOM) -> str:
        """컨트랙트 배포"""
        try:
            contract_id = str(uuid.uuid4())
            contract_address = hashlib.sha256(contract_id.encode()).hexdigest()[:40]
            
            # 코드 검증
            if not self._validate_contract_code(code):
                raise ValueError("컨트랙트 코드가 유효하지 않습니다")
            
            # 컨트랙트 생성
            contract = SmartContract(
                contract_id=contract_id,
                name=name,
                code=code,
                owner=owner,
                address=contract_address,
                balance=0.0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.contracts[contract_id] = contract
            
            # 초기 상태 생성
            initial_state = ContractState(
                contract_id=contract_id,
                variables={},
                mappings={},
                arrays={},
                events=[],
                last_updated=datetime.now()
            )
            
            self.contract_states[contract_id] = initial_state
            
            # 데이터베이스에 저장
            self._save_contract_to_db(contract, initial_state)
            
            logger.info(f"컨트랙트 배포 완료: {contract_id}")
            return contract_id
            
        except Exception as e:
            logger.error(f"컨트랙트 배포 오류: {e}")
            raise
    
    def _validate_contract_code(self, code: str) -> bool:
        """컨트랙트 코드 검증"""
        try:
            # Python 문법 검증
            ast.parse(code)
            
            # 위험한 함수 검사
            dangerous_functions = ['eval', 'exec', 'open', 'file', 'input', 'raw_input']
            for func in dangerous_functions:
                if func in code:
                    logger.warning(f"위험한 함수 사용: {func}")
                    return False
            
            return True
            
        except SyntaxError as e:
            logger.error(f"컨트랙트 코드 문법 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"컨트랙트 코드 검증 오류: {e}")
            return False
    
    async def execute_contract_function(self, contract_id: str, function_name: str, 
                                      parameters: Dict[str, Any], caller: str, 
                                      gas_limit: int = 1000000) -> ContractExecution:
        """컨트랙트 함수 실행"""
        try:
            execution_id = str(uuid.uuid4())
            
            # 컨트랙트 확인
            if contract_id not in self.contracts:
                raise ValueError(f"컨트랙트를 찾을 수 없습니다: {contract_id}")
            
            contract = self.contracts[contract_id]
            contract_state = self.contract_states[contract_id]
            
            # 실행 기록 생성
            execution = ContractExecution(
                execution_id=execution_id,
                contract_id=contract_id,
                function_name=function_name,
                parameters=parameters,
                caller=caller,
                gas_used=0,
                gas_limit=gas_limit,
                execution_time=0.0,
                status=ExecutionStatus.EXECUTING,
                result=None,
                error_message="",
                timestamp=datetime.now()
            )
            
            start_time = time.time()
            
            try:
                # 가상 머신 초기화
                self._init_vm(contract, contract_state, caller, parameters)
                
                # 함수 실행
                result = await self._execute_function(contract, function_name, parameters, gas_limit)
                
                execution.status = ExecutionStatus.COMPLETED
                execution.result = result
                
            except Exception as e:
                execution.status = ExecutionStatus.FAILED
                execution.error_message = str(e)
                logger.error(f"컨트랙트 실행 오류: {e}")
            
            execution.execution_time = time.time() - start_time
            
            # 실행 기록 저장
            self.executions[execution_id] = execution
            self._save_execution_to_db(execution)
            
            # 상태 업데이트
            contract_state.last_updated = datetime.now()
            self._save_contract_state_to_db(contract_state)
            
            logger.info(f"컨트랙트 함수 실행 완료: {execution_id}")
            return execution
            
        except Exception as e:
            logger.error(f"컨트랙트 함수 실행 오류: {e}")
            raise
    
    def _init_vm(self, contract: SmartContract, contract_state: ContractState, 
                caller: str, parameters: Dict[str, Any]):
        """가상 머신 초기화"""
        try:
            # 메모리 초기화
            self.vm_memory = {
                'contract': contract,
                'state': contract_state,
                'caller': caller,
                'parameters': parameters,
                'block': {
                    'timestamp': int(time.time()),
                    'number': len(self.chain) if hasattr(self, 'chain') else 0
                },
                'msg': {
                    'sender': caller,
                    'value': parameters.get('value', 0)
                }
            }
            
            # 스택 초기화
            self.vm_stack.clear()
            
            # 레지스터 초기화
            self.vm_registers = {
                'pc': 0,  # 프로그램 카운터
                'gas': 0,  # 가스 사용량
                'memory': {},  # 임시 메모리
                'storage': contract_state.variables  # 영구 저장소
            }
            
        except Exception as e:
            logger.error(f"가상 머신 초기화 오류: {e}")
            raise
    
    async def _execute_function(self, contract: SmartContract, function_name: str, 
                              parameters: Dict[str, Any], gas_limit: int) -> Any:
        """함수 실행"""
        try:
            # 컨트랙트 코드 컴파일
            compiled_code = self._compile_contract_code(contract.code)
            
            # 함수 찾기
            if function_name not in compiled_code:
                raise ValueError(f"함수를 찾을 수 없습니다: {function_name}")
            
            # 함수 실행
            result = await self._execute_compiled_function(compiled_code[function_name], parameters, gas_limit)
            
            return result
            
        except Exception as e:
            logger.error(f"함수 실행 오류: {e}")
            raise
    
    def _compile_contract_code(self, code: str) -> Dict[str, Callable]:
        """컨트랙트 코드 컴파일"""
        try:
            # 안전한 실행 환경 생성
            safe_globals = {
                '__builtins__': {
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'min': min,
                    'max': max,
                    'sum': sum,
                    'abs': abs,
                    'round': round,
                    'hash': hash,
                    'id': id,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                    'delattr': delattr,
                    'callable': callable,
                    'issubclass': issubclass,
                    'super': super,
                    'property': property,
                    'staticmethod': staticmethod,
                    'classmethod': classmethod,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'reversed': reversed,
                    'sorted': sorted,
                    'any': any,
                    'all': all,
                    'range': range,
                    'print': lambda *args: None,  # 무시
                }
            }
            
            # 컨트랙트 클래스 정의
            exec(code, safe_globals)
            
            # 컨트랙트 인스턴스 생성
            contract_class = None
            for name, obj in safe_globals.items():
                if isinstance(obj, type) and name.endswith('Contract'):
                    contract_class = obj
                    break
            
            if not contract_class:
                raise ValueError("컨트랙트 클래스를 찾을 수 없습니다")
            
            # 인스턴스 생성
            contract_instance = contract_class()
            
            # 함수들 추출
            functions = {}
            for name, method in inspect.getmembers(contract_instance, inspect.ismethod):
                if not name.startswith('_'):
                    functions[name] = method
            
            return functions
            
        except Exception as e:
            logger.error(f"컨트랙트 코드 컴파일 오류: {e}")
            raise
    
    async def _execute_compiled_function(self, function: Callable, parameters: Dict[str, Any], 
                                       gas_limit: int) -> Any:
        """컴파일된 함수 실행"""
        try:
            # 가스 체크
            if self.vm_registers['gas'] >= gas_limit:
                raise Exception("가스 한도 초과")
            
            # 함수 실행
            result = function(**parameters)
            
            # 가스 사용량 계산
            gas_used = self._calculate_gas_usage(function, parameters)
            self.vm_registers['gas'] += gas_used
            
            return result
            
        except Exception as e:
            logger.error(f"컴파일된 함수 실행 오류: {e}")
            raise
    
    def _calculate_gas_usage(self, function: Callable, parameters: Dict[str, Any]) -> int:
        """가스 사용량 계산"""
        try:
            # 기본 가스 비용
            base_cost = 21000
            
            # 함수 복잡도에 따른 추가 비용
            function_complexity = len(inspect.getsource(function).split('\n'))
            complexity_cost = function_complexity * 3
            
            # 매개변수 크기에 따른 비용
            param_cost = sum(len(str(v)) for v in parameters.values()) * 16
            
            # 저장소 접근 비용
            storage_cost = 0
            if hasattr(function, '__self__'):
                state = getattr(function.__self__, 'state', {})
                storage_cost = len(state) * 200
            
            total_cost = base_cost + complexity_cost + param_cost + storage_cost
            
            return total_cost
            
        except Exception as e:
            logger.error(f"가스 사용량 계산 오류: {e}")
            return 21000  # 기본 비용
    
    def emit_event(self, event_name: str, event_data: Dict[str, Any]):
        """이벤트 발생"""
        try:
            event = {
                'event_id': str(uuid.uuid4()),
                'contract_id': self.vm_memory['contract'].contract_id,
                'event_name': event_name,
                'event_data': event_data,
                'block_number': self.vm_memory['block']['number'],
                'transaction_hash': hashlib.sha256(str(time.time()).encode()).hexdigest(),
                'timestamp': datetime.now().isoformat()
            }
            
            # 이벤트 저장
            self._save_event_to_db(event)
            
            # 컨트랙트 상태에 이벤트 추가
            contract_state = self.vm_memory['state']
            contract_state.events.append(event)
            
            logger.info(f"이벤트 발생: {event_name}")
            
        except Exception as e:
            logger.error(f"이벤트 발생 오류: {e}")
    
    def get_contract_state(self, contract_id: str) -> Optional[ContractState]:
        """컨트랙트 상태 조회"""
        try:
            return self.contract_states.get(contract_id)
        except Exception as e:
            logger.error(f"컨트랙트 상태 조회 오류: {e}")
            return None
    
    def get_contract_executions(self, contract_id: str) -> List[ContractExecution]:
        """컨트랙트 실행 기록 조회"""
        try:
            return [execution for execution in self.executions.values() 
                   if execution.contract_id == contract_id]
        except Exception as e:
            logger.error(f"컨트랙트 실행 기록 조회 오류: {e}")
            return []
    
    def _save_contract_to_db(self, contract: SmartContract, state: ContractState):
        """컨트랙트를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 컨트랙트 저장
            cursor.execute('''
                INSERT OR REPLACE INTO contracts 
                (contract_id, name, code, owner, address, balance, contract_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract.contract_id,
                contract.name,
                contract.code,
                contract.owner,
                contract.address,
                contract.balance,
                'custom',
                contract.created_at.isoformat(),
                contract.updated_at.isoformat()
            ))
            
            # 상태 저장
            cursor.execute('''
                INSERT OR REPLACE INTO contract_states 
                (contract_id, variables, mappings, arrays, events, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                state.contract_id,
                json.dumps(state.variables),
                json.dumps(state.mappings),
                json.dumps(state.arrays),
                json.dumps(state.events),
                state.last_updated.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"컨트랙트 데이터베이스 저장 오류: {e}")
    
    def _save_execution_to_db(self, execution: ContractExecution):
        """실행 기록을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO executions 
                (execution_id, contract_id, function_name, parameters, caller, gas_used, gas_limit, 
                 execution_time, status, result, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution.execution_id,
                execution.contract_id,
                execution.function_name,
                json.dumps(execution.parameters),
                execution.caller,
                execution.gas_used,
                execution.gas_limit,
                execution.execution_time,
                execution.status.value,
                json.dumps(execution.result) if execution.result else None,
                execution.error_message,
                execution.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"실행 기록 데이터베이스 저장 오류: {e}")
    
    def _save_event_to_db(self, event: Dict[str, Any]):
        """이벤트를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO events 
                (event_id, contract_id, event_name, event_data, block_number, transaction_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['event_id'],
                event['contract_id'],
                event['event_name'],
                json.dumps(event['event_data']),
                event['block_number'],
                event['transaction_hash'],
                event['timestamp']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"이벤트 데이터베이스 저장 오류: {e}")
    
    def _save_contract_state_to_db(self, state: ContractState):
        """컨트랙트 상태를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE contract_states 
                SET variables = ?, mappings = ?, arrays = ?, events = ?, last_updated = ?
                WHERE contract_id = ?
            ''', (
                json.dumps(state.variables),
                json.dumps(state.mappings),
                json.dumps(state.arrays),
                json.dumps(state.events),
                state.last_updated.isoformat(),
                state.contract_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"컨트랙트 상태 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            logger.info("스마트 컨트랙트 엔진 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './smart_contracts.db'
    }
    
    # 스마트 컨트랙트 엔진 생성
    engine = SmartContractEngine(config)
    
    # 토큰 컨트랙트 배포
    token_code = engine.contract_templates['token']
    contract_id = engine.deploy_contract(
        name="MyToken",
        code=token_code,
        owner="0x1234567890abcdef",
        contract_type=ContractType.TOKEN
    )
    
    print(f"토큰 컨트랙트 배포 완료: {contract_id}")
    
    # 컨트랙트 함수 실행
    async def test_contract():
        result = await engine.execute_contract_function(
            contract_id=contract_id,
            function_name="transfer",
            parameters={'to': '0xabcdef1234567890', 'amount': 100},
            caller="0x1234567890abcdef"
        )
        print(f"함수 실행 결과: {result.status}")
    
    # 비동기 실행
    asyncio.run(test_contract()) 