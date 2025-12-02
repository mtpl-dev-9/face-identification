"""Check which database Flask is actually connecting to"""
from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check database connection details
        with db.engine.connect() as conn:
            # Get current database name
            result = conn.execute(text("SELECT DATABASE()"))
            current_db = result.fetchone()[0]
            print(f"Flask is connected to database: {current_db}")
            
            # Get connection info
            result = conn.execute(text("SELECT USER(), @@hostname, @@port"))
            user_info = result.fetchone()
            print(f"User: {user_info[0]}")
            print(f"Host: {user_info[1]}")
            print(f"Port: {user_info[2]}")
            
            # Check if table exists in current database
            result = conn.execute(text("SHOW TABLES LIKE 'mtpl_leave_allotment'"))
            table_exists = result.fetchone()
            print(f"Table exists in {current_db}: {table_exists is not None}")
            
            if table_exists:
                # Count records
                result = conn.execute(text("SELECT COUNT(*) FROM mtpl_leave_allotment"))
                count = result.fetchone()[0]
                print(f"Records in table: {count}")
                
                # Show sample data
                result = conn.execute(text("SELECT * FROM mtpl_leave_allotment LIMIT 3"))
                print("Sample data:")
                for row in result:
                    print(f"  {row}")
            else:
                print("Table does not exist in this database!")
                
    except Exception as e:
        print(f"Error: {e}")