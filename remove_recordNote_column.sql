-- Remove recordNote column from mtpl_working_records table
-- Run this script in MySQL Workbench to remove the column from existing database

USE mtpl_website;

-- Drop the recordNote column
ALTER TABLE mtpl_working_records DROP COLUMN recordNote;

-- Verify the column has been removed
DESCRIBE mtpl_working_records;

