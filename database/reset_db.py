import sqlite3

DB_NAME = "game_stats.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# ✅ Clear UserStats completely
c.execute("DELETE FROM UserStats")

# ✅ Reset CornerKing completely
c.execute("DELETE FROM CornerKing")
# Reset autoincrement
c.execute("DELETE FROM sqlite_sequence WHERE name='CornerKing'")

# ✅ Instead of deleting GameHierarchy rows, reset them
c.execute("""
    UPDATE GameHierarchy
    SET username = '',
        updated_at = NULL
""")

conn.commit()
conn.close()
print("✅ All tables cleared but GameHierarchy rows preserved!")
