# MTPL Database Migration Guide

## Database Changes

### Database Name
- **Old**: `face_attendance`
- **New**: `mtpl_website`

### Table Name Changes
| Old Table | New Table |
|-----------|-----------|
| `persons` | `mtpl_biometric` |
| `attendance` | `mtpl_attendance` |
| `settings` | `mtpl_attendance_settings` |
| `allowed_ips` | `mtpl_allowed_ips` |
| `holidays` | `mtpl_holidays` |

### Column Name Changes

#### mtpl_biometric (was persons)
| Old Column | New Column |
|------------|------------|
| `id` | `biometricId` |
| `name` | Removed (uses mtpl_users) |
| `employee_code` | Removed (uses mtpl_users) |
| `encoding` | `biometricEncoding` |
| `created_at` | `biometricCreatedAt` |
| `is_active` | `biometricIsActive` |
| - | `biometricUserId` (NEW - FK to mtpl_users) |

#### mtpl_attendance (was attendance)
| Old Column | New Column |
|------------|------------|
| `id` | `attendanceId` |
| `person_id` | `attendanceUserId` |
| `timestamp` | `attendanceTimestamp` |
| `source` | `attendanceSource` |
| `status` | `attendanceStatus` |
| `action` | `attendanceAction` |
| `latitude` | `attendanceLatitude` |
| `longitude` | `attendanceLongitude` |
| `ip_address` | `attendanceIpAddress` |
| `clock_in_time` | `attendanceClockInTime` |
| `clock_out_time` | `attendanceClockOutTime` |
| `break_in_time` | `attendanceBreakInTime` |
| `break_out_time` | `attendanceBreakOutTime` |

#### mtpl_attendance_settings (was settings)
| Old Column | New Column |
|------------|------------|
| `id` | `settingId` |
| `key` | `settingKey` |
| `value` | `settingValue` |
| `updated_at` | `settingUpdatedAt` |

#### mtpl_allowed_ips (was allowed_ips)
| Old Column | New Column |
|------------|------------|
| `id` | `allowedIpId` |
| `ip_address` | `allowedIpAddress` |
| `description` | `allowedIpDescription` |
| `is_active` | `allowedIpIsActive` |
| `created_at` | `allowedIpCreatedAt` |

#### mtpl_holidays (was holidays)
| Old Column | New Column |
|------------|------------|
| `id` | `holidayId` |
| `date` | `holidayDate` |
| `name` | `holidayName` |
| `is_weekoff` | `holidayIsWeekoff` |
| `created_at` | `holidayCreatedAt` |

## Setup Steps

### 1. Import SQL Schema
```bash
mysql -u root -p mtpl_website < DATABASE_SCHEMA_MYSQL.sql
```

### 2. Update Configuration
Already done in `config.py`:
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/mtpl_website"
```

### 3. Models Updated
All models in `models.py` have been updated to use new schema.

### 4. Registration Flow Change

**Old Flow:**
- Register with name + employee_code + face
- Store in `persons` table

**New Flow:**
- User must exist in `mtpl_users` table first
- Register face with userId
- Store encoding in `mtpl_biometric` table

## Important Notes

1. **User Table Required**: The `mtpl_users` table must exist and contain user data
2. **Foreign Keys**: `mtpl_biometric` and `mtpl_attendance` reference `mtpl_users.userId`
3. **Name Storage**: Names are now stored in `mtpl_users`, not in biometric table
4. **Employee Code**: Stored in `mtpl_users.userEmployeeCode`

## Testing

After migration, test:
1. Face registration with existing userId
2. Clock in/out
3. Break in/out
4. Attendance reports
5. Holiday management
6. Settings management

## Rollback

If needed, restore from backup:
```bash
mysql -u root -p mtpl_website < backup.sql
```
