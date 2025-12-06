-- Rename table and drop recordNote column if it still exists
USE mtpl_website;

-- Rename table mtpl_working_records -> mtpl_working_reports
RENAME TABLE mtpl_working_records TO mtpl_working_reports;

-- Drop recordNote column if it exists (should already be removed in code)
ALTER TABLE mtpl_working_reports DROP COLUMN IF EXISTS recordNote;

-- Verify structure
DESCRIBE mtpl_working_reports;

