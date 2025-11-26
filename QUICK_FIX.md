# Quick Fix for mtpl_users Table Error

## Error
```
Table 'mtpl_website.mtpl_users' doesn't exist in engine
```

## Solution

### Step 1: Open phpMyAdmin
Go to: `http://localhost/phpmyadmin`

### Step 2: Select Database
Click on `mtpl_website` database in left sidebar

### Step 3: Run SQL
Click on **SQL** tab and paste this:

```sql
CREATE TABLE IF NOT EXISTS mtpl_users (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    userFirstName VARCHAR(100) NOT NULL,
    userLastName VARCHAR(100) NOT NULL,
    userEmployeeCode VARCHAR(50) UNIQUE NOT NULL,
    userEmail VARCHAR(150),
    userPhone VARCHAR(20),
    userIsActive VARCHAR(1) DEFAULT '1',
    userCreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_employee_code (userEmployeeCode),
    INDEX idx_user_is_active (userIsActive)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample users for testing
INSERT INTO mtpl_users (userFirstName, userLastName, userEmployeeCode, userEmail, userIsActive) VALUES
('John', 'Doe', 'EMP001', 'john.doe@example.com', '1'),
('Jane', 'Smith', 'EMP002', 'jane.smith@example.com', '1'),
('Bob', 'Johnson', 'EMP003', 'bob.johnson@example.com', '1');
```

### Step 4: Click "Go"

### Step 5: Run App
```bash
python app.py
```

## Alternative: Import SQL File

1. Open phpMyAdmin
2. Select `mtpl_website` database
3. Click **Import** tab
4. Choose file: `CREATE_MTPL_USERS_TABLE.sql`
5. Click **Go**

Done! The app should now start successfully.
