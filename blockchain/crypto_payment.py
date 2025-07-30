"""
암호화폐 결제 시스템
다중 암호화폐 지원, 결제 게이트웨이, 지갑 관리, 거래 모니터링을 포함한 완전한 암호화폐 결제 플랫폼
"""

import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import aiohttp
from aiohttp import web
import websockets
import hashlib
import hmac
import base64
import secrets
from decimal import Decimal, ROUND_HALF_UP
import sqlite3
from pathlib import Path
import requests
from requests.exceptions import RequestException
import hmac
import hashlib
import time
import urllib.parse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptocurrencyType(Enum):
    """암호화폐 타입"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    LITECOIN = "litecoin"
    RIPPLE = "ripple"
    BITCOIN_CASH = "bitcoin_cash"
    CARDANO = "cardano"
    POLKADOT = "polkadot"
    CHAINLINK = "chainlink"
    UNISWAP = "uniswap"
    CUSTOM = "custom"

class PaymentStatus(Enum):
    """결제 상태"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class TransactionType(Enum):
    """거래 타입"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    EXCHANGE = "exchange"

@dataclass
class CryptocurrencyConfig:
    """암호화폐 설정"""
    symbol: str
    name: str
    decimals: int
    network: str
    confirmations_required: int
    min_amount: Decimal
    max_amount: Decimal
    fee_percentage: Decimal
    gas_limit: int = 21000
    gas_price: int = 20

@dataclass
class PaymentRequest:
    """결제 요청"""
    payment_id: str
    merchant_id: str
    amount: Decimal
    currency: CryptocurrencyType
    description: str
    callback_url: str
    return_url: str
    created_at: datetime
    expires_at: datetime
    status: PaymentStatus
    transaction_hash: str = ""
    confirmations: int = 0

@dataclass
class Wallet:
    """암호화폐 지갑"""
    wallet_id: str
    address: str
    private_key: str
    public_key: str
    cryptocurrency: CryptocurrencyType
    balance: Decimal
    created_at: datetime
    last_updated: datetime
    is_active: bool = True

@dataclass
class Transaction:
    """암호화폐 거래"""
    tx_id: str
    tx_hash: str
    from_address: str
    to_address: str
    amount: Decimal
    cryptocurrency: CryptocurrencyType
    tx_type: TransactionType
    status: PaymentStatus
    confirmations: int
    block_number: int
    gas_used: int
    gas_price: int
    fee: Decimal
    created_at: datetime
    confirmed_at: datetime = None

class CryptoPaymentGateway:
    """암호화폐 결제 게이트웨이"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cryptocurrencies: Dict[CryptocurrencyType, CryptocurrencyConfig] = {}
        self.wallets: Dict[str, Wallet] = {}
        self.payment_requests: Dict[str, PaymentRequest] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.exchange_rates: Dict[str, Decimal] = {}
        
        # API 키
        self.api_keys = config.get('api_keys', {})
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './crypto_payments.db'))
        self._init_database()
        
        # 암호화폐 설정 초기화
        self._init_cryptocurrencies()
        
        # 지갑 초기화
        self._init_wallets()
        
        # 모니터링 스레드
        self.monitoring_thread = None
        self.is_running = False
        
        logger.info("암호화폐 결제 게이트웨이 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 지갑 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wallets (
                    wallet_id TEXT PRIMARY KEY,
                    address TEXT,
                    private_key TEXT,
                    public_key TEXT,
                    cryptocurrency TEXT,
                    balance REAL,
                    created_at TEXT,
                    last_updated TEXT,
                    is_active INTEGER
                )
            ''')
            
            # 결제 요청 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_requests (
                    payment_id TEXT PRIMARY KEY,
                    merchant_id TEXT,
                    amount REAL,
                    currency TEXT,
                    description TEXT,
                    callback_url TEXT,
                    return_url TEXT,
                    created_at TEXT,
                    expires_at TEXT,
                    status TEXT,
                    transaction_hash TEXT,
                    confirmations INTEGER
                )
            ''')
            
            # 거래 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    tx_id TEXT PRIMARY KEY,
                    tx_hash TEXT,
                    from_address TEXT,
                    to_address TEXT,
                    amount REAL,
                    cryptocurrency TEXT,
                    tx_type TEXT,
                    status TEXT,
                    confirmations INTEGER,
                    block_number INTEGER,
                    gas_used INTEGER,
                    gas_price INTEGER,
                    fee REAL,
                    created_at TEXT,
                    confirmed_at TEXT
                )
            ''')
            
            # 환율 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    currency TEXT PRIMARY KEY,
                    rate REAL,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("암호화폐 결제 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _init_cryptocurrencies(self):
        """암호화폐 설정 초기화"""
        try:
            self.cryptocurrencies = {
                CryptocurrencyType.BITCOIN: CryptocurrencyConfig(
                    symbol="BTC",
                    name="Bitcoin",
                    decimals=8,
                    network="bitcoin",
                    confirmations_required=6,
                    min_amount=Decimal("0.0001"),
                    max_amount=Decimal("100"),
                    fee_percentage=Decimal("0.001")
                ),
                CryptocurrencyType.ETHEREUM: CryptocurrencyConfig(
                    symbol="ETH",
                    name="Ethereum",
                    decimals=18,
                    network="ethereum",
                    confirmations_required=12,
                    min_amount=Decimal("0.001"),
                    max_amount=Decimal("1000"),
                    fee_percentage=Decimal("0.002"),
                    gas_limit=21000,
                    gas_price=20
                ),
                CryptocurrencyType.LITECOIN: CryptocurrencyConfig(
                    symbol="LTC",
                    name="Litecoin",
                    decimals=8,
                    network="litecoin",
                    confirmations_required=6,
                    min_amount=Decimal("0.01"),
                    max_amount=Decimal("1000"),
                    fee_percentage=Decimal("0.001")
                ),
                CryptocurrencyType.RIPPLE: CryptocurrencyConfig(
                    symbol="XRP",
                    name="Ripple",
                    decimals=6,
                    network="ripple",
                    confirmations_required=1,
                    min_amount=Decimal("1"),
                    max_amount=Decimal("1000000"),
                    fee_percentage=Decimal("0.0001")
                ),
                CryptocurrencyType.BITCOIN_CASH: CryptocurrencyConfig(
                    symbol="BCH",
                    name="Bitcoin Cash",
                    decimals=8,
                    network="bitcoin_cash",
                    confirmations_required=6,
                    min_amount=Decimal("0.001"),
                    max_amount=Decimal("1000"),
                    fee_percentage=Decimal("0.001")
                )
            }
            
            logger.info(f"{len(self.cryptocurrencies)}개 암호화폐 설정 완료")
            
        except Exception as e:
            logger.error(f"암호화폐 설정 초기화 오류: {e}")
            raise
    
    def _init_wallets(self):
        """지갑 초기화"""
        try:
            # 각 암호화폐별로 지갑 생성
            for crypto_type in self.cryptocurrencies.keys():
                wallet = self._create_wallet(crypto_type)
                self.wallets[wallet.wallet_id] = wallet
                self._save_wallet_to_db(wallet)
            
            logger.info(f"{len(self.wallets)}개 지갑 초기화 완료")
            
        except Exception as e:
            logger.error(f"지갑 초기화 오류: {e}")
            raise
    
    def _create_wallet(self, cryptocurrency: CryptocurrencyType) -> Wallet:
        """지갑 생성"""
        try:
            wallet_id = str(uuid.uuid4())
            
            # 실제 구현에서는 각 암호화폐별로 적절한 키 생성 알고리즘 사용
            # 여기서는 간단한 예시
            private_key = secrets.token_hex(32)
            public_key = hashlib.sha256(private_key.encode()).hexdigest()
            address = hashlib.sha256(public_key.encode()).hexdigest()[:40]
            
            wallet = Wallet(
                wallet_id=wallet_id,
                address=address,
                private_key=private_key,
                public_key=public_key,
                cryptocurrency=cryptocurrency,
                balance=Decimal("0"),
                created_at=datetime.now(),
                last_updated=datetime.now(),
                is_active=True
            )
            
            return wallet
            
        except Exception as e:
            logger.error(f"지갑 생성 오류: {e}")
            raise
    
    def create_payment_request(self, merchant_id: str, amount: Decimal, 
                             currency: CryptocurrencyType, description: str,
                             callback_url: str, return_url: str,
                             expiry_minutes: int = 30) -> PaymentRequest:
        """결제 요청 생성"""
        try:
            # 금액 검증
            crypto_config = self.cryptocurrencies[currency]
            if amount < crypto_config.min_amount or amount > crypto_config.max_amount:
                raise ValueError(f"금액이 허용 범위를 벗어났습니다. 최소: {crypto_config.min_amount}, 최대: {crypto_config.max_amount}")
            
            payment_id = str(uuid.uuid4())
            created_at = datetime.now()
            expires_at = created_at + timedelta(minutes=expiry_minutes)
            
            payment_request = PaymentRequest(
                payment_id=payment_id,
                merchant_id=merchant_id,
                amount=amount,
                currency=currency,
                description=description,
                callback_url=callback_url,
                return_url=return_url,
                created_at=created_at,
                expires_at=expires_at,
                status=PaymentStatus.PENDING
            )
            
            self.payment_requests[payment_id] = payment_request
            self._save_payment_request_to_db(payment_request)
            
            logger.info(f"결제 요청 생성 완료: {payment_id}")
            return payment_request
            
        except Exception as e:
            logger.error(f"결제 요청 생성 오류: {e}")
            raise
    
    def get_payment_info(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """결제 정보 조회"""
        try:
            payment_request = self.payment_requests.get(payment_id)
            if not payment_request:
                return None
            
            # 만료 확인
            if datetime.now() > payment_request.expires_at:
                payment_request.status = PaymentStatus.EXPIRED
                self._save_payment_request_to_db(payment_request)
            
            # 환율 정보
            exchange_rate = self.exchange_rates.get(payment_request.currency.value, Decimal("1"))
            
            return {
                'payment_id': payment_request.payment_id,
                'merchant_id': payment_request.merchant_id,
                'amount': str(payment_request.amount),
                'currency': payment_request.currency.value,
                'currency_symbol': self.cryptocurrencies[payment_request.currency].symbol,
                'description': payment_request.description,
                'status': payment_request.status.value,
                'created_at': payment_request.created_at.isoformat(),
                'expires_at': payment_request.expires_at.isoformat(),
                'transaction_hash': payment_request.transaction_hash,
                'confirmations': payment_request.confirmations,
                'exchange_rate': str(exchange_rate),
                'usd_amount': str(payment_request.amount * exchange_rate),
                'wallet_address': self._get_wallet_address(payment_request.currency),
                'qr_code_data': self._generate_qr_code_data(payment_request)
            }
            
        except Exception as e:
            logger.error(f"결제 정보 조회 오류: {e}")
            return None
    
    def _get_wallet_address(self, cryptocurrency: CryptocurrencyType) -> str:
        """암호화폐별 지갑 주소 조회"""
        try:
            for wallet in self.wallets.values():
                if wallet.cryptocurrency == cryptocurrency and wallet.is_active:
                    return wallet.address
            return ""
        except Exception as e:
            logger.error(f"지갑 주소 조회 오류: {e}")
            return ""
    
    def _generate_qr_code_data(self, payment_request: PaymentRequest) -> str:
        """QR 코드 데이터 생성"""
        try:
            wallet_address = self._get_wallet_address(payment_request.currency)
            if not wallet_address:
                return ""
            
            # 암호화폐별 QR 코드 형식
            if payment_request.currency == CryptocurrencyType.BITCOIN:
                return f"bitcoin:{wallet_address}?amount={payment_request.amount}&label={payment_request.description}"
            elif payment_request.currency == CryptocurrencyType.ETHEREUM:
                return f"ethereum:{wallet_address}?value={payment_request.amount * Decimal('10')**18}"
            else:
                return wallet_address
                
        except Exception as e:
            logger.error(f"QR 코드 데이터 생성 오류: {e}")
            return ""
    
    async def process_payment(self, payment_id: str, transaction_hash: str) -> bool:
        """결제 처리"""
        try:
            payment_request = self.payment_requests.get(payment_id)
            if not payment_request:
                raise ValueError(f"결제 요청을 찾을 수 없습니다: {payment_id}")
            
            if payment_request.status != PaymentStatus.PENDING:
                raise ValueError(f"결제가 이미 처리되었습니다: {payment_request.status}")
            
            # 트랜잭션 검증
            if not await self._verify_transaction(transaction_hash, payment_request):
                raise ValueError("트랜잭션이 유효하지 않습니다")
            
            # 결제 상태 업데이트
            payment_request.status = PaymentStatus.CONFIRMED
            payment_request.transaction_hash = transaction_hash
            payment_request.confirmations = 1
            
            self._save_payment_request_to_db(payment_request)
            
            # 거래 기록 생성
            transaction = Transaction(
                tx_id=str(uuid.uuid4()),
                tx_hash=transaction_hash,
                from_address="",  # 실제로는 트랜잭션에서 추출
                to_address=self._get_wallet_address(payment_request.currency),
                amount=payment_request.amount,
                cryptocurrency=payment_request.currency,
                tx_type=TransactionType.PAYMENT,
                status=PaymentStatus.CONFIRMED,
                confirmations=1,
                block_number=0,  # 실제로는 블록체인에서 추출
                gas_used=0,
                gas_price=0,
                fee=Decimal("0"),
                created_at=datetime.now()
            )
            
            self.transactions[transaction.tx_id] = transaction
            self._save_transaction_to_db(transaction)
            
            # 콜백 URL 호출
            await self._send_callback(payment_request)
            
            logger.info(f"결제 처리 완료: {payment_id}")
            return True
            
        except Exception as e:
            logger.error(f"결제 처리 오류: {e}")
            return False
    
    async def _verify_transaction(self, transaction_hash: str, payment_request: PaymentRequest) -> bool:
        """트랜잭션 검증"""
        try:
            # 실제 구현에서는 블록체인 API를 사용하여 트랜잭션 검증
            # 여기서는 간단한 예시
            
            # 트랜잭션 해시 형식 검증
            if len(transaction_hash) < 64:
                return False
            
            # 금액 검증 (실제로는 블록체인에서 확인)
            # 여기서는 항상 True 반환
            return True
            
        except Exception as e:
            logger.error(f"트랜잭션 검증 오류: {e}")
            return False
    
    async def _send_callback(self, payment_request: PaymentRequest):
        """콜백 URL 호출"""
        try:
            if not payment_request.callback_url:
                return
            
            callback_data = {
                'payment_id': payment_request.payment_id,
                'status': payment_request.status.value,
                'amount': str(payment_request.amount),
                'currency': payment_request.currency.value,
                'transaction_hash': payment_request.transaction_hash,
                'confirmations': payment_request.confirmations,
                'timestamp': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(payment_request.callback_url, json=callback_data) as response:
                    if response.status == 200:
                        logger.info(f"콜백 전송 성공: {payment_request.payment_id}")
                    else:
                        logger.warning(f"콜백 전송 실패: {response.status}")
                        
        except Exception as e:
            logger.error(f"콜백 전송 오류: {e}")
    
    async def update_exchange_rates(self):
        """환율 업데이트"""
        try:
            # 실제 구현에서는 외부 API 사용 (예: CoinGecko, CoinMarketCap)
            # 여기서는 간단한 예시
            
            rates = {
                'bitcoin': Decimal("45000"),
                'ethereum': Decimal("3000"),
                'litecoin': Decimal("150"),
                'ripple': Decimal("1.2"),
                'bitcoin_cash': Decimal("400")
            }
            
            self.exchange_rates.update(rates)
            
            # 데이터베이스에 저장
            self._save_exchange_rates_to_db()
            
            logger.info("환율 업데이트 완료")
            
        except Exception as e:
            logger.error(f"환율 업데이트 오류: {e}")
    
    def get_wallet_balance(self, cryptocurrency: CryptocurrencyType) -> Decimal:
        """지갑 잔액 조회"""
        try:
            for wallet in self.wallets.values():
                if wallet.cryptocurrency == cryptocurrency and wallet.is_active:
                    return wallet.balance
            return Decimal("0")
        except Exception as e:
            logger.error(f"지갑 잔액 조회 오류: {e}")
            return Decimal("0")
    
    def get_transaction_history(self, wallet_address: str = None, 
                               cryptocurrency: CryptocurrencyType = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """거래 내역 조회"""
        try:
            filtered_transactions = []
            
            for transaction in self.transactions.values():
                # 필터링
                if wallet_address and transaction.to_address != wallet_address:
                    continue
                if cryptocurrency and transaction.cryptocurrency != cryptocurrency:
                    continue
                
                filtered_transactions.append({
                    'tx_id': transaction.tx_id,
                    'tx_hash': transaction.tx_hash,
                    'from_address': transaction.from_address,
                    'to_address': transaction.to_address,
                    'amount': str(transaction.amount),
                    'cryptocurrency': transaction.cryptocurrency.value,
                    'tx_type': transaction.tx_type.value,
                    'status': transaction.status.value,
                    'confirmations': transaction.confirmations,
                    'fee': str(transaction.fee),
                    'created_at': transaction.created_at.isoformat(),
                    'confirmed_at': transaction.confirmed_at.isoformat() if transaction.confirmed_at else None
                })
            
            # 최신 순으로 정렬
            filtered_transactions.sort(key=lambda x: x['created_at'], reverse=True)
            
            return filtered_transactions[:limit]
            
        except Exception as e:
            logger.error(f"거래 내역 조회 오류: {e}")
            return []
    
    def _save_wallet_to_db(self, wallet: Wallet):
        """지갑을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO wallets 
                (wallet_id, address, private_key, public_key, cryptocurrency, balance, created_at, last_updated, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                wallet.wallet_id,
                wallet.address,
                wallet.private_key,
                wallet.public_key,
                wallet.cryptocurrency.value,
                float(wallet.balance),
                wallet.created_at.isoformat(),
                wallet.last_updated.isoformat(),
                1 if wallet.is_active else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"지갑 데이터베이스 저장 오류: {e}")
    
    def _save_payment_request_to_db(self, payment_request: PaymentRequest):
        """결제 요청을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO payment_requests 
                (payment_id, merchant_id, amount, currency, description, callback_url, return_url, 
                 created_at, expires_at, status, transaction_hash, confirmations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                payment_request.payment_id,
                payment_request.merchant_id,
                float(payment_request.amount),
                payment_request.currency.value,
                payment_request.description,
                payment_request.callback_url,
                payment_request.return_url,
                payment_request.created_at.isoformat(),
                payment_request.expires_at.isoformat(),
                payment_request.status.value,
                payment_request.transaction_hash,
                payment_request.confirmations
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"결제 요청 데이터베이스 저장 오류: {e}")
    
    def _save_transaction_to_db(self, transaction: Transaction):
        """거래를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO transactions 
                (tx_id, tx_hash, from_address, to_address, amount, cryptocurrency, tx_type, status, 
                 confirmations, block_number, gas_used, gas_price, fee, created_at, confirmed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.tx_id,
                transaction.tx_hash,
                transaction.from_address,
                transaction.to_address,
                float(transaction.amount),
                transaction.cryptocurrency.value,
                transaction.tx_type.value,
                transaction.status.value,
                transaction.confirmations,
                transaction.block_number,
                transaction.gas_used,
                transaction.gas_price,
                float(transaction.fee),
                transaction.created_at.isoformat(),
                transaction.confirmed_at.isoformat() if transaction.confirmed_at else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"거래 데이터베이스 저장 오류: {e}")
    
    def _save_exchange_rates_to_db(self):
        """환율을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for currency, rate in self.exchange_rates.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO exchange_rates 
                    (currency, rate, updated_at)
                    VALUES (?, ?, ?)
                ''', (
                    currency,
                    float(rate),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"환율 데이터베이스 저장 오류: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        try:
            self.is_running = True
            
            def monitoring_worker():
                while self.is_running:
                    try:
                        # 만료된 결제 요청 처리
                        self._cleanup_expired_payments()
                        
                        # 환율 업데이트
                        asyncio.run(self.update_exchange_rates())
                        
                        time.sleep(60)  # 1분마다 체크
                        
                    except Exception as e:
                        logger.error(f"모니터링 워커 오류: {e}")
                        time.sleep(60)
            
            self.monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("암호화폐 결제 모니터링 시작")
            
        except Exception as e:
            logger.error(f"모니터링 시작 오류: {e}")
    
    def _cleanup_expired_payments(self):
        """만료된 결제 요청 정리"""
        try:
            current_time = datetime.now()
            expired_payments = []
            
            for payment_id, payment_request in self.payment_requests.items():
                if (payment_request.status == PaymentStatus.PENDING and 
                    current_time > payment_request.expires_at):
                    payment_request.status = PaymentStatus.EXPIRED
                    expired_payments.append(payment_request)
            
            # 데이터베이스 업데이트
            for payment_request in expired_payments:
                self._save_payment_request_to_db(payment_request)
            
            if expired_payments:
                logger.info(f"{len(expired_payments)}개 만료된 결제 요청 정리 완료")
                
        except Exception as e:
            logger.error(f"만료된 결제 요청 정리 오류: {e}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        try:
            self.is_running = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            logger.info("암호화폐 결제 모니터링 중지")
            
        except Exception as e:
            logger.error(f"모니터링 중지 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            self.stop_monitoring()
            logger.info("암호화폐 결제 게이트웨이 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './crypto_payments.db',
        'api_keys': {
            'coingecko': 'your_api_key_here'
        }
    }
    
    # 암호화폐 결제 게이트웨이 생성
    gateway = CryptoPaymentGateway(config)
    
    # 결제 요청 생성
    payment_request = gateway.create_payment_request(
        merchant_id="merchant_123",
        amount=Decimal("0.001"),
        currency=CryptocurrencyType.BITCOIN,
        description="테스트 결제",
        callback_url="https://example.com/callback",
        return_url="https://example.com/return"
    )
    
    print(f"결제 요청 생성: {payment_request.payment_id}")
    
    # 결제 정보 조회
    payment_info = gateway.get_payment_info(payment_request.payment_id)
    print(f"결제 정보: {payment_info}")
    
    # 모니터링 시작
    gateway.start_monitoring()
    
    # 잠시 대기
    time.sleep(10)
    
    # 지갑 잔액 조회
    balance = gateway.get_wallet_balance(CryptocurrencyType.BITCOIN)
    print(f"비트코인 잔액: {balance}")
    
    # 모니터링 중지
    gateway.stop_monitoring() 