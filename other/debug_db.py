import sqlite3

def check_data():
    conn = sqlite3.connect('crime_data.db')
    output = []
    try:
        # Get a sample province
        prov = conn.execute("SELECT DISTINCT province FROM main_crime LIMIT 1").fetchone()[0]
        output.append(f"Checking Province: {prov}")
        
        # Get districts
        districts = [r[0] for r in conn.execute("SELECT DISTINCT district FROM main_crime WHERE province = ?", (prov,)).fetchall()]
        output.append(f"Districts found: {districts[:5]}...")
        
        if len(districts) < 2:
            output.append("Not enough districts to compare.")
        else:
            d1 = districts[0]
            d2 = districts[1]
            # Get totals for a specific year
            year = conn.execute("SELECT DISTINCT year FROM main_crime LIMIT 1").fetchone()[0]
            
            output.append(f"Comparing District '{d1}' vs '{d2}' for Year '{year}'")
            
            t1 = conn.execute("SELECT SUM(total_cases) FROM main_crime WHERE province=? AND district=? AND year=?", (prov, d1, year)).fetchone()[0]
            t2 = conn.execute("SELECT SUM(total_cases) FROM main_crime WHERE province=? AND district=? AND year=?", (prov, d2, year)).fetchone()[0]
            
            output.append(f"{d1} Total: {t1}")
            output.append(f"{d2} Total: {t2}")
            
            if t1 == t2:
                output.append("WARNING: Data seems identical between districts!")
            else:
                output.append("Data is different. Filtering should work.")
            
    finally:
        conn.close()
        
    with open('debug_result.txt', 'w') as f:
        f.write('\n'.join(output))

if __name__ == "__main__":
    check_data()
