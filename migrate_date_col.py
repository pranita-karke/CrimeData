
import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('crime_data.db')
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(firs)")
    columns = [c[1] for c in cursor.fetchall()]
    
    if 'created_at' not in columns:
        print("Adding 'created_at' column...")
        try:
            # Add column with NULL default first (SQLite workaround)
            cursor.execute("ALTER TABLE firs ADD COLUMN created_at TIMESTAMP")
            print("Column added.")
            
            # Backfill
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE firs SET created_at = ?", (now,))
            print(f"Backfilled existing rows with {now}")
            
            conn.commit()
        except Exception as e:
            print(f"Error migrating: {e}")
    else:
        print("'created_at' column already exists.")
        
    conn.close()

if __name__ == "__main__":
    migrate()
