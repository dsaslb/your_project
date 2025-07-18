import schedule
import time
import subprocess
from datetime import datetime


def run_backup():
    """?먮룞 諛깆뾽 ?ㅽ뻾"""
    try:
        print(f"Starting backup: {datetime.now()}")

        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/backup_project.ps1",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            print(f"Backup completed successfully: {datetime.now()}")
        else:
            print(f"Backup failed: {result.stderr}")

    except Exception as e:
        print(f"Backup error: {e}")


def main():
    # 留ㅼ씪 ?덈꼍 2?쒖뿉 諛깆뾽 ?ㅽ뻾
    schedule.every().day.at("02:00").do(run_backup)

    # 留ㅼ＜ ?쇱슂???덈꼍 3?쒖뿉 ?꾩껜 諛깆뾽
    schedule.every().sunday.at("03:00").do(run_backup)

    print("Auto backup scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
