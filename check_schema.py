
import sqlite3

def check_schema():
    conn = sqlite3.connect('crime_data.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(firs)")
    columns = cursor.fetchall()
    print("Columns in 'firs' table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    conn.close()

if __name__ == "__main__":
    check_schema()
