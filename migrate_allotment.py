"""Run this to create leave allotment table"""
from app import create_app
from database import db

app = create_app()

with app.app_context():
    # This will create all tables including LeaveAllotment
    db.create_all()
    print("Leave allotment table created successfully!")
