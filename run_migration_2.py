import sqlite3
import os

def migrate():
    db_paths = ['instance/app.db', 'app.db', 'database.db', 'instance/database.db']
    db_path = next((p for p in db_paths if os.path.exists(p)), None)
    
    if not db_path:
        print("Database not found. Skipping migration.")
        return

    print(f"Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE application ADD COLUMN interview_type VARCHAR(50)")
        c.execute("ALTER TABLE application ADD COLUMN interview_location VARCHAR(200)")
        print("Added interview_type and interview_location fields to application table.")
    except sqlite3.OperationalError as e:
        print(f"Columns notice: {e}")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
