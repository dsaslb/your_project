import sqlite3

def check_schedule_table():
    conn = sqlite3.connect('core_db.sqlite3')
    cursor = conn.cursor()
    
    try:
        cursor.execute('PRAGMA table_info(schedule)')
        columns = cursor.fetchall()
        print("Schedule 테이블 구조:")
        for col in columns:
            print(f"  {col}")
    except sqlite3.OperationalError as e:
        print(f"Schedule 테이블이 존재하지 않습니다: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_schedule_table() 