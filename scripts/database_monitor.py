import sqlite3
import json
from datetime import datetime
import os

def check_database_health():
    """?곗씠?곕쿋?댁뒪 ?곹깭 ?뺤씤"""
    try:
        # DB ?곌껐 ?뚯뒪??
        conn = sqlite3.connect("instance/your_program.db")
        cursor = conn.cursor()
        
        # ?뚯씠釉??뺣낫 ?섏쭛
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 媛??뚯씠釉붿쓽 ?덉퐫?????뺤씤
        table_stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_stats[table] = count
        
        # DB ?ш린 ?뺤씤
        db_size = os.path.getsize("instance/your_program.db")
        
        # ?곌껐 ?쒓컙 痢≪젙
        start_time = datetime.now()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        conn.close()
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "tables": table_stats,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "response_time_ms": round(response_time, 2),
            "total_records": sum(table_stats.values())
        }
        
        # 寃곌낵 ???
        with open("logs/database_health.json", "w") as f:
            json.dump(health_data, f, indent=2)
        
        return health_data
        
    except Exception as e:
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }
        
        with open("logs/database_health.json", "w") as f:
            json.dump(error_data, f, indent=2)
        
        return error_data

if __name__ == "__main__":
    result = check_database_health()
    print(json.dumps(result, indent=2))
