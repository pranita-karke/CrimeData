import sqlite3

db_path = 'crime_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='firs';")
table_exists = cursor.fetchone()

if table_exists:
    print("Table 'firs' exists.")
    # Get schema
    cursor.execute("PRAGMA table_info(firs);")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f" - {col[1]} ({col[2]})")
else:
    print("Table 'firs' does not exist.")

conn.close()
