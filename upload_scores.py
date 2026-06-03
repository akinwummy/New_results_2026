import csv
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

with open("scores.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cur.execute("""
            INSERT INTO scores (
                matric_no,
                student_name,
                ca1,
                exam1,
                total1,
                ca2,
                exam2,
                total2
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

            ON CONFLICT (matric_no)
            DO UPDATE SET
                student_name = EXCLUDED.student_name,
                ca1 = EXCLUDED.ca1,
                exam1 = EXCLUDED.exam1,
                total1 = EXCLUDED.total1,
                ca2 = EXCLUDED.ca2,
                exam2 = EXCLUDED.exam2,
                total2 = EXCLUDED.total2;
        """, (
            row["matric_no"],
            row["student_name"],
            int(row["ca1"]),
            int(row["exam1"]),
            int(row["total1"]),
            int(row["ca2"]),
            int(row["exam2"]),
            int(row["total2"])
        ))

conn.commit()
cur.close()
conn.close()

print("Upload completed successfully")
