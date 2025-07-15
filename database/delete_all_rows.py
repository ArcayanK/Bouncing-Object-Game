import sqlite3

DB_NAME = "game_stats.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Clear data from tables
c.execute("DELETE FROM UserStats")
c.execute("DELETE FROM GameHierarchy")
c.execute("DELETE FROM CornerKing")

# Reset autoincrement sequence if needed
c.execute("DELETE FROM sqlite_sequence WHERE name='CornerKing'")

conn.commit()
conn.close()
print("✅ All tables cleared!")
