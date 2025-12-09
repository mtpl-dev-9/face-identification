from app import app, db

with app.app_context():
    with open('daily_attendance_summary.sql', 'r') as f:
        sql = f.read()
    db.session.execute(db.text(sql))
    db.session.commit()
    print("Table created successfully!")
