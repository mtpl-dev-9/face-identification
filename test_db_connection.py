"""
Database Connection Test Script
Run this to verify your MySQL connection is working
"""
import sys
from sqlalchemy import create_engine, text

# Update these values to match your server
DB_USER = "root"
DB_PASSWORD = ""  # Add your password here
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "mtpl_website"

# Build connection string
connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("=" * 60)
print("MySQL Connection Test")
print("=" * 60)
print(f"Connection String: mysql+pymysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
print()

try:
    # Test connection
    print("1. Testing database connection...")
    engine = create_engine(connection_string)
    connection = engine.connect()
    print("   ✓ Connection successful!")
    
    # Test database exists
    print("\n2. Checking database...")
    result = connection.execute(text("SELECT DATABASE()"))
    db_name = result.fetchone()[0]
    print(f"   ✓ Connected to database: {db_name}")
    
    # Check tables
    print("\n3. Checking attendance tables...")
    result = connection.execute(text("SHOW TABLES LIKE 'mtpl_%'"))
    tables = [row[0] for row in result.fetchall()]
    
    required_tables = [
        'mtpl_users',
        'mtpl_biometric',
        'mtpl_attendance',
        'mtpl_attendance_settings',
        'mtpl_allowed_ips',
        'mtpl_holidays'
    ]
    
    for table in required_tables:
        if table in tables:
            print(f"   ✓ {table} exists")
        else:
            print(f"   ✗ {table} MISSING!")
    
    # Check users table
    print("\n4. Checking users...")
    result = connection.execute(text("SELECT COUNT(*) FROM mtpl_users WHERE userIsActive = '1'"))
    user_count = result.fetchone()[0]
    print(f"   ✓ Active users: {user_count}")
    
    # Check settings
    print("\n5. Checking settings...")
    result = connection.execute(text("SELECT COUNT(*) FROM mtpl_attendance_settings"))
    settings_count = result.fetchone()[0]
    print(f"   ✓ Settings configured: {settings_count}")
    
    if settings_count == 0:
        print("   ⚠ Warning: No settings found. Run the SQL schema to insert defaults.")
    
    # Check allowed IPs
    print("\n6. Checking allowed IPs...")
    result = connection.execute(text("SELECT COUNT(*) FROM mtpl_allowed_ips WHERE allowedIpIsActive = 1"))
    ip_count = result.fetchone()[0]
    print(f"   ✓ Allowed IPs: {ip_count}")
    
    if ip_count == 0:
        print("   ⚠ Warning: No allowed IPs. Run the SQL schema to insert defaults.")
    
    connection.close()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour database is ready. You can now start the Flask service:")
    print("  python app.py")
    print()
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING:")
    print("=" * 60)
    
    error_str = str(e).lower()
    
    if "access denied" in error_str:
        print("• Wrong username or password")
        print("  Update DB_USER and DB_PASSWORD in this script")
    elif "unknown database" in error_str:
        print("• Database doesn't exist")
        print("  Create it with: CREATE DATABASE mtpl_website;")
    elif "can't connect" in error_str:
        print("• MySQL server not running")
        print("  Start XAMPP/MySQL service")
    elif "no module named" in error_str:
        print("• Missing Python package")
        print("  Run: pip install PyMySQL sqlalchemy")
    else:
        print("• Check the error message above")
        print("• Verify MySQL is running on the correct port")
        print("• Check firewall settings")
    
    print()
    sys.exit(1)
