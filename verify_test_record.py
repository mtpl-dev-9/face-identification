"""Verify the test record exists"""
from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Check for our test record
            result = conn.execute(text("SELECT * FROM mtpl_leave_allotment WHERE allotmentUserId = 999"))
            record = result.fetchone()
            
            if record:
                print("TEST RECORD FOUND:")
                print(f"ID: {record[0]}")
                print(f"User ID: {record[1]}")
                print(f"Leave Type: {record[2]}")
                print(f"Total: {record[3]}")
                print(f"Year: {record[4]}")
                print("\nThis record should be visible in MySQL Workbench")
                print("if you connect to hostname: mtpl-secondory-server")
            else:
                print("Test record not found")
                
    except Exception as e:
        print(f"Error: {e}")