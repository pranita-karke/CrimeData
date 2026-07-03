import sqlite3
import pandas as pd

def check_demo_data():
    conn = sqlite3.connect('crime_data.db')
    try:
        print("Checking Demographics Data Content...")
        
        # Check Gender (which works)
        gender = conn.execute("SELECT SUM(Victim_Female), SUM(Victim_Male) FROM victim_demographics").fetchone()
        print(f"Gender Sum: Female={gender[0]}, Male={gender[1]}")
        
        # Check Education
        edu_cols = ['Victim_Edu_Illiterate', 'Victim_Edu_Literate', 'Victim_Edu_SchoolLevel', 'Victim_Edu_Plus2', 'Victim_Edu_BachelorPlus']
        for col in edu_cols:
            val = conn.execute(f"SELECT SUM({col}) FROM victim_demographics").fetchone()[0]
            print(f"{col}: {val}")
            
        # Check Relationship
        rel_cols = ['Relationship_Family', 'Relationship_Relative', 'Relationship_Neighbor']
        for col in rel_cols:
             val = conn.execute(f"SELECT SUM({col}) FROM victim_demographics").fetchone()[0]
             print(f"{col}: {val}")

    finally:
        conn.close()

if __name__ == "__main__":
    check_demo_data()
