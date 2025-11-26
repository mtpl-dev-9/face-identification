-- ============================================
-- Create mtpl_users table for face attendance system
-- ============================================

USE mtpl_website;

-- Create mtpl_users table if it doesn't exist
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

-- Insert sample users for testing (optional)
INSERT IGNORE INTO mtpl_users (userFirstName, userLastName, userEmployeeCode, userEmail, userIsActive) VALUES
('John', 'Doe', 'EMP001', 'john.doe@example.com', '1'),
('Jane', 'Smith', 'EMP002', 'jane.smith@example.com', '1'),
('Bob', 'Johnson', 'EMP003', 'bob.johnson@example.com', '1');

SELECT 'mtpl_users table created successfully!' as Status;
