import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                country VARCHAR(10),
                temperature FLOAT,
                conditions VARCHAR(200),
                searched_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        logger.info("Database initialised successfully")
    except Exception as e:
        conn.rollback()
        logger.error("Error initialising database: %s", str(e))
    finally:
        cur.close()
        conn.close()


def save_search(city, country, temperature, conditions):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO searches (city, country, temperature, conditions) VALUES (%s, %s, %s, %s)",
        (city, country, temperature, conditions)
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

