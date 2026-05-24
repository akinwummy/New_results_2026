import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    exit()

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            matric_no TEXT PRIMARY KEY,
            student_name TEXT,
            ca1 INT,
            exam1 INT,
            total1 INT,
            ca2 INT,
            exam2 INT,
            total2 INT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Table created successfully")

except Exception as e:
    print("❌ Error:", e)