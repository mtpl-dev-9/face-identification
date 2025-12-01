-- Fix Missing Users in mtpl_users Table
-- This script creates user records for biometric entries that don't have corresponding users

-- Insert missing users based on biometric records
INSERT INTO mtpl_users (userId, userFirstName, userLastName, userLogin, userIsActive)
SELECT 
    b.biometricUserId,
    CONCAT('User ', b.biometricUserId) as userFirstName,
    '' as userLastName,
    CONCAT('EMP', LPAD(b.biometricUserId, 4, '0')) as userLogin,
    '1' as userIsActive
FROM mtpl_biometric b
WHERE NOT EXISTS (
    SELECT 1 FROM mtpl_users u WHERE u.userId = b.biometricUserId
)
AND b.biometricIsActive = 1;

-- Verify the fix
SELECT 
    b.biometricId,
    b.biometricUserId,
    u.userFirstName,
    u.userLastName,
    u.userLogin,
    b.biometricCreatedAt
FROM mtpl_biometric b
LEFT JOIN mtpl_users u ON b.biometricUserId = u.userId
WHERE b.biometricIsActive = 1
ORDER BY b.biometricId;
