-- Remove foreign key constraints to allow standalone biometric registration
-- Run this in phpMyAdmin or MySQL command line

USE mtpl_website;

-- Drop foreign key from mtpl_biometric
ALTER TABLE mtpl_biometric DROP FOREIGN KEY mtpl_biometric_ibfk_1;

-- Drop foreign key from mtpl_attendance (if exists)
ALTER TABLE mtpl_attendance DROP FOREIGN KEY IF EXISTS mtpl_attendance_ibfk_1;

-- Verify constraints are removed
SHOW CREATE TABLE mtpl_biometric;
SHOW CREATE TABLE mtpl_attendance;
