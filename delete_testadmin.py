import sqlite3

conn = sqlite3.connect("instance/restaurant_dev.sqlite3")
cur = conn.cursor()
cur.execute("DELETE FROM users WHERE username = 'testadmin'")
conn.commit()
print("testadmin 계정이 삭제되었습니다.")
conn.close() 