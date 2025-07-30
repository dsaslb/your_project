"""
블록체인 코어 시스템
분산 원장, 합의 알고리즘, 암호화, P2P 네트워크를 포함한 완전한 블록체인 시스템
"""

import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import aiohttp
from aiohttp import web
import websockets
import logging
import secrets
import hmac
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
from pathlib import Path
import sqlite3
import pickle

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """트랜잭션 타입"""
    TRANSFER = "transfer"
    SMART_CONTRACT = "smart_contract"
    DATA_STORAGE = "data_storage"
    VOTING = "voting"
    IDENTITY = "identity"

class BlockStatus(Enum):
    """블록 상태"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class ConsensusType(Enum):
    """합의 알고리즘 타입"""
    PROOF_OF_WORK = "proof_of_work"
    PROOF_OF_STAKE = "proof_of_stake"
    DELEGATED_PROOF_OF_STAKE = "delegated_proof_of_stake"
    PRACTICAL_BYZANTINE_FAULT_TOLERANCE = "pbft"

@dataclass
class Transaction:
    """트랜잭션"""
    tx_id: str
    tx_type: TransactionType
    sender: str
    recipient: str
    amount: float
    data: Dict[str, Any]
    timestamp: datetime
    signature: str
    nonce: int
    gas_price: float = 0.0
    gas_limit: int = 21000

@dataclass
class Block:
    """블록"""
    block_id: str
    previous_hash: str
    merkle_root: str
    timestamp: datetime
    transactions: List[Transaction]
    nonce: int
    difficulty: int
    miner: str
    block_hash: str
    status: BlockStatus = BlockStatus.PENDING

@dataclass
class Wallet:
    """지갑"""
    address: str
    public_key: str
    private_key: str
    balance: float
    nonce: int
    created_at: datetime

@dataclass
class SmartContract:
    """스마트 컨트랙트"""
    contract_id: str
    name: str
    code: str
    owner: str
    address: str
    balance: float
    state: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class BlockchainCore:
    """블록체인 코어 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.wallets: Dict[str, Wallet] = {}
        self.smart_contracts: Dict[str, SmartContract] = {}
        self.peers: List[str] = []
        self.difficulty = config.get('difficulty', 4)
        self.block_reward = config.get('block_reward', 50.0)
        self.consensus_type = ConsensusType(config.get('consensus_type', 'proof_of_work'))
        
        # 네트워크 관련
        self.node_id = str(uuid.uuid4())
        self.websocket_server = None
        self.http_server = None
        self.is_running = False
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './blockchain.db'))
        self._init_database()
        
        # 제네시스 블록 생성
        self._create_genesis_block()
        
        # 워커 스레드
        self.mining_thread = None
        self.network_thread = None
        self.transaction_queue = queue.Queue()
        
        logger.info("블록체인 코어 시스템 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 블록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocks (
                    block_id TEXT PRIMARY KEY,
                    previous_hash TEXT,
                    merkle_root TEXT,
                    timestamp TEXT,
                    nonce INTEGER,
                    difficulty INTEGER,
                    miner TEXT,
                    block_hash TEXT,
                    status TEXT
                )
            ''')
            
            # 트랜잭션 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    tx_id TEXT PRIMARY KEY,
                    block_id TEXT,
                    tx_type TEXT,
                    sender TEXT,
                    recipient TEXT,
                    amount REAL,
                    data TEXT,
                    timestamp TEXT,
                    signature TEXT,
                    nonce INTEGER,
                    gas_price REAL,
                    gas_limit INTEGER,
                    FOREIGN KEY (block_id) REFERENCES blocks (block_id)
                )
            ''')
            
            # 지갑 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wallets (
                    address TEXT PRIMARY KEY,
                    public_key TEXT,
                    private_key TEXT,
                    balance REAL,
                    nonce INTEGER,
                    created_at TEXT
                )
            ''')
            
            # 스마트 컨트랙트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS smart_contracts (
                    contract_id TEXT PRIMARY KEY,
                    name TEXT,
                    code TEXT,
                    owner TEXT,
                    address TEXT,
                    balance REAL,
                    state TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _create_genesis_block(self):
        """제네시스 블록 생성"""
        try:
            genesis_transaction = Transaction(
                tx_id=str(uuid.uuid4()),
                tx_type=TransactionType.TRANSFER,
                sender="0" * 64,  # 제네시스 주소
                recipient=self.config.get('genesis_recipient', '0' * 64),
                amount=self.block_reward,
                data={},
                timestamp=datetime.now(),
                signature="",
                nonce=0
            )
            
            genesis_block = Block(
                block_id=str(uuid.uuid4()),
                previous_hash="0" * 64,
                merkle_root=self._calculate_merkle_root([genesis_transaction]),
                timestamp=datetime.now(),
                transactions=[genesis_transaction],
                nonce=0,
                difficulty=self.difficulty,
                miner="genesis",
                block_hash="",
                status=BlockStatus.CONFIRMED
            )
            
            genesis_block.block_hash = self._calculate_block_hash(genesis_block)
            self.chain.append(genesis_block)
            
            # 데이터베이스에 저장
            self._save_block_to_db(genesis_block)
            
            logger.info("제네시스 블록 생성 완료")
            
        except Exception as e:
            logger.error(f"제네시스 블록 생성 오류: {e}")
            raise
    
    def create_wallet(self) -> Wallet:
        """지갑 생성"""
        try:
            # RSA 키 쌍 생성
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # 주소 생성 (공개키 해시)
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            address = hashlib.sha256(public_key_bytes).hexdigest()
            
            # 개인키를 PEM 형식으로 직렬화
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            wallet = Wallet(
                address=address,
                public_key=public_key_pem,
                private_key=private_key_pem,
                balance=0.0,
                nonce=0,
                created_at=datetime.now()
            )
            
            self.wallets[address] = wallet
            self._save_wallet_to_db(wallet)
            
            logger.info(f"지갑 생성 완료: {address}")
            return wallet
            
        except Exception as e:
            logger.error(f"지갑 생성 오류: {e}")
            raise
    
    def create_transaction(self, sender: str, recipient: str, amount: float, 
                          data: Dict[str, Any] = None, tx_type: TransactionType = TransactionType.TRANSFER) -> Transaction:
        """트랜잭션 생성"""
        try:
            # 지갑 확인
            if sender not in self.wallets:
                raise ValueError(f"발신자 지갑을 찾을 수 없습니다: {sender}")
            
            wallet = self.wallets[sender]
            
            # 잔액 확인
            if wallet.balance < amount:
                raise ValueError(f"잔액이 부족합니다. 필요: {amount}, 보유: {wallet.balance}")
            
            # 트랜잭션 생성
            transaction = Transaction(
                tx_id=str(uuid.uuid4()),
                tx_type=tx_type,
                sender=sender,
                recipient=recipient,
                amount=amount,
                data=data or {},
                timestamp=datetime.now(),
                signature="",
                nonce=wallet.nonce
            )
            
            # 트랜잭션 서명
            transaction.signature = self._sign_transaction(transaction, wallet.private_key)
            
            # 지갑 nonce 증가
            wallet.nonce += 1
            
            # 대기 트랜잭션에 추가
            self.pending_transactions.append(transaction)
            
            logger.info(f"트랜잭션 생성 완료: {transaction.tx_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"트랜잭션 생성 오류: {e}")
            raise
    
    def _sign_transaction(self, transaction: Transaction, private_key_pem: str) -> str:
        """트랜잭션 서명"""
        try:
            # 개인키 로드
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            
            # 서명할 데이터 생성
            data_to_sign = f"{transaction.sender}{transaction.recipient}{transaction.amount}{transaction.nonce}{transaction.timestamp.isoformat()}"
            data_bytes = data_to_sign.encode('utf-8')
            
            # 서명 생성
            signature = private_key.sign(
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"트랜잭션 서명 오류: {e}")
            raise
    
    def verify_transaction(self, transaction: Transaction) -> bool:
        """트랜잭션 검증"""
        try:
            # 서명 검증
            if not self._verify_signature(transaction):
                return False
            
            # 발신자 지갑 확인
            if transaction.sender not in self.wallets:
                return False
            
            wallet = self.wallets[transaction.sender]
            
            # nonce 확인
            if transaction.nonce != wallet.nonce:
                return False
            
            # 잔액 확인
            if wallet.balance < transaction.amount:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"트랜잭션 검증 오류: {e}")
            return False
    
    def _verify_signature(self, transaction: Transaction) -> bool:
        """서명 검증"""
        try:
            # 발신자 지갑의 공개키 가져오기
            if transaction.sender not in self.wallets:
                return False
            
            wallet = self.wallets[transaction.sender]
            public_key = serialization.load_pem_public_key(
                wallet.public_key.encode('utf-8'),
                backend=default_backend()
            )
            
            # 서명할 데이터 생성
            data_to_sign = f"{transaction.sender}{transaction.recipient}{transaction.amount}{transaction.nonce}{transaction.timestamp.isoformat()}"
            data_bytes = data_to_sign.encode('utf-8')
            
            # 서명 검증
            signature = base64.b64decode(transaction.signature.encode('utf-8'))
            
            public_key.verify(
                signature,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"서명 검증 오류: {e}")
            return False
    
    def mine_block(self, miner_address: str) -> Optional[Block]:
        """블록 마이닝"""
        try:
            if not self.pending_transactions:
                return None
            
            # 대기 트랜잭션 검증
            valid_transactions = []
            for tx in self.pending_transactions:
                if self.verify_transaction(tx):
                    valid_transactions.append(tx)
                else:
                    logger.warning(f"유효하지 않은 트랜잭션 제거: {tx.tx_id}")
            
            if not valid_transactions:
                return None
            
            # 블록 생성
            previous_block = self.chain[-1]
            block = Block(
                block_id=str(uuid.uuid4()),
                previous_hash=previous_block.block_hash,
                merkle_root=self._calculate_merkle_root(valid_transactions),
                timestamp=datetime.now(),
                transactions=valid_transactions,
                nonce=0,
                difficulty=self.difficulty,
                miner=miner_address,
                block_hash=""
            )
            
            # 작업 증명
            target = "0" * self.difficulty
            while True:
                block.nonce += 1
                block.block_hash = self._calculate_block_hash(block)
                
                if block.block_hash.startswith(target):
                    break
                
                # 마이닝 중단 확인
                if not self.is_running:
                    return None
            
            # 블록 체인에 추가
            block.status = BlockStatus.CONFIRMED
            self.chain.append(block)
            
            # 대기 트랜잭션에서 제거
            for tx in valid_transactions:
                self.pending_transactions.remove(tx)
            
            # 마이너에게 보상
            reward_tx = Transaction(
                tx_id=str(uuid.uuid4()),
                tx_type=TransactionType.TRANSFER,
                sender="0" * 64,
                recipient=miner_address,
                amount=self.block_reward,
                data={},
                timestamp=datetime.now(),
                signature="",
                nonce=0
            )
            self.pending_transactions.append(reward_tx)
            
            # 잔액 업데이트
            self._update_balances(valid_transactions)
            
            # 데이터베이스에 저장
            self._save_block_to_db(block)
            
            logger.info(f"블록 마이닝 완료: {block.block_id} (nonce: {block.nonce})")
            return block
            
        except Exception as e:
            logger.error(f"블록 마이닝 오류: {e}")
            return None
    
    def _calculate_block_hash(self, block: Block) -> str:
        """블록 해시 계산"""
        try:
            block_data = {
                'block_id': block.block_id,
                'previous_hash': block.previous_hash,
                'merkle_root': block.merkle_root,
                'timestamp': block.timestamp.isoformat(),
                'nonce': block.nonce,
                'difficulty': block.difficulty,
                'miner': block.miner
            }
            
            block_string = json.dumps(block_data, sort_keys=True)
            return hashlib.sha256(block_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"블록 해시 계산 오류: {e}")
            raise
    
    def _calculate_merkle_root(self, transactions: List[Transaction]) -> str:
        """머클 루트 계산"""
        try:
            if not transactions:
                return hashlib.sha256("".encode()).hexdigest()
            
            # 트랜잭션 해시 계산
            tx_hashes = []
            for tx in transactions:
                tx_data = f"{tx.tx_id}{tx.sender}{tx.recipient}{tx.amount}{tx.nonce}{tx.timestamp.isoformat()}"
                tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
                tx_hashes.append(tx_hash)
            
            # 머클 트리 구성
            while len(tx_hashes) > 1:
                new_hashes = []
                for i in range(0, len(tx_hashes), 2):
                    if i + 1 < len(tx_hashes):
                        combined = tx_hashes[i] + tx_hashes[i + 1]
                    else:
                        combined = tx_hashes[i] + tx_hashes[i]
                    
                    new_hash = hashlib.sha256(combined.encode()).hexdigest()
                    new_hashes.append(new_hash)
                
                tx_hashes = new_hashes
            
            return tx_hashes[0]
            
        except Exception as e:
            logger.error(f"머클 루트 계산 오류: {e}")
            raise
    
    def _update_balances(self, transactions: List[Transaction]):
        """잔액 업데이트"""
        try:
            for tx in transactions:
                if tx.sender in self.wallets:
                    self.wallets[tx.sender].balance -= tx.amount
                
                if tx.recipient in self.wallets:
                    self.wallets[tx.recipient].balance += tx.amount
                    
        except Exception as e:
            logger.error(f"잔액 업데이트 오류: {e}")
    
    def _save_block_to_db(self, block: Block):
        """블록을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 블록 저장
            cursor.execute('''
                INSERT OR REPLACE INTO blocks 
                (block_id, previous_hash, merkle_root, timestamp, nonce, difficulty, miner, block_hash, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                block.block_id,
                block.previous_hash,
                block.merkle_root,
                block.timestamp.isoformat(),
                block.nonce,
                block.difficulty,
                block.miner,
                block.block_hash,
                block.status.value
            ))
            
            # 트랜잭션 저장
            for tx in block.transactions:
                cursor.execute('''
                    INSERT OR REPLACE INTO transactions 
                    (tx_id, block_id, tx_type, sender, recipient, amount, data, timestamp, signature, nonce, gas_price, gas_limit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tx.tx_id,
                    block.block_id,
                    tx.tx_type.value,
                    tx.sender,
                    tx.recipient,
                    tx.amount,
                    json.dumps(tx.data),
                    tx.timestamp.isoformat(),
                    tx.signature,
                    tx.nonce,
                    tx.gas_price,
                    tx.gas_limit
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"블록 데이터베이스 저장 오류: {e}")
    
    def _save_wallet_to_db(self, wallet: Wallet):
        """지갑을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO wallets 
                (address, public_key, private_key, balance, nonce, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                wallet.address,
                wallet.public_key,
                wallet.private_key,
                wallet.balance,
                wallet.nonce,
                wallet.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"지갑 데이터베이스 저장 오류: {e}")
    
    def get_balance(self, address: str) -> float:
        """잔액 조회"""
        try:
            if address in self.wallets:
                return self.wallets[address].balance
            return 0.0
        except Exception as e:
            logger.error(f"잔액 조회 오류: {e}")
            return 0.0
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """블록체인 정보 조회"""
        try:
            return {
                'chain_length': len(self.chain),
                'pending_transactions': len(self.pending_transactions),
                'difficulty': self.difficulty,
                'block_reward': self.block_reward,
                'consensus_type': self.consensus_type.value,
                'total_wallets': len(self.wallets),
                'last_block_hash': self.chain[-1].block_hash if self.chain else None,
                'last_block_timestamp': self.chain[-1].timestamp.isoformat() if self.chain else None
            }
        except Exception as e:
            logger.error(f"블록체인 정보 조회 오류: {e}")
            return {}
    
    def validate_chain(self) -> bool:
        """체인 유효성 검증"""
        try:
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]
                
                # 이전 블록 해시 확인
                if current_block.previous_hash != previous_block.block_hash:
                    logger.error(f"블록 {i}의 이전 해시가 일치하지 않습니다")
                    return False
                
                # 블록 해시 확인
                calculated_hash = self._calculate_block_hash(current_block)
                if current_block.block_hash != calculated_hash:
                    logger.error(f"블록 {i}의 해시가 일치하지 않습니다")
                    return False
                
                # 작업 증명 확인
                target = "0" * self.difficulty
                if not current_block.block_hash.startswith(target):
                    logger.error(f"블록 {i}의 작업 증명이 유효하지 않습니다")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"체인 유효성 검증 오류: {e}")
            return False
    
    def start_mining(self, miner_address: str):
        """마이닝 시작"""
        try:
            self.is_running = True
            
            def mining_worker():
                while self.is_running:
                    try:
                        block = self.mine_block(miner_address)
                        if block:
                            logger.info(f"새 블록 마이닝 완료: {block.block_id}")
                        time.sleep(1)
                    except Exception as e:
                        logger.error(f"마이닝 워커 오류: {e}")
                        time.sleep(5)
            
            self.mining_thread = threading.Thread(target=mining_worker, daemon=True)
            self.mining_thread.start()
            
            logger.info(f"마이닝 시작: {miner_address}")
            
        except Exception as e:
            logger.error(f"마이닝 시작 오류: {e}")
    
    def stop_mining(self):
        """마이닝 중지"""
        try:
            self.is_running = False
            if self.mining_thread:
                self.mining_thread.join(timeout=5)
            
            logger.info("마이닝 중지 완료")
            
        except Exception as e:
            logger.error(f"마이닝 중지 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            self.stop_mining()
            logger.info("블록체인 코어 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'difficulty': 4,
        'block_reward': 50.0,
        'consensus_type': 'proof_of_work',
        'db_path': './blockchain.db',
        'genesis_recipient': '0' * 64
    }
    
    # 블록체인 코어 생성
    blockchain = BlockchainCore(config)
    
    # 지갑 생성
    wallet1 = blockchain.create_wallet()
    wallet2 = blockchain.create_wallet()
    
    print(f"지갑 1: {wallet1.address}")
    print(f"지갑 2: {wallet2.address}")
    
    # 트랜잭션 생성
    transaction = blockchain.create_transaction(
        sender=wallet1.address,
        recipient=wallet2.address,
        amount=10.0
    )
    
    print(f"트랜잭션 생성: {transaction.tx_id}")
    
    # 마이닝 시작
    blockchain.start_mining(wallet1.address)
    
    # 잠시 대기
    time.sleep(10)
    
    # 잔액 확인
    balance1 = blockchain.get_balance(wallet1.address)
    balance2 = blockchain.get_balance(wallet2.address)
    
    print(f"지갑 1 잔액: {balance1}")
    print(f"지갑 2 잔액: {balance2}")
    
    # 블록체인 정보
    info = blockchain.get_blockchain_info()
    print(f"블록체인 정보: {info}")
    
    # 마이닝 중지
    blockchain.stop_mining() 