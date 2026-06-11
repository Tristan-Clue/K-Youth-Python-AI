import sqlite3

def run_data_profile(db_path): # profiler.py    

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    with sqlite3.connect(db_path) as db:
        cursor = db.cursor()

        # Total records
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_records = cursor.fetchone()[0]

        # Null counts
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_title IS NULL")
        null_job_title = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM jobs WHERE company IS NULL")
        null_company = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM jobs WHERE description IS NULL")
        null_description = cursor.fetchone()[0]

        # Average description length
        cursor.execute("SELECT AVG(LENGTH(description)) FROM jobs WHERE description IS NOT NULL")
        avg_desc_length = cursor.fetchone()[0]
        if not (avg_desc_length):
            avg_desc_length = "-"
        if (type(avg_desc_length) == float):
            avg_desc_length = int(avg_desc_length)

        # Shortest description
        cursor.execute("""
            SELECT
                source_id,
                job_title,
                LENGTH(description)
            FROM jobs
            WHERE description IS NOT NULL
            ORDER BY LENGTH(description) ASC
            LIMIT 1
        """)
        shortest = cursor.fetchone()
        if not shortest:
            shortest = ("-", "-", "-")

        # Longest description
        cursor.execute("""
            SELECT
                source_id,
                job_title,
                LENGTH(description)
            FROM jobs
            WHERE description IS NOT NULL
            ORDER BY LENGTH(description) DESC
            LIMIT 1
        """)
        longest = cursor.fetchone()
        if not longest:
            longest = ("-", "-", "-")

        print("--- 🔍 DATA QUALITY REPORT ---")
        print(f"📈 Total Records: {total_records}")
        print(f"❓ Missing Values -> job_title: {null_job_title}, company: {null_company}, description: {null_description}")
        print(f"📝 Avg Description Length: {avg_desc_length} char")
        print(f"⚠️ Shortest Description: {shortest[2]} char")
        print(f"   ↳ source_id: {shortest[0]} | job_title: {shortest[1]}")
        print(f"🚨 Longest Description: {longest[2]} char")
        print(f"   ↳ source_id: {longest[0]} | job_title: {longest[1]}")