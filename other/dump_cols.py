import sqlite3
conn = sqlite3.connect('crime_data.db')
cols = [d[1] for d in conn.execute('PRAGMA table_info(victim_demographics)').fetchall()]
conn.close()
with open('cols.txt', 'w') as f:
    f.write('\n'.join(cols))
