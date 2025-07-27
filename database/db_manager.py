import sqlite3
from datetime import datetime, timezone

DB_NAME = "game_stats.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Game hierarchy tables
    c.execute('''CREATE TABLE IF NOT EXISTS GameHierarchy(
        corner TEXT PRIMARY KEY,
        username TEXT,
        updated_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS CornerKing(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        became_king_at TEXT,
        lost_king_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS UserStats(
        username TEXT PRIMARY KEY,
        attempts INTEGER DEFAULT 0,
        corner_lord_count INTEGER DEFAULT 0,
        corner_king_count INTEGER DEFAULT 0
    )''')

    conn.commit()
    conn.close()

def record_attempt(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO UserStats (username, attempts)
                 VALUES (?, 1)
                 ON CONFLICT(username) DO UPDATE SET attempts = attempts + 1''', (username,))
    conn.commit()
    conn.close()



def update_corner_lord(username, corner):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO GameHierarchy (corner, username, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(corner)
        DO UPDATE SET username = excluded.username,
                      updated_at = excluded.updated_at
    ''', (corner, username, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    print(f"✅ {username} is now Lord of {corner}")

def check_for_corner_king():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT username
        FROM GameHierarchy
        GROUP BY username
        HAVING COUNT(*) = 4
    ''')
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def update_corner_king(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # close previous king
    c.execute('UPDATE CornerKing SET lost_king_at = ? WHERE lost_king_at IS NULL', (datetime.now(timezone.utc).isoformat(),))
    # insert new king
    c.execute('INSERT INTO CornerKing (username, became_king_at) VALUES (?, ?)', (username, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    print(f"👑 {username} is now the Corner King!")


if __name__ == "__main__":
    # Make sure tables exist
    init_db()

    # OPTIONAL: Re-insert default corner rows if needed
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    initial_corners = ["NE", "NW", "SE", "SW"]
    from datetime import datetime
    for corner in initial_corners:
        c.execute('''
            INSERT INTO GameHierarchy (corner, username, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(corner) DO NOTHING
        ''', (corner, "", datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    print("✅ Database initialized and default corners added.")
