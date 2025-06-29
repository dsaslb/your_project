import datetime
import os
import shutil

# 프로젝트 루트 디렉토리를 기준으로 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "restaurant_dev.sqlite3")
BACKUP_DIR = os.path.join(BASE_DIR, "db_backups")


def backup():
    """데이터베이스 파일을 백업합니다."""
    if not os.path.exists(DB_PATH):
        print(f"오류: 데이터베이스 파일이 존재하지 않습니다. 경로: {DB_PATH}")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)

    db_filename = os.path.basename(DB_PATH)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{db_filename}_{timestamp}.bak")

    try:
        shutil.copy2(DB_PATH, backup_file)
        print(f"백업 완료: {backup_file}")
    except Exception as e:
        print(f"백업 중 오류 발생: {e}")


def find_latest_backup():
    """가장 최신 백업 파일을 찾습니다."""
    if not os.path.exists(BACKUP_DIR):
        return None

    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".bak")]
    if not backups:
        return None

    return os.path.join(BACKUP_DIR, max(backups))


def restore(backup_file=None):
    """지정된 백업 파일 또는 최신 백업 파일로 데이터베이스를 복원합니다."""
    if backup_file is None:
        print("백업 파일이 지정되지 않았습니다. 가장 최신 백업 파일을 찾습니다.")
        backup_file = find_latest_backup()

    if not backup_file or not os.path.exists(backup_file):
        print(f"오류: 복원할 백업 파일이 존재하지 않습니다. 경로: {backup_file}")
        return

    try:
        shutil.copy2(backup_file, DB_PATH)
        print(f"복원 완료: '{backup_file}' -> '{DB_PATH}'")
    except Exception as e:
        print(f"복원 중 오류 발생: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "사용법: python backup_restore_sqlite.py [backup|restore] [백업파일경로(옵션)]"
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "backup":
        backup()
    elif command == "restore":
        # 복원할 파일 경로가 주어지면 해당 파일로, 아니면 최신 파일로 복원
        restore_path = sys.argv[2] if len(sys.argv) > 2 else None
        restore(restore_path)
    else:
        print(f"알 수 없는 명령어: {command}")
        print(
            "사용법: python backup_restore_sqlite.py [backup|restore] [백업파일경로(옵션)]"
        )
