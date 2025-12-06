-- Update standard_working_hours from 9 to 8
-- This query uses the primary key (optionId) to satisfy MySQL safe update mode

USE mtpl_website;

-- Method 1: Using optionId (primary key) - RECOMMENDED
UPDATE mtpl_options 
SET optionValue = '8' 
WHERE optionId = 5 AND optionKey = 'standard_working_hours';

-- Method 2: If you don't know the optionId, first find it:
-- SELECT optionId FROM mtpl_options WHERE optionKey = 'standard_working_hours';

-- Method 3: Alternative using LIMIT (if safe mode is enabled)
-- UPDATE mtpl_options 
-- SET optionValue = '8' 
-- WHERE optionKey = 'standard_working_hours'
-- LIMIT 1;

-- Verify the update
SELECT optionId, optionKey, optionValue 
FROM mtpl_options 
WHERE optionKey = 'standard_working_hours';

