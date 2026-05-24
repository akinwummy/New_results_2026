from flask import Flask, request, render_template_string
import psycopg2
import os



app = Flask(__name__)

# --- DB CONNECTION ---
def get_db_connection():
    try:
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            raise Exception("DATABASE_URL not set")

        conn = psycopg2.connect(database_url, sslmode="require")
        conn.autocommit = True
        return conn

    except Exception as e:
        print("DB error:", e)
        return None


# --- AUTO CREATE TABLE (IMPORTANT FIX) ---
def init_db():
    conn = get_db_connection()
    if conn:
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

        print("✅ scores table ready")


# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>EEG Results Portal</title>
</head>

<body>

<h2>EEG 326 & EEG 346 Result Checker</h2>

<form method="POST">
  <input type="text" name="matric_no" placeholder="Matric Number" required>
  <input type="submit" value="Check Results">
</form>

{% if result %}

  <h3>{{ result.student_name }} ({{ result.matric_no }})</h3>

  <h4>EEG 326</h4>
  <ul>
    <li>CA: {{ result.ca1 }}</li>
    <li>Exam: {{ result.exam1 }}</li>
    <li>Total: {{ result.total1 }}</li>
  </ul>

  <h4>EEG 346</h4>
  <ul>
    <li>CA: {{ result.ca2 }}</li>
    <li>Exam: {{ result.exam2 }}</li>
    <li>Total: {{ result.total2 }}</li>
  </ul>

{% elif searched %}

  <p><strong>No result found for {{ matric_no }}</strong></p>

{% endif %}

</body>
</html>
"""


# --- ROUTE ---
@app.route('/', methods=['GET', 'POST'])
def index():

    result = None
    searched = False
    matric_no = ""

    if request.method == 'POST':

        matric_no = request.form['matric_no'].strip()
        searched = True

        conn = get_db_connection()

        if conn:
            cur = conn.cursor()

            try:
                cur.execute("""
                    SELECT
                        student_name,
                        matric_no,
                        ca1,
                        exam1,
                        total1,
                        ca2,
                        exam2,
                        total2
                    FROM public.scores
                    WHERE BTRIM(matric_no) = %s
                """, (matric_no,))

                row = cur.fetchone()

            except Exception as e:
                print("Query error:", e)
                row = None

            finally:
                cur.close()
                conn.close()

            if row:
                result = {
                    "student_name": row[0],
                    "matric_no": row[1],
                    "ca1": row[2],
                    "exam1": row[3],
                    "total1": row[4],
                    "ca2": row[5],
                    "exam2": row[6],
                    "total2": row[7],
                }

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        searched=searched,
        matric_no=matric_no
    )


# --- DEBUG ---
@app.route('/debug')
def debug():
    conn = get_db_connection()
    if conn:
        conn.close()
        return "✅ DB Connected"
    return "❌ DB Failed"


# --- CHECK DATA ---
@app.route('/check')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    message = ""

    if request.method == 'POST':
        file = request.files['file']

        if not file:
            return "No file uploaded"

        import csv
        import io

        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        conn = get_db_connection()
        cur = conn.cursor()

        for row in reader:
            cur.execute("""
                INSERT INTO scores (
                    matric_no, student_name,
                    ca1, exam1, total1,
                    ca2, exam2, total2
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
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
                row["ca1"],
                row["exam1"],
                row["total1"],
                row["ca2"],
                row["exam2"],
                row["total2"]
            ))

        conn.commit()
        cur.close()
        conn.close()

        message = "✅ Upload successful"

    return f"""
    <h2>Upload Scores CSV</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Upload</button>
    </form>
    <p>{message}</p>
    """

def check():
    conn = get_db_connection()
    if not conn:
        return "❌ Cannot connect"

    cur = conn.cursor()
    cur.execute("SELECT matric_no, student_name FROM public.scores LIMIT 10;")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return {"sample": data}


# --- APP START ---
if __name__ == '__main__':
    init_db()   # 🔥 THIS FIXES YOUR MAIN PROBLEM
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))