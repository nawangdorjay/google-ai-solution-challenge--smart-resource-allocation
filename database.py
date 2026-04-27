"""
database.py — Member 3 (Backend)
Setup SQLite database to store volunteers, requests, assignments, and match history.
"""

import os
import sqlite3

# Absolute path so the DB file is always found regardless of CWD or Docker
_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(_DIR, "volunteer_lite.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Volunteers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills TEXT NOT NULL,
            city TEXT NOT NULL,
            available BOOLEAN DEFAULT 1
        )
    ''')
    
    # Requests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            city TEXT NOT NULL,
            urgency INTEGER DEFAULT 3
        )
    ''')
    
    # Assignments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_name TEXT NOT NULL,
            request_title TEXT NOT NULL,
            score REAL NOT NULL,
            confidence TEXT NOT NULL
        )
    ''')
    
    # Match History Table for latest 30 requests processed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_title TEXT,
            results TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
