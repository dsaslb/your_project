#!/bin/bash
# AWS 클라우드 배포 자동화 스크립트 예시
# EC2 인스턴스 생성, 환경설정, 서버/스케줄러/이벤트 감지 서비스 자동 실행

# 1. EC2 인스턴스 생성 (예: AWS CLI)
# aws ec2 run-instances --image-id ami-xxxx --count 1 --instance-type t3.medium --key-name my-key --security-group-ids sg-xxxx --subnet-id subnet-xxxx

# 2. SSH 접속 및 환경설정
# ssh -i my-key.pem ec2-user@<EC2_IP>
# sudo yum update -y
# sudo yum install python3 git -y
# git clone https://github.com/yourorg/your_program.git
# cd your_program
# pip3 install -r requirements.txt

# 3. 서버/스케줄러/이벤트 감지 서비스 실행
nohup python3 app.py &
nohup python3 scripts/auto_admin_alerts.py &
nohup python3 -m utils.event_auto_detector &

echo "[AWS 배포] 서버/스케줄러/이벤트 감지 서비스가 자동 실행되었습니다." 