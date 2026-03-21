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
        c.execute("ALTER TABLE user ADD COLUMN company_name VARCHAR(150)")
        c.execute("ALTER TABLE user ADD COLUMN company_details TEXT")
        print("Added company fields to user table.")
    except sqlite3.OperationalError as e:
        print(f"User columns notice: {e}")
        
    try:
        c.execute("ALTER TABLE application ADD COLUMN interview_date DATETIME")
        c.execute("ALTER TABLE application ADD COLUMN offer_letter_filename VARCHAR(200)")
        print("Added interview and offer fields to application table.")
    except sqlite3.OperationalError as e:
        print(f"Application columns notice: {e}")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
