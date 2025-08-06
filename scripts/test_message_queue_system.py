#!/usr/bin/env python3
"""
메시지 큐 시스템 테스트 스크립트

이 스크립트는 메시지 큐 시스템의 주요 기능을 테스트합니다.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000/api/message-queue"

def print_test_header(name):
    print(f"\n{'='*60}\n테스트: {name}\n{'='*60}")

def print_test_result(name, success, msg=""):
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{name}: {status}")
    if msg:
        print(f"  메시지: {msg}")

def test_health():
    print_test_header("시스템 상태 확인")
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print_test_result("상태 확인", True)
            return True
        else:
            print_test_result("상태 확인", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("상태 확인", False, str(e))
        return False

def test_create_queue():
    print_test_header("큐 생성")
    try:
        data = {"name": "테스트큐", "queue_type": "standard", "max_size": 100}
        r = requests.post(f"{BASE_URL}/queues", json=data)
        if r.status_code == 201:
            queue_id = r.json().get('queue_id')
            print_test_result("큐 생성", True, f"큐 ID: {queue_id}")
            return queue_id
        else:
            print_test_result("큐 생성", False, f"HTTP {r.status_code}")
            return None
    except Exception as e:
        print_test_result("큐 생성", False, str(e))
        return None

def test_publish_message(queue_id):
    print_test_header("메시지 발행")
    try:
        data = {"queue_id": queue_id, "topic": "test", "payload": {"msg": "hello"}, "priority": "normal"}
        r = requests.post(f"{BASE_URL}/messages", json=data)
        if r.status_code == 201:
            message_id = r.json().get('message_id')
            print_test_result("메시지 발행", True, f"메시지 ID: {message_id}")
            return message_id
        else:
            print_test_result("메시지 발행", False, f"HTTP {r.status_code}")
            return None
    except Exception as e:
        print_test_result("메시지 발행", False, str(e))
        return None

def test_consume_message(queue_id):
    print_test_header("메시지 소비")
    try:
        r = requests.post(f"{BASE_URL}/messages/consume", json={"queue_id": queue_id})
        if r.status_code == 200 and r.json().get('status') == 'success':
            data = r.json().get('data', {})
            print_test_result("메시지 소비", True, f"메시지 ID: {data.get('message_id')}")
            return data.get('message_id')
        else:
            print_test_result("메시지 소비", False, f"HTTP {r.status_code}")
            return None
    except Exception as e:
        print_test_result("메시지 소비", False, str(e))
        return None

def test_complete_message(message_id):
    print_test_header("메시지 완료 처리")
    try:
        r = requests.post(f"{BASE_URL}/messages/{message_id}/complete", json={"success": True})
        if r.status_code == 200:
            print_test_result("메시지 완료 처리", True)
            return True
        else:
            print_test_result("메시지 완료 처리", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("메시지 완료 처리", False, str(e))
        return False

def test_delete_queue(queue_id):
    print_test_header("큐 삭제")
    try:
        r = requests.delete(f"{BASE_URL}/queues/{queue_id}")
        if r.status_code == 200:
            print_test_result("큐 삭제", True)
            return True
        else:
            print_test_result("큐 삭제", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("큐 삭제", False, str(e))
        return False

def run_all_tests():
    print("🚀 메시지 큐 시스템 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results = []
    results.append(test_health())
    queue_id = test_create_queue()
    results.append(queue_id is not None)
    if queue_id:
        message_id = test_publish_message(queue_id)
        results.append(message_id is not None)
        if message_id:
            consumed_id = test_consume_message(queue_id)
            results.append(consumed_id == message_id)
            results.append(test_complete_message(message_id))
        results.append(test_delete_queue(queue_id))
    print("\n테스트 결과:")
    print(f"✅ 성공: {results.count(True)} / {len(results)}")
    print(f"❌ 실패: {results.count(False)} / {len(results)}")
    print(f"📅 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if all(results):
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")

if __name__ == "__main__":
    run_all_tests()