import sqlite3

conn = sqlite3.connect("instance/restaurant_dev.sqlite3")
cur = conn.cursor()
cur.execute("SELECT id, username, email, status FROM users")
rows = cur.fetchall()
print("id | username | email | status")
for row in rows:
    print(row)
conn.close() 