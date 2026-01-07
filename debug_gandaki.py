import sqlite3

def check_gandaki():
    conn = sqlite3.connect('crime_data.db')
    output = []
    try:
        output.append("--- DEBUGGING GANDAKI DATA ---")
        
        # Get all districts in Gandaki
        districts = [r[0] for r in conn.execute("SELECT DISTINCT district FROM main_crime WHERE province = 'Gandaki' ORDER BY district").fetchall()]
        output.append(f"Districts in Gandaki: {districts}")
        
        output.append(f"\n{'District':<20} | {'Total Cases (All Years)':<25}")
        output.append("-" * 50)
        
        for dist in districts:
            total = conn.execute("SELECT SUM(total_cases) FROM main_crime WHERE province='Gandaki' AND district=?", (dist,)).fetchone()[0]
            output.append(f"{dist:<20} | {total:<25}")
            
        output.append("\n--- DETAILED CHECK (Sample Year 2076/77) ---")
        output.append(f"{'District':<20} | {'Crime Type':<30} | {'Cases'}")
        
        # Detailed check for first 3 districts
        for dist in districts[:3]:
            rows = conn.execute("SELECT crime_type, total_cases FROM main_crime WHERE province='Gandaki' AND district=? AND year='2076/77' ORDER BY crime_type LIMIT 5", (dist,)).fetchall()
            for r in rows:
                 output.append(f"{dist:<20} | {r[0]:<30} | {r[1]}")
            output.append("-" * 60)

    finally:
        conn.close()

    with open('gandaki_debug.txt', 'w') as f:
        f.write('\n'.join(output))

if __name__ == "__main__":
    check_gandaki()
