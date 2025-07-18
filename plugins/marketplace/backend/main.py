"""
마켓플레이스 플러그인
플러그인 마켓플레이스 샘플
"""

from flask import Blueprint, request, jsonify
import os, zipfile, json
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import current_user
import json as pyjson
from flask_socketio import SocketIO
import uuid
import tempfile
import shutil
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

RATINGS_FILE = "plugins/marketplace/metadata/ratings.json"
FEEDBACKS_FILE = "plugins/marketplace/metadata/feedbacks.json"

marketplace_api = Blueprint("marketplace_api", __name__)
socketio = SocketIO()

# 임시 메모리 저장소 (실제 운영시 DB로 대체)
PLUGINS = {}

UPLOAD_FOLDER = "plugins/marketplace/published/"
ALLOWED_EXTENSIONS = {"zip"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def send_notification(user_email, subject, message):
    # 실제 이메일/알림 발송 로직 (샘플)
    print(f"[알림] {user_email}: {subject} - {message}")


def send_email(user_email, subject, message):
    # 실제 이메일 발송 로직 (샘플)
    print(f"[이메일] {user_email}: {subject} - {message}")


def send_push(user_id, message):
    # 실제 푸시 알림 발송 로직 (샘플)
    print(f"[푸시] {user_id}: {message}")


APPROVAL_LOG = "plugins/marketplace/metadata/approval_log.json"


def log_approval(plugin_id, action, user, reason=None):
    log_entry = {
        "plugin_id": plugin_id,
        "action": action,
        "user": user,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
    }
    try:
        if os.path.exists(APPROVAL_LOG):
            with open(APPROVAL_LOG, "r", encoding="utf-8") as f:
                logs = pyjson.load(f)
        else:
            logs = []
        logs.append(log_entry)
        with open(APPROVAL_LOG, "w", encoding="utf-8") as f:
            pyjson.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[이력 기록 오류] {e}")


def load_json_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return pyjson.load(f)
    return []


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        pyjson.dump(data, f, indent=2, ensure_ascii=False)


@marketplace_api.route("/api/marketplace/upload", methods=["POST"])
def upload_plugin():
    """플러그인 zip 업로드 및 메타정보 추출, 자동 테스트/보안/품질 검사, 승인 대기 등록"""
    if "file" not in request.files:
        return jsonify({"success": False, "msg": "파일이 없습니다."}), 400
    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"success": False, "msg": "지원하지 않는 파일 형식"}), 400
    filename = secure_filename(str(file.filename))
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    # zip에서 plugin.json 추출 및 임시 디렉토리로 압축 해제
    try:
        with zipfile.ZipFile(save_path, "r") as zipf:
            with zipf.open("config/plugin.json") as manifest:
                meta = json.load(manifest)
            # 임시 디렉토리에 압축 해제
            with tempfile.TemporaryDirectory() as tmpdir:
                zipf.extractall(tmpdir)
                # 필수 파일 검사
                required = [
                    os.path.join(tmpdir, "config", "plugin.json"),
                    os.path.join(tmpdir, "backend"),
                ]
                for req in required:
                    if not os.path.exists(req):
                        return reject_plugin_upload(meta, "필수 파일/폴더 누락")
                # 보안 검사(위험 함수/패턴)
                for root, _, files in os.walk(tmpdir):
                    for fname in files:
                        if fname.endswith(".py"):
                            with open(os.path.join(root, fname), encoding="utf-8") as f:
                                code = f.read()
                                if "eval(" in code or "os.system" in code:
                                    return reject_plugin_upload(
                                        meta, "보안 위험 함수 사용"
                                    )
                # 자동 테스트 실행(pytest)
                test_dir = os.path.join(tmpdir, "tests")
                if os.path.exists(test_dir):
                    try:
                        result = subprocess.run(
                            [
                                "pytest",
                                test_dir,
                                "--maxfail=1",
                                "--disable-warnings",
                                "-q",
                            ],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode != 0:
                            return reject_plugin_upload(meta, "자동 테스트 실패")
                    except Exception as e:
                        return reject_plugin_upload(meta, f"테스트 실행 오류: {e}")
    except Exception as e:
        return jsonify({"success": False, "msg": f"메타정보 추출/검사 실패: {e}"}), 400
    plugin_id = meta.get("name", filename)
    PLUGINS[plugin_id] = {
        "meta": meta,
        "status": "pending",
        "uploaded_at": datetime.utcnow().isoformat(),
        "file": filename,
    }
    return jsonify(
        {"success": True, "plugin_id": plugin_id, "status": "pending", "meta": meta}
    )


def reject_plugin_upload(meta, reason):
    """자동 reject 처리 및 알림"""
    plugin_id = meta.get("name", "unknown")
    PLUGINS[plugin_id] = {
        "meta": meta,
        "status": "rejected",
        "uploaded_at": datetime.utcnow().isoformat(),
        "rejected_at": datetime.utcnow().isoformat(),
        "file": None,
    }
    log_approval(plugin_id, "auto_reject", "system", reason)
    send_notification(
        meta.get("author_email", "dev@example.com"),
        "플러그인 자동 거절",
        f"사유: {reason}",
    )
    send_email(
        meta.get("author_email", "dev@example.com"),
        "플러그인 자동 거절",
        f"사유: {reason}",
    )
    send_push(
        meta.get("author_email", "dev@example.com"), f"플러그인 자동 거절: {reason}"
    )
    return jsonify({"success": False, "msg": f"자동 거절: {reason}"}), 400


@marketplace_api.route("/api/marketplace/approve/<plugin_id>", methods=["POST"])
def approve_plugin(plugin_id):
    """플러그인 승인 처리 (총관리자만 가능, 이력 기록, 알림)"""
    if (
        not current_user.is_authenticated
        or getattr(current_user, "role", None) != "OWNER"
    ):
        return jsonify({"success": False, "msg": "총관리자만 승인할 수 있습니다."}), 403
    if plugin_id not in PLUGINS:
        return jsonify({"success": False, "msg": "플러그인 없음"}), 404
    reason = request.json.get("reason") if request.is_json else None
    # 이중 승인 로직
    if PLUGINS[plugin_id].get("status") == "pending":
        PLUGINS[plugin_id]["status"] = "waiting_second_approval"
        PLUGINS[plugin_id]["first_approved_by"] = current_user.username
        PLUGINS[plugin_id]["first_approved_at"] = datetime.utcnow().isoformat()
        log_approval(plugin_id, "first_approve", current_user.username, reason)
        send_notification(
            PLUGINS[plugin_id]["meta"].get("author_email", "dev@example.com"),
            "플러그인 1차 승인",
            f"{plugin_id} 플러그인이 1차 승인되었습니다.\n사유: {reason or '-'}",
        )
        socketio.emit(
            "plugin_approval",
            {
                "plugin_id": plugin_id,
                "action": "first_approve",
                "user": current_user.username,
            },
        )
        return (
            jsonify(
                {
                    "success": True,
                    "plugin_id": plugin_id,
                    "status": "waiting_second_approval",
                    "msg": "1차 승인 완료, 2차 승인 필요",
                }
            ),
            200,
        )
    elif PLUGINS[plugin_id].get("status") == "waiting_second_approval":
        # 2차 승인자는 1차 승인자와 달라야 함
        if PLUGINS[plugin_id].get("first_approved_by") == current_user.username:
            return (
                jsonify(
                    {"success": False, "msg": "2차 승인은 다른 관리자가 해야 합니다."}
                ),
                400,
            )
        PLUGINS[plugin_id]["status"] = "approved"
        PLUGINS[plugin_id]["approved_at"] = datetime.utcnow().isoformat()
        PLUGINS[plugin_id]["second_approved_by"] = current_user.username
        PLUGINS[plugin_id]["second_approved_at"] = datetime.utcnow().isoformat()
        log_approval(plugin_id, "second_approve", current_user.username, reason)
        send_notification(
            PLUGINS[plugin_id]["meta"].get("author_email", "dev@example.com"),
            "플러그인 최종 승인",
            f"{plugin_id} 플러그인이 최종 승인되었습니다.\n사유: {reason or '-'}",
        )
        socketio.emit(
            "plugin_approval",
            {
                "plugin_id": plugin_id,
                "action": "second_approve",
                "user": current_user.username,
            },
        )
        return (
            jsonify(
                {
                    "success": True,
                    "plugin_id": plugin_id,
                    "status": "approved",
                    "msg": "최종 승인 완료",
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "이미 승인되었거나 승인 대기 상태가 아닙니다.",
                }
            ),
            400,
        )


@marketplace_api.route("/api/marketplace/reject/<plugin_id>", methods=["POST"])
def reject_plugin(plugin_id):
    """플러그인 거절 처리 (총관리자만 가능, 이력 기록, 알림)"""
    if (
        not current_user.is_authenticated
        or getattr(current_user, "role", None) != "OWNER"
    ):
        return jsonify({"success": False, "msg": "총관리자만 거절할 수 있습니다."}), 403
    if plugin_id not in PLUGINS:
        return jsonify({"success": False, "msg": "플러그인 없음"}), 404
    PLUGINS[plugin_id]["status"] = "rejected"
    PLUGINS[plugin_id]["rejected_at"] = datetime.utcnow().isoformat()
    reason = request.json.get("reason") if request.is_json else None
    log_approval(plugin_id, "reject", current_user.username, reason)
    # 알림 발송 (샘플)
    send_notification(
        PLUGINS[plugin_id]["meta"].get("author_email", "dev@example.com"),
        "플러그인 거절",
        f"{plugin_id} 플러그인이 거절되었습니다.\n사유: {reason or '-'}",
    )
    # 실시간 알림(WebSocket)
    socketio.emit(
        "plugin_approval",
        {"plugin_id": plugin_id, "action": "reject", "user": current_user.username},
    )
    return jsonify({"success": True, "plugin_id": plugin_id, "status": "rejected"})


@marketplace_api.route("/api/marketplace/status/<plugin_id>", methods=["GET"])
def plugin_status(plugin_id):
    """플러그인 상태/메타정보 조회"""
    if plugin_id not in PLUGINS:
        return jsonify({"success": False, "msg": "플러그인 없음"}), 404
    return jsonify(
        {
            "success": True,
            "plugin_id": plugin_id,
            "status": PLUGINS[plugin_id]["status"],
            "meta": PLUGINS[plugin_id]["meta"],
        }
    )


@marketplace_api.route("/api/marketplace/approval_log", methods=["GET"])
def get_approval_log():
    """플러그인 승인/거절 감사 로그 전체 반환"""
    try:
        if os.path.exists(APPROVAL_LOG):
            with open(APPROVAL_LOG, "r", encoding="utf-8") as f:
                logs = pyjson.load(f)
        else:
            logs = []
        return jsonify(logs)
    except Exception as e:
        return jsonify({"success": False, "msg": f"로그 조회 오류: {e}"}), 500


@marketplace_api.route("/api/marketplace/rating/<plugin_id>", methods=["POST"])
def rate_plugin(plugin_id):
    """별점/리뷰 등록"""
    user = getattr(current_user, "username", "익명")
    data = request.json or {}
    rating = int(data.get("rating", 0))
    review = data.get("review", "")
    if not (1 <= rating <= 5):
        return jsonify({"success": False, "msg": "별점은 1~5점이어야 합니다."}), 400
    ratings = load_json_file(RATINGS_FILE)
    entry = {
        "id": str(uuid.uuid4()),
        "plugin_id": plugin_id,
        "user": user,
        "rating": rating,
        "review": review,
        "timestamp": datetime.utcnow().isoformat(),
    }
    ratings.append(entry)
    save_json_file(RATINGS_FILE, ratings)
    return jsonify({"success": True})


@marketplace_api.route("/api/marketplace/feedback/<plugin_id>", methods=["GET"])
def get_feedbacks(plugin_id):
    """리뷰/버그 신고 목록 조회"""
    ratings = load_json_file(RATINGS_FILE)
    feedbacks = load_json_file(FEEDBACKS_FILE)
    result = [r for r in ratings if r["plugin_id"] == plugin_id]
    result += [f for f in feedbacks if f["plugin_id"] == plugin_id]
    return jsonify({"success": True, "feedbacks": result})


@marketplace_api.route("/api/marketplace/feedback/<plugin_id>", methods=["POST"])
def add_feedback(plugin_id):
    """버그 신고/피드백 등록"""
    user = getattr(current_user, "username", "익명")
    data = request.json or {}
    feedback = data.get("feedback", "")
    if not feedback:
        return jsonify({"success": False, "msg": "내용을 입력하세요."}), 400
    feedbacks = load_json_file(FEEDBACKS_FILE)
    entry = {
        "id": str(uuid.uuid4()),
        "plugin_id": plugin_id,
        "user": user,
        "feedback": feedback,
        "timestamp": datetime.utcnow().isoformat(),
    }
    feedbacks.append(entry)
    save_json_file(FEEDBACKS_FILE, feedbacks)
    return jsonify({"success": True})


@marketplace_api.route("/api/marketplace/stats", methods=["GET"])
def get_marketplace_stats():
    """플러그인 승인률, 처리속도, 관리자별 승인 현황, 플러그인별 평균 별점/피드백 수 등 통계 반환"""
    try:
        # 승인/거절 이력
        if os.path.exists(APPROVAL_LOG):
            with open(APPROVAL_LOG, "r", encoding="utf-8") as f:
                logs = pyjson.load(f)
        else:
            logs = []
        # 별점/피드백
        ratings = load_json_file(RATINGS_FILE)
        feedbacks = load_json_file(FEEDBACKS_FILE)
        # 승인률
        approve_cnt = sum(1 for l in logs if "approve" in l["action"])
        reject_cnt = sum(1 for l in logs if "reject" in l["action"])
        total = approve_cnt + reject_cnt
        approve_rate = (approve_cnt / total * 100) if total else 0
        # 평균 처리속도(1차 승인~2차 승인)
        speed_list = []
        plugin_first = {}
        for l in logs:
            if l["action"] == "first_approve":
                plugin_first[l["plugin_id"]] = l["timestamp"]
            if l["action"] == "second_approve" and l["plugin_id"] in plugin_first:
                from datetime import datetime

                t1 = datetime.fromisoformat(plugin_first[l["plugin_id"]])
                t2 = datetime.fromisoformat(l["timestamp"])
                speed_list.append((t2 - t1).total_seconds())
        avg_speed = sum(speed_list) / len(speed_list) if speed_list else 0
        # 관리자별 승인 건수
        admin_stats = {}
        for l in logs:
            if "approve" in l["action"]:
                admin_stats[l["user"]] = admin_stats.get(l["user"], 0) + 1
        # 플러그인별 평균 별점/피드백 수
        plugin_stats = {}
        for r in ratings:
            pid = r["plugin_id"]
            plugin_stats.setdefault(
                pid, {"rating_sum": 0, "rating_cnt": 0, "feedback_cnt": 0}
            )
            plugin_stats[pid]["rating_sum"] += r["rating"]
            plugin_stats[pid]["rating_cnt"] += 1
        for f in feedbacks:
            pid = f["plugin_id"]
            plugin_stats.setdefault(
                pid, {"rating_sum": 0, "rating_cnt": 0, "feedback_cnt": 0}
            )
            plugin_stats[pid]["feedback_cnt"] += 1
        for pid in plugin_stats:
            if plugin_stats[pid]["rating_cnt"]:
                plugin_stats[pid]["avg_rating"] = round(
                    plugin_stats[pid]["rating_sum"] / plugin_stats[pid]["rating_cnt"], 2
                )
            else:
                plugin_stats[pid]["avg_rating"] = None
        return jsonify(
            {
                "approve_rate": approve_rate,
                "avg_speed_sec": avg_speed,
                "admin_stats": admin_stats,
                "plugin_stats": plugin_stats,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "msg": f"통계 조회 오류: {e}"}), 500


@marketplace_api.route("/api/marketplace/list", methods=["GET"])
def list_plugins():
    """브랜드/업종별 접근 가능한 플러그인 목록 반환"""
    # 예시: current_user.brand_code, current_user.industry_code 사용(없으면 전체)
    brand_code = getattr(current_user, "brand_code", None)
    industry_code = getattr(current_user, "industry_code", None)
    # plugins/marketplace/metadata/marketplace.json에서 목록 불러오기
    meta_path = "plugins/marketplace/metadata/marketplace.json"
    if not os.path.exists(meta_path):
        return jsonify({"success": True, "plugins": []})
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    plugins = list(meta.get("plugins", {}).values())

    # 브랜드/업종 필터링
    def is_accessible(p):
        if brand_code and p.get("brand_code") and p["brand_code"] != brand_code:
            return False
        if (
            industry_code
            and p.get("industry_code")
            and p["industry_code"] != industry_code
        ):
            return False
        return True

    plugins = [p for p in plugins if is_accessible(p)]
    return jsonify({"success": True, "plugins": plugins})


scheduler = BackgroundScheduler()


def send_pending_approval_report():
    """승인 대기 플러그인 목록을 관리자에게 자동 알림"""
    meta_path = "plugins/marketplace/metadata/marketplace.json"
    if not os.path.exists(meta_path):
        return
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    plugins = [
        p for p in meta.get("plugins", {}).values() if p.get("status") == "pending"
    ]
    if not plugins:
        return
    # 관리자 이메일/ID 예시
    admin_email = "admin@your_program.com"
    admin_id = "admin"
    msg = f"승인 대기 플러그인: {[p['name'] for p in plugins]}"
    send_email(admin_email, "승인 대기 플러그인 알림", msg)
    send_push(admin_id, msg)


# 매일 오전 9시에 자동 실행
scheduler.add_job(send_pending_approval_report, "cron", hour=9, minute=0)
scheduler.start()


@marketplace_api.route("/api/marketplace/delegate_admin", methods=["POST"])
def delegate_admin():
    """OWNER가 다른 관리자에게 승인/관리 권한 위임"""
    if (
        not current_user.is_authenticated
        or getattr(current_user, "role", None) != "OWNER"
    ):
        return jsonify({"success": False, "msg": "총관리자만 권한 위임 가능"}), 403
    data = request.json or {}
    target = data.get("target")
    if not target:
        return jsonify({"success": False, "msg": "대상 관리자 지정 필요"}), 400
    # 실제 권한 위임 로직(예: DB/파일에 기록) 필요
    log_approval(
        "system", "delegate_admin", current_user.username, f"위임 대상: {target}"
    )
    send_email(
        f"{target}@your_program.com",
        "관리자 권한 위임",
        f"OWNER가 {target}에게 권한을 위임했습니다.",
    )
    send_push(target, "관리자 권한이 위임되었습니다.")
    return jsonify({"success": True, "msg": f"{target}에게 권한 위임 완료"})


@marketplace_api.route("/api/marketplace/revoke_admin", methods=["POST"])
def revoke_admin():
    """OWNER가 다른 관리자 권한 회수"""
    if (
        not current_user.is_authenticated
        or getattr(current_user, "role", None) != "OWNER"
    ):
        return jsonify({"success": False, "msg": "총관리자만 권한 회수 가능"}), 403
    data = request.json or {}
    target = data.get("target")
    if not target:
        return jsonify({"success": False, "msg": "대상 관리자 지정 필요"}), 400
    # 실제 권한 회수 로직(예: DB/파일에 기록) 필요
    log_approval(
        "system", "revoke_admin", current_user.username, f"회수 대상: {target}"
    )
    send_email(
        f"{target}@your_program.com",
        "관리자 권한 회수",
        f"OWNER가 {target}의 권한을 회수했습니다.",
    )
    send_push(target, "관리자 권한이 회수되었습니다.")
    return jsonify({"success": True, "msg": f"{target}의 권한 회수 완료"})
