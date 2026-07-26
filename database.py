import sqlite3
from pathlib import Path

DB_PATH = Path("tasks.db")

def init_db():
    """Create database and tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Insert example tasks only if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Learn FastAPI", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Build a database", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Deploy to production", 0))
    
    conn.commit()
    conn.close()

# Call this when your app starts
if __name__ == "__main__":
    init_db()