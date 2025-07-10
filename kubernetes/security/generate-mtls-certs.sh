#!/bin/bash

# mTLS 인증서 생성 스크립트
# 레스토랑 관리 시스템 마이크로서비스 간 암호화 통신을 위한 인증서 생성

set -e

# 디렉토리 생성
mkdir -p certs/ca
mkdir -p certs/server
mkdir -p certs/client

echo "🔐 mTLS 인증서 생성 시작..."

# 1. CA (Certificate Authority) 생성
echo "1. CA 인증서 생성..."
openssl genrsa -out certs/ca/ca.key 4096
openssl req -new -x509 -days 365 -key certs/ca/ca.key -out certs/ca/ca.crt \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Restaurant/OU=IT/CN=restaurant-ca"

# 2. 서버 인증서 생성
echo "2. 서버 인증서 생성..."

# API Gateway 서버 인증서
openssl genrsa -out certs/server/gateway.key 2048
openssl req -new -key certs/server/gateway.key -out certs/server/gateway.csr \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Restaurant/OU=IT/CN=gateway-service"
openssl x509 -req -days 365 -in certs/server/gateway.csr \
    -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial \
    -out certs/server/gateway.crt

# User Service 서버 인증서
openssl genrsa -out certs/server/user.key 2048
openssl req -new -key certs/server/user.key -out certs/server/user.csr \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Restaurant/OU=IT/CN=user-service"
openssl x509 -req -days 365 -in certs/server/user.csr \
    -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial \
    -out certs/server/user.crt

# IoT Service 서버 인증서
openssl genrsa -out certs/server/iot.key 2048
openssl req -new -key certs/server/iot.key -out certs/server/iot.csr \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Restaurant/OU=IT/CN=iot-service"
openssl x509 -req -days 365 -in certs/server/iot.csr \
    -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial \
    -out certs/server/iot.crt

# 3. 클라이언트 인증서 생성
echo "3. 클라이언트 인증서 생성..."

# API Gateway 클라이언트 인증서
openssl genrsa -out certs/client/gateway-client.key 2048
openssl req -new -key certs/client/gateway-client.key -out certs/client/gateway-client.csr \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Restaurant/OU=IT/CN=gateway-client"
openssl x509 -req -days 365 -in certs/client/gateway-client.csr \
    -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial \
    -out certs/client/gateway-client.crt

# User Service 클라이언트 인증서
openssl genrsa -out certs/client/user-client.key 2048
openssl req -new -key certs/client/user-client.key -out certs/client/user-client.csr \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Restaurant/OU=IT/CN=user-client"
openssl x509 -req -days 365 -in certs/client/user-client.csr \
    -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial \
    -out certs/client/user-client.crt

# IoT Service 클라이언트 인증서
openssl genrsa -out certs/client/iot-client.key 2048
openssl req -new -key certs/client/iot-client.key -out certs/client/iot-client.csr \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Restaurant/OU=IT/CN=iot-client"
openssl x509 -req -days 365 -in certs/client/iot-client.csr \
    -CA certs/ca/ca.crt -CAkey certs/ca/ca.key -CAcreateserial \
    -out certs/client/iot-client.crt

# 4. 인증서 검증
echo "4. 인증서 검증..."
for cert in certs/server/*.crt certs/client/*.crt; do
    echo "검증 중: $cert"
    openssl verify -CAfile certs/ca/ca.crt "$cert"
done

echo "✅ mTLS 인증서 생성 완료!"
echo "📁 생성된 인증서 위치: certs/"
echo "🔑 CA 인증서: certs/ca/ca.crt"
echo "🔒 서버 인증서: certs/server/"
echo "👤 클라이언트 인증서: certs/client/" 