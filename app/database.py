import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            country VARCHAR(10),
            temperature FLOAT,
            description VARCHAR(200),
            searched_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_search(city, country, temperature, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO searches (city, country, temperature, description) VALUES (%s, %s, %s, %s)",
        (city, country, temperature, description)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_recent_searches(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM searches ORDER BY searched_at DESC LIMIT %s", (limit,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results