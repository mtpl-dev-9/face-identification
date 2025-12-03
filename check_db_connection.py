"""Check database connection details"""
from config import Config

print("Database Connection Details:")
print(f"URI: {Config.SQLALCHEMY_DATABASE_URI}")

# Parse the URI
uri = Config.SQLALCHEMY_DATABASE_URI
if "mysql+pymysql://" in uri:
    # Extract details
    parts = uri.replace("mysql+pymysql://", "").split("/")
    credentials = parts[0].split("@")
    user_pass = credentials[0].split(":")
    host_port = credentials[1].split(":")
    
    print(f"Username: {user_pass[0]}")
    print(f"Password: {user_pass[1] if len(user_pass) > 1 else 'No password'}")
    print(f"Host: {host_port[0]}")
    print(f"Port: {host_port[1] if len(host_port) > 1 else '3306'}")
    print(f"Database: {parts[1]}")
    
print("\nUse these details in MySQL Workbench to connect to the same database.")