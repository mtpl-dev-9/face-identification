"""Quick script to check if leave management tables exist"""
from app import create_app
from database import db

app = create_app()

with app.app_context():
    # Check if tables exist
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("All tables in database:")
    for table in tables:
        print(f"  - {table}")
    
    print("\nLeave management tables:")
    leave_tables = [t for t in tables if 'leave' in t.lower()]
    if leave_tables:
        for table in leave_tables:
            print(f"  ✓ {table}")
    else:
        print("  ✗ No leave tables found!")
        print("\nRun this SQL in phpMyAdmin:")
        print("  mysql -u root -p mtpl_website < leave_management_schema.sql")
