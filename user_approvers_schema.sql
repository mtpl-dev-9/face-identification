-- User Approvers System - Assign approvers to users, not requests

-- Table to store which approvers are assigned to each user
CREATE TABLE IF NOT EXISTS `mtpl_user_approvers` (
  `userApproverId` INT NOT NULL AUTO_INCREMENT,
  `userApproverUserId` INT NOT NULL,
  `userApproverApproverId` INT NOT NULL,
  `userApproverIsActive` TINYINT(1) DEFAULT 1,
  `userApproverCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`userApproverId`),
  KEY `idx_user` (`userApproverUserId`),
  KEY `idx_approver` (`userApproverApproverId`),
  UNIQUE KEY `unique_user_approver` (`userApproverUserId`, `userApproverApproverId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample data: Assign approvers to users
INSERT IGNORE INTO mtpl_user_approvers (userApproverUserId, userApproverApproverId) VALUES
(1, 8), (1, 9), (1, 10),  -- User 1 has Admin, HR, Manager approvers
(4, 8), (4, 9),           -- User 4 has Admin, HR approvers
(5, 9), (5, 10);          -- User 5 has HR, Manager approvers