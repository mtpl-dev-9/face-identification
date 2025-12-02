"""Check mtpl_leave_allotment table structure and data"""
from app import create_app
from database import db

app = create_app()

with app.app_context():
    try:
        # Check table structure
        with db.engine.connect() as conn:
            result = conn.execute(db.text("DESCRIBE mtpl_leave_allotment"))
            print("Table structure:")
            for row in result:
                print(f"  {row[0]} - {row[1]} - {row[2]} - {row[3]}")
            
            print("\nTable data count:")
            result = conn.execute(db.text("SELECT COUNT(*) FROM mtpl_leave_allotment"))
            count = result.fetchone()[0]
            print(f"  Records: {count}")
            
            if count > 0:
                print("\nSample data:")
                result = conn.execute(db.text("SELECT * FROM mtpl_leave_allotment LIMIT 5"))
                for row in result:
                    print(f"  {row}")
            else:
                print("\nNo data found - table is empty!")
            
    except Exception as e:
        print(f"Error: {e}")