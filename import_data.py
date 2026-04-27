import sqlite3
import pandas as pd
import json
import os
import sys

DB_PATH = "volunteer_lite.db"

def clean_and_insert_volunteers(csv_path):
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return
    
    print(f"Loading volunteers from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Member 1's Cleaning Logic
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("?", "")
    df.dropna(how="all", inplace=True)
    df.fillna("unknown", inplace=True)

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.lower().str.strip()
    
    # Try to find relevant columns dynamically
    name_col = next((c for c in df.columns if 'name' in c), None)
    skill_col = next((c for c in df.columns if 'skill' in c), None)
    city_col = next((c for c in df.columns if 'city' in c or 'location' in c), None)
    avail_col = next((c for c in df.columns if 'available' in c or 'urgency' in c), None)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    for _, row in df.iterrows():
        name = str(row[name_col]).title() if name_col else "Unknown Volunteer"
        skills = [s.strip().title() for s in str(row[skill_col]).split(',')] if skill_col else []
        city = str(row[city_col]).title() if city_col else "Unknown"
        available = 1 if avail_col and 'yes' in str(row[avail_col]) else 1
        
        cursor.execute('''
            INSERT INTO volunteers (name, skills, city, available)
            VALUES (?, ?, ?, ?)
        ''', (name, json.dumps(skills), city, available))
        inserted += 1
        
    conn.commit()
    conn.close()
    print(f"✅ Successfully inserted {inserted} volunteers into the database!")

def clean_and_insert_ngos(csv_path):
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return
    
    print(f"Loading NGO requests from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("?", "")
    df.dropna(how="all", inplace=True)
    df.fillna("unknown", inplace=True)

    org_col = next((c for c in df.columns if 'org' in c or 'ngo' in c or 'name' in c), None)
    skill_col = next((c for c in df.columns if 'skill' in c or 'require' in c), None)
    city_col = next((c for c in df.columns if 'city' in c or 'location' in c), None)
    urgency_col = next((c for c in df.columns if 'urgency' in c), None)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    for _, row in df.iterrows():
        title = str(row[org_col]).title() if org_col else "NGO Request"
        skills = [s.strip().title() for s in str(row[skill_col]).split(',')] if skill_col else []
        city = str(row[city_col]).title() if city_col else "Unknown"
        
        urg_str = str(row[urgency_col]).lower() if urgency_col else "medium"
        urgency = 5 if 'critical' in urg_str else 4 if 'high' in urg_str else 2 if 'low' in urg_str else 3
        
        # Format title to match UI expectations
        formatted_title = f"{title} — {', '.join(skills[:2])}"
        
        cursor.execute('''
            INSERT INTO requests (title, required_skills, city, urgency)
            VALUES (?, ?, ?, ?)
        ''', (formatted_title, json.dumps(skills), city, urgency))
        inserted += 1
        
    conn.commit()
    conn.close()
    print(f"✅ Successfully inserted {inserted} NGO requests into the database!")

if __name__ == "__main__":
    print("=== Lapper Data Pipeline ===")
    if len(sys.argv) < 3:
        print("Usage: python import_data.py <volunteers_csv> <ngos_csv>")
        print("Put 'skip' if you only want to load one. Example: python import_data.py volunteers.csv skip")
        sys.exit(1)
        
    vol_file = sys.argv[1]
    ngo_file = sys.argv[2]
    
    if vol_file.lower() != 'skip':
        clean_and_insert_volunteers(vol_file)
    if ngo_file.lower() != 'skip':
        clean_and_insert_ngos(ngo_file)
