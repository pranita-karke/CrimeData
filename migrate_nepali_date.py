
import sqlite3

def migrate():
    conn = sqlite3.connect('crime_data.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(firs)")
    columns = [c[1] for c in cursor.fetchall()]
    
    if 'nepali_date' not in columns:
        print("Adding 'nepali_date' column...")
        try:
            cursor.execute("ALTER TABLE firs ADD COLUMN nepali_date TEXT")
            print("Column added.")
            conn.commit()
        except Exception as e:
            print(f"Error migrating: {e}")
    else:
        print("'nepali_date' column already exists.")
        
    conn.close()

if __name__ == "__main__":
    migrate()
