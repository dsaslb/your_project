# 실시간 시스템 의존성 설치 가이드

## 필수 의존성 설치

실시간 시스템을 사용하기 위해 다음 패키지들을 설치해야 합니다:

### 1. Socket.IO 클라이언트

```bash
npm install socket.io-client
```

### 2. 타입 정의 (TypeScript 사용 시)

```bash
npm install --save-dev @types/socket.io-client
```

## 환경변수 설정

프로젝트 루트에 `.env.local` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# .env.local
NEXT_PUBLIC_WS_URL=ws://localhost:5000
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## 설치 확인

설치가 완료되었는지 확인하려면:

```bash
npm list socket.io-client
```

## 문제 해결

### 1. 설치 오류 발생 시

```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install

# 또는 yarn 사용 시
rm -rf node_modules yarn.lock
yarn install
```

### 2. 타입 오류 발생 시

```bash
# TypeScript 재설치
npm install --save-dev typescript @types/node
```

### 3. 웹소켓 연결 실패 시

- 백엔드 서버가 실행 중인지 확인
- 포트 번호가 올바른지 확인
- 방화벽 설정 확인

## 개발 서버 실행

의존성 설치 완료 후:

```bash
npm run dev
```

그 후 `http://localhost:3000/test-realtime`에서 테스트 페이지에 접근할 수 있습니다.
