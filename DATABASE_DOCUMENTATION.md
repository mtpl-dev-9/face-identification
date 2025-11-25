# Face Attendance System - Database Documentation

## Database Overview

**Database Type:** SQLite  
**ORM:** SQLAlchemy  
**Timezone:** IST (Asia/Kolkata, UTC+5:30)  
**Location:** `instance/attendance.db`

---

## 📋 Table of Contents
1. [Database Schema](#database-schema)
2. [Tables](#tables)
3. [Relationships](#relationships)
4. [Indexes](#indexes)
5. [Data Types](#data-types)
6. [Sample Queries](#sample-queries)

---

## Database Schema

### Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│    persons      │
├─────────────────┤
│ id (PK)         │
│ name            │
│ employee_code   │◄─────┐
│ encoding        │      │
│ created_at      │      │
│ is_active       │      │
└─────────────────┘      │
                         │
                         │ 1:N
                         │
┌─────────────────┐      │
│   attendance    │      │
├─────────────────┤      │
│ id (PK)         │      │
│ person_id (FK)  │──────┘
│ timestamp       │
│ source          │
│ status          │
│ action          │
│ latitude        │
│ longitude       │
│ ip_address      │
│ clock_in_time   │
│ clock_out_time  │
└─────────────────┘

┌─────────────────┐
│    settings     │
├─────────────────┤
│ id (PK)         │
│ key (UNIQUE)    │
│ value           │
│ updated_at      │
└─────────────────┘

┌─────────────────┐
│  allowed_ips    │
├─────────────────┤
│ id (PK)         │
│ ip_address      │
│ description     │
│ is_active       │
│ created_at      │
└─────────────────┘
```

---

## Tables

### 1. persons

Stores registered employees with their face encodings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique person identifier |
| `name` | VARCHAR(120) | NOT NULL | Employee full name |
| `employee_code` | VARCHAR(50) | UNIQUE, NOT NULL | Unique employee code/ID |
| `encoding` | TEXT | NOT NULL | JSON string of 128-dimensional face encoding vector |
| `created_at` | DATETIME | DEFAULT IST NOW | Registration timestamp (IST) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status flag |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `employee_code`

**Sample Data:**
```sql
INSERT INTO persons (name, employee_code, encoding, created_at, is_active)
VALUES ('John Doe', 'EMP001', '[0.123, -0.456, ...]', '2024-01-15 10:30:00', 1);
```

**Notes:**
- `encoding` stores face recognition vector as JSON array
- `is_active` allows soft deletion without removing records
- All timestamps in IST timezone

---

### 2. attendance

Records all attendance events including clock in/out with location and IP tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique attendance record ID |
| `person_id` | INTEGER | FOREIGN KEY → persons.id, NOT NULL | Reference to person |
| `timestamp` | DATETIME | DEFAULT IST NOW, INDEXED | Record creation time (IST) |
| `source` | VARCHAR(50) | DEFAULT 'live_camera' | Attendance source (live_camera, manual, etc.) |
| `status` | VARCHAR(20) | DEFAULT 'present' | Attendance status (present, absent, leave) |
| `action` | VARCHAR(20) | DEFAULT 'clock_in' | Action type (clock_in, clock_out) |
| `latitude` | FLOAT | NULLABLE | GPS latitude coordinate |
| `longitude` | FLOAT | NULLABLE | GPS longitude coordinate |
| `ip_address` | VARCHAR(50) | NULLABLE | Client IP address |
| `clock_in_time` | DATETIME | NULLABLE | Actual clock-in timestamp (IST) |
| `clock_out_time` | DATETIME | NULLABLE | Actual clock-out timestamp (IST) |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `timestamp` (for date range queries)
- FOREIGN KEY on `person_id` references `persons(id)`

**Sample Data:**
```sql
-- Clock In Record
INSERT INTO attendance (person_id, timestamp, action, latitude, longitude, ip_address, clock_in_time)
VALUES (1, '2024-01-15 09:30:00', 'clock_in', 23.022797, 72.531968, '192.168.1.100', '2024-01-15 09:30:00');

-- Clock Out Record (updates existing)
UPDATE attendance 
SET clock_out_time = '2024-01-15 18:30:00', action = 'clock_out'
WHERE id = 1;
```

**Notes:**
- One record per clock-in, updated with clock-out time
- `latitude`/`longitude` validated against geofence
- `ip_address` validated against whitelist
- Late arrival: `clock_in_time.hour >= 10`
- Overtime: `clock_out_time.hour >= 18`

---

### 3. settings

Key-value store for system configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique setting ID |
| `key` | VARCHAR(50) | UNIQUE, NOT NULL | Setting key name |
| `value` | VARCHAR(200) | NOT NULL | Setting value (stored as string) |
| `updated_at` | DATETIME | DEFAULT IST NOW, ON UPDATE IST NOW | Last update timestamp (IST) |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `key`

**Sample Data:**
```sql
INSERT INTO settings (key, value, updated_at) VALUES
('office_latitude', '23.022797', '2024-01-15 10:00:00'),
('office_longitude', '72.531968', '2024-01-15 10:00:00'),
('geofence_radius', '10000', '2024-01-15 10:00:00');
```

**Common Keys:**
- `office_latitude` - Office GPS latitude
- `office_longitude` - Office GPS longitude
- `geofence_radius` - Allowed distance in meters

**Notes:**
- All values stored as strings, cast when retrieved
- `updated_at` auto-updates on modification

---

### 4. allowed_ips

IP address whitelist for access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique IP record ID |
| `ip_address` | VARCHAR(50) | UNIQUE, NOT NULL | IP address (IPv4/IPv6) |
| `description` | VARCHAR(200) | NULLABLE | Description/label for IP |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status flag |
| `created_at` | DATETIME | DEFAULT IST NOW | Creation timestamp (IST) |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `ip_address`

**Sample Data:**
```sql
INSERT INTO allowed_ips (ip_address, description, is_active, created_at) VALUES
('127.0.0.1', 'Localhost', 1, '2024-01-15 10:00:00'),
('192.168.1.100', 'Office Network', 1, '2024-01-15 10:05:00');
```

**Notes:**
- `is_active` allows temporary disable without deletion
- Supports both IPv4 and IPv6 addresses

---

## Relationships

### One-to-Many: persons → attendance

```python
# SQLAlchemy Relationship
class Person(db.Model):
    attendance_records = db.relationship("Attendance", backref="person")

class Attendance(db.Model):
    person_id = db.Column(db.Integer, db.ForeignKey("persons.id"))
    person = db.relationship("Person", backref="attendance_records")
```

**Cascade Behavior:**
- Deleting a person manually deletes all associated attendance records
- No automatic cascade (handled in application logic)

---

## Indexes

### Performance Indexes

1. **attendance.timestamp** - Optimizes date range queries
   ```sql
   CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);
   ```

2. **persons.employee_code** - Unique constraint + fast lookup
   ```sql
   CREATE UNIQUE INDEX idx_persons_employee_code ON persons(employee_code);
   ```

3. **settings.key** - Unique constraint + fast lookup
   ```sql
   CREATE UNIQUE INDEX idx_settings_key ON settings(key);
   ```

4. **allowed_ips.ip_address** - Unique constraint + fast validation
   ```sql
   CREATE UNIQUE INDEX idx_allowed_ips_ip_address ON allowed_ips(ip_address);
   ```

---

## Data Types

### Face Encoding Storage

Face encodings are stored as JSON strings in the `persons.encoding` column:

```json
"[-0.123, 0.456, -0.789, ..., 0.321]"
```

- **Format:** JSON array of 128 floating-point numbers
- **Size:** ~1-2 KB per encoding
- **Precision:** 6 decimal places
- **Library:** dlib face_recognition

**Encoding/Decoding:**
```python
import json
import numpy as np

# Encode
encoding_json = json.dumps(face_encoding.tolist())

# Decode
face_encoding = np.array(json.loads(encoding_json))
```

---

## Sample Queries

### Common Database Operations

#### 1. Get Today's Attendance Count
```sql
SELECT COUNT(*) 
FROM attendance 
WHERE DATE(timestamp) = DATE('now', 'localtime')
  AND clock_in_time IS NOT NULL;
```

#### 2. Get Late Arrivals Today
```sql
SELECT p.name, p.employee_code, a.clock_in_time
FROM attendance a
JOIN persons p ON a.person_id = p.id
WHERE DATE(a.timestamp) = DATE('now', 'localtime')
  AND CAST(strftime('%H', a.clock_in_time) AS INTEGER) >= 10;
```

#### 3. Get Absent Employees Today
```sql
SELECT p.id, p.name, p.employee_code
FROM persons p
WHERE p.is_active = 1
  AND p.id NOT IN (
    SELECT DISTINCT person_id 
    FROM attendance 
    WHERE DATE(timestamp) = DATE('now', 'localtime')
      AND clock_in_time IS NOT NULL
  );
```

#### 4. Calculate Work Duration
```sql
SELECT 
  p.name,
  a.clock_in_time,
  a.clock_out_time,
  ROUND((julianday(a.clock_out_time) - julianday(a.clock_in_time)) * 24, 2) as hours_worked
FROM attendance a
JOIN persons p ON a.person_id = p.id
WHERE a.clock_in_time IS NOT NULL 
  AND a.clock_out_time IS NOT NULL
  AND DATE(a.timestamp) = DATE('now', 'localtime');
```

#### 5. Weekly Attendance Report
```sql
SELECT 
  strftime('%w', timestamp) as day_of_week,
  strftime('%Y-%m-%d', timestamp) as date,
  COUNT(DISTINCT person_id) as attendance_count
FROM attendance
WHERE timestamp >= date('now', '-7 days')
  AND clock_in_time IS NOT NULL
GROUP BY date
ORDER BY date;
```

#### 6. Employee Attendance History
```sql
SELECT 
  DATE(a.timestamp) as date,
  a.clock_in_time,
  a.clock_out_time,
  a.latitude,
  a.longitude,
  a.ip_address,
  CASE 
    WHEN CAST(strftime('%H', a.clock_in_time) AS INTEGER) >= 10 THEN 'Late'
    ELSE 'On Time'
  END as status
FROM attendance a
WHERE a.person_id = 1
ORDER BY a.timestamp DESC
LIMIT 30;
```

#### 7. Get Office Settings
```sql
SELECT key, value 
FROM settings 
WHERE key IN ('office_latitude', 'office_longitude', 'geofence_radius');
```

#### 8. Active IP Whitelist
```sql
SELECT ip_address, description 
FROM allowed_ips 
WHERE is_active = 1;
```

---

## Database Migrations

### Initial Setup
```python
from database import db
from app import create_app

app = create_app()
with app.app_context():
    db.create_all()
```

### Adding New Columns (Example)
```python
# Migration script: migrate_db.py
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        # Add new column
        conn.execute(text(
            "ALTER TABLE attendance ADD COLUMN notes TEXT"
        ))
        conn.commit()
```

---

## Backup and Restore

### Backup Database
```bash
# Copy SQLite file
cp instance/attendance.db instance/attendance_backup_$(date +%Y%m%d).db

# Or use SQLite dump
sqlite3 instance/attendance.db .dump > backup.sql
```

### Restore Database
```bash
# From file copy
cp instance/attendance_backup_20240115.db instance/attendance.db

# From SQL dump
sqlite3 instance/attendance.db < backup.sql
```

---

## Performance Optimization

### Recommended Practices

1. **Use Indexes:** Already implemented on frequently queried columns
2. **Batch Operations:** Use bulk inserts for multiple records
3. **Connection Pooling:** SQLAlchemy handles automatically
4. **Query Optimization:** Use joins instead of multiple queries
5. **Regular Vacuum:** Clean up SQLite database
   ```bash
   sqlite3 instance/attendance.db "VACUUM;"
   ```

### Query Performance Tips

```python
# Good: Single query with join
attendance = db.session.query(Attendance, Person)\
    .join(Person)\
    .filter(Attendance.timestamp >= today_start)\
    .all()

# Bad: N+1 queries
attendance = Attendance.query.filter(Attendance.timestamp >= today_start).all()
for record in attendance:
    person = Person.query.get(record.person_id)  # Separate query each time
```

---

## Data Integrity

### Constraints

1. **Foreign Keys:** Enforced by SQLAlchemy
2. **Unique Constraints:** `employee_code`, `ip_address`, `settings.key`
3. **NOT NULL:** Critical fields like `name`, `employee_code`, `person_id`
4. **Default Values:** Timestamps, status flags

### Validation Rules

- `employee_code`: Must be unique across all persons
- `latitude`: Range -90 to 90
- `longitude`: Range -180 to 180
- `ip_address`: Valid IPv4/IPv6 format
- `clock_out_time`: Must be after `clock_in_time`

---

## Security Considerations

1. **SQL Injection:** Protected by SQLAlchemy ORM
2. **Sensitive Data:** Face encodings stored as JSON (not reversible to images)
3. **Access Control:** IP whitelist in `allowed_ips` table
4. **Audit Trail:** All records timestamped with IST
5. **Soft Deletes:** Use `is_active` flag instead of hard deletes

---

## Maintenance Tasks

### Daily
- Monitor database size
- Check for failed attendance records

### Weekly
- Review attendance patterns
- Update IP whitelist if needed

### Monthly
- Backup database
- Archive old records (optional)
- Run VACUUM to optimize

### Yearly
- Review and clean inactive persons
- Analyze attendance trends

---

## Database Size Estimates

| Records | Persons | Attendance | Total Size |
|---------|---------|------------|------------|
| Small | 50 | 10,000 | ~5 MB |
| Medium | 200 | 50,000 | ~20 MB |
| Large | 1,000 | 250,000 | ~100 MB |

**Note:** Face encodings (~1-2 KB each) are the largest data per person.

---

## Troubleshooting

### Common Issues

**Issue:** Database locked error
```bash
# Solution: Close all connections
sqlite3 instance/attendance.db "PRAGMA busy_timeout = 30000;"
```

**Issue:** Corrupted database
```bash
# Solution: Check integrity
sqlite3 instance/attendance.db "PRAGMA integrity_check;"
```

**Issue:** Slow queries
```bash
# Solution: Analyze and optimize
sqlite3 instance/attendance.db "ANALYZE;"
```

---

## Version History

- **v1.0** - Initial schema with persons and attendance
- **v1.1** - Added clock_in_time, clock_out_time columns
- **v1.2** - Added location tracking (latitude, longitude)
- **v1.3** - Added IP address tracking
- **v1.4** - Added settings and allowed_ips tables
- **v1.5** - Changed timezone to IST

---

## Support

For database-related issues:
1. Check SQLite logs
2. Verify table structure: `sqlite3 instance/attendance.db .schema`
3. Review migration scripts
4. Backup before making changes

---

**Last Updated:** January 2024  
**Database Version:** 1.5
