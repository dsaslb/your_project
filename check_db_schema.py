import sqlite3

from app import app, db
from models import ReasonTemplate


def check_schedule_table():
    conn = sqlite3.connect("core_db.sqlite3")
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(schedule)")
        columns = cursor.fetchall()
        print("Schedule 테이블 구조:")
        for col in columns:
            print(f"  {col}")
    except sqlite3.OperationalError as e:
        print(f"Schedule 테이블이 존재하지 않습니다: {e}")

    conn.close()


with app.app_context():
    print("ReasonTemplate 테이블 컬럼 확인:")
    for column in ReasonTemplate.__table__.columns:
        print(f"  {column.name}: {column.type}")

    print("\n테이블 존재 여부 확인:")
    try:
        result = db.session.execute("PRAGMA table_info(reason_templates)")
        columns = result.fetchall()
        print(f"reason_templates 테이블 컬럼 수: {len(columns)}")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_schedule_table()
