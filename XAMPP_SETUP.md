# XAMPP MySQL Setup Guide

## Quick Setup for XAMPP

### Step 1: Start XAMPP Services
1. Open XAMPP Control Panel
2. Start **Apache** (optional, for phpMyAdmin)
3. Start **MySQL**

### Step 2: Create Database via phpMyAdmin
1. Open browser: `http://localhost/phpmyadmin`
2. Click **New** in left sidebar
3. Database name: `face_attendance`
4. Collation: `utf8mb4_unicode_ci`
5. Click **Create**

### Step 3: Import Database Schema
1. Select `face_attendance` database
2. Click **Import** tab
3. Choose file: `DATABASE_SCHEMA_MYSQL.sql`
4. Click **Go**

### Step 4: Install Python Dependencies
```bash
pip install PyMySQL cryptography
```

### Step 5: Verify Configuration
Check `config.py` has XAMPP settings:
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/face_attendance"
```

Note: XAMPP MySQL default has **no password** for root user (empty password after `root:`)

### Step 6: Run Application
```bash
python app.py
```

## Alternative: Manual SQL Import

1. Open Command Prompt in project folder
2. Run:
```bash
"C:\xampp\mysql\bin\mysql.exe" -u root < DATABASE_SCHEMA_MYSQL.sql
```

## Verify Database

Check tables created:
```bash
"C:\xampp\mysql\bin\mysql.exe" -u root -e "USE face_attendance; SHOW TABLES;"
```

Expected output:
```
+---------------------------+
| Tables_in_face_attendance |
+---------------------------+
| allowed_ips               |
| attendance                |
| holidays                  |
| persons                   |
| settings                  |
+---------------------------+
```

## Troubleshooting

### MySQL not starting in XAMPP
- Check if port 3306 is already in use
- Click **Config** → **my.ini** and change port if needed
- Update config.py with new port

### Error: Access denied
- XAMPP default: username=`root`, password=`empty`
- Connection string: `mysql+pymysql://root:@localhost:3306/face_attendance`

### Error: Can't connect to MySQL server
- Ensure MySQL is running in XAMPP Control Panel
- Check if port 3306 is correct

### If you set a password for root
Update config.py:
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:yourpassword@localhost:3306/face_attendance"
```

## XAMPP MySQL Paths

- **MySQL executable**: `C:\xampp\mysql\bin\mysql.exe`
- **Config file**: `C:\xampp\mysql\bin\my.ini`
- **Data directory**: `C:\xampp\mysql\data`
- **phpMyAdmin**: `http://localhost/phpmyadmin`

## Quick Commands

### Start MySQL (if not using Control Panel)
```bash
C:\xampp\mysql\bin\mysqld.exe
```

### Access MySQL CLI
```bash
C:\xampp\mysql\bin\mysql.exe -u root
```

### Create database via CLI
```bash
C:\xampp\mysql\bin\mysql.exe -u root -e "CREATE DATABASE face_attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Import schema via CLI
```bash
C:\xampp\mysql\bin\mysql.exe -u root face_attendance < DATABASE_SCHEMA_MYSQL.sql
```

## Connection String Examples

### XAMPP Default (no password)
```
mysql+pymysql://root:@localhost:3306/face_attendance
```

### XAMPP with password
```
mysql+pymysql://root:password@localhost:3306/face_attendance
```

### XAMPP with custom port
```
mysql+pymysql://root:@localhost:3307/face_attendance
```

## Done! 
Your face attendance system is now using XAMPP MySQL database.
