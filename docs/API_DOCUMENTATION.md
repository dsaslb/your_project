# 📚 Your Program API 문서

**생성일**: 2025년 07월 29일  
**기본 URL**: `http://localhost:5000`

## 📋 목차

## 📋 API 목록



## 🔐 인증

모든 API는 JWT 토큰 기반 인증을 사용합니다.

### 인증 헤더
```
Authorization: Bearer <access_token>
```

### 토큰 갱신
액세스 토큰이 만료되면 리프레시 토큰을 사용하여 새로운 토큰을 발급받을 수 있습니다.

## 📊 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": {
    // 응답 데이터
  }
}
```

### 오류 응답
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "오류 메시지"
  }
}
```

## 🔒 보안

- 모든 API는 HTTPS를 통해 제공됩니다
- Rate limiting이 적용됩니다
- 입력 데이터는 검증됩니다
- 민감한 정보는 로그에 기록되지 않습니다

---

**© 2025 Your Program. All rights reserved.**
