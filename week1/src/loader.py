import json
import sqlite3

def load_all_jsons(input_dir, output_dir): # loader.py

    print("🥇 Gold:...")
    if not input_dir.exists():
        print(f"{input_dir.name} does not exist!")
        return
    if not input_dir.is_dir():
        print(f"{input_dir.name} is not a directory!")
        return
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        print(f"{output_dir.name}: {error}")
        return

    db_path = output_dir / "jobs.db"
    count = 0
    passed = 0
    with sqlite3.connect(db_path) as db:
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                source_id TEXT PRIMARY KEY,
                job_title TEXT,
                company TEXT,
                description TEXT,
                tech_stack TEXT
            );
        """)
        for path in input_dir.glob("*.json"):
            count += 1
            try:
                data = json.loads(path.read_text(encoding = "utf-8"))
                cur.execute("""           
                    INSERT OR IGNORE INTO jobs (source_id, job_title, company, description)
                    VALUES (?, ?, ?, ?)
                            """,
                    ((data["source_id"]), data["job_title"], data["company"], data["description"]))
                if (cur.rowcount == 0):
                    raise Exception("Duplicate")
                print(f"✅ Inserted: {path.name}")
                passed += 1
            except Exception as error:
                print (f"⏭️ Skipped ({error}) : {path.name}")
    print("📊 Gold Summary:")
    print(f"Total: {count} | Extracted: {passed} | Failed: {count - passed}")

