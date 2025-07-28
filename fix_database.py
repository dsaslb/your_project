import sqlite3

try:
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    
    # level 컬럼 추가
    cursor.execute('ALTER TABLE system_logs ADD COLUMN level VARCHAR(20) DEFAULT "info"')
    conn.commit()
    print('✅ level 컬럼 추가 완료')
    
    # 테이블 구조 확인
    cursor.execute('PRAGMA table_info(system_logs)')
    print('\n📋 system_logs 테이블 구조:')
    for row in cursor.fetchall():
        print(f'  {row}')
    
    conn.close()
    print('\n✅ 데이터베이스 수정 완료')
    
except Exception as e:
    print(f'❌ 오류 발생: {e}')
    if 'duplicate column name' in str(e).lower():
        print('ℹ️ level 컬럼이 이미 존재합니다.')
    conn.close() 