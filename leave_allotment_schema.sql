-- Leave Allotment Table Schema
-- This table stores leave allocations for users

CREATE TABLE IF NOT EXISTS `mtpl_leave_allotment` (
  `allotmentId` INT NOT NULL AUTO_INCREMENT,
  `allotmentUserId` INT NOT NULL,
  `allotmentLeaveTypeId` INT NOT NULL,
  `allotmentTotal` DECIMAL(5,1) NOT NULL DEFAULT 0,
  `allotmentYear` INT NOT NULL,
  `allotmentAssignedBy` INT DEFAULT NULL,
  `allotmentAssignedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `allotmentUpdatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`allotmentId`),
  KEY `idx_user_year` (`allotmentUserId`, `allotmentYear`),
  KEY `idx_leave_type` (`allotmentLeaveTypeId`),
  CONSTRAINT `fk_allotment_leave_type` FOREIGN KEY (`allotmentLeaveTypeId`) REFERENCES `mtpl_leave_types` (`leaveTypeId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample data (optional)
-- INSERT INTO mtpl_leave_allotment (allotmentUserId, allotmentLeaveTypeId, allotmentTotal, allotmentYear, allotmentAssignedBy)
-- VALUES (1, 1, 4, 2024, 1), (1, 2, 7, 2024, 1), (1, 3, 0.5, 2024, 1);
