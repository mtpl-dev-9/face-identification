"""
Database migration script to add clock in/out columns
Run this once to update existing database
"""
import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "attendance.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database doesn't exist yet. Will be created on first run.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [col[1] for col in cursor.fetchall()]
    
    migrations = []
    
    if 'action' not in columns:
        migrations.append("ALTER TABLE attendance ADD COLUMN action VARCHAR(20) DEFAULT 'clock_in'")
    if 'latitude' not in columns:
        migrations.append("ALTER TABLE attendance ADD COLUMN latitude FLOAT")
    if 'longitude' not in columns:
        migrations.append("ALTER TABLE attendance ADD COLUMN longitude FLOAT")
    if 'ip_address' not in columns:
        migrations.append("ALTER TABLE attendance ADD COLUMN ip_address VARCHAR(50)")
    if 'clock_in_time' not in columns:
        migrations.append("ALTER TABLE attendance ADD COLUMN clock_in_time DATETIME")
    if 'clock_out_time' not in columns:
        migrations.append("ALTER TABLE attendance ADD COLUMN clock_out_time DATETIME")
    
    if migrations:
        print(f"Running {len(migrations)} migrations...")
        for migration in migrations:
            print(f"  - {migration}")
            cursor.execute(migration)
        conn.commit()
        print("[SUCCESS] Migration completed successfully!")
    else:
        print("[SUCCESS] Database is already up to date!")
    
    # Create settings table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(50) UNIQUE NOT NULL,
            value VARCHAR(200) NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("[SUCCESS] Settings table ready!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allowed_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(200),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("[SUCCESS] Allowed IPs table ready!")
    
    cursor.execute("SELECT COUNT(*) FROM allowed_ips")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO allowed_ips (ip_address, description) VALUES ('127.0.0.1', 'Localhost')")
        cursor.execute("INSERT INTO allowed_ips (ip_address, description) VALUES ('localhost', 'Localhost alias')")
        conn.commit()
        print("[SUCCESS] Default IPs added!")
    
    conn.close()

if __name__ == "__main__":
    migrate()
