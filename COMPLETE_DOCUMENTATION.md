# Face Attendance System - Complete Documentation

## Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Setup Database**
```bash
mysql -u admin -p mtpl_website < complete_database_schema.sql
```

3. **Configure Environment**
- Copy `.env.example` to `.env`
- Update database credentials

4. **Run Application**
```bash
python app.py
```

5. **Access**
- Web UI: http://127.0.0.1:5000
- API Docs: http://127.0.0.1:5000/api/docs

## Features

### Core Features
- Face recognition attendance
- Clock in/out with geofencing
- IP whitelist validation
- Break time tracking
- Holiday management
- Leave management system
- Monthly attendance reports

### Leave Management
- Create leave types (Casual, Sick, etc.)
- Assign leave allotments to users
- Request and approve leaves
- Track leave balance
- Multi-level approval workflow

### Monthly Reports
- Total working hours
- Worked days vs absent days
- Weekly offs and holidays
- On-time vs late entries
- Early outs tracking

## API Endpoints

### Attendance
- `POST /api/attendance/clock` - Clock in/out
- `POST /api/attendance/break` - Break in/out
- `GET /api/attendance/monthly-report` - Generate monthly report

### Leave Management
- `GET /api/leave-creation-form` - Get leave types
- `POST /api/leave-creation-form` - Create leave type
- `GET /api/leave-allotments` - Get leave allotments
- `POST /api/leave-allotments` - Assign leaves
- `POST /api/leave-allotments/bulk` - Bulk assign leaves
- `GET /api/leave-requests` - Get leave requests
- `POST /api/leave-requests` - Create leave request
- `POST /api/leave-requests/{id}/approve` - Approve request
- `POST /api/leave-requests/{id}/reject` - Reject request

### Users
- `GET /api/users` - Get all users
- `POST /api/register-face` - Register face
- `DELETE /api/biometric/{user_id}` - Delete biometric

### Reports
- `GET /api/monthly-reports` - Get saved reports
- `GET /api/attendance/monthly-report` - Generate new report

## Database Tables

### Core Tables
- `mtpl_users` - User information
- `mtpl_biometric` - Face encodings
- `mtpl_attendance` - Attendance records
- `mtpl_holidays` - Holiday calendar

### Leave Tables
- `mtpl_leave_types` - Leave type definitions
- `mtpl_leave_allotment` - Leave allocations
- `mtpl_user_leave_balance` - Leave balance tracking
- `mtpl_leave_requests` - Leave requests

### Approval Tables
- `mtpl_leave_approvers` - Approver definitions
- `mtpl_user_approvers` - User-approver assignments
- `mtpl_leave_approvals` - Approval workflow

### Reports
- `mtpl_monthly_reports` - Monthly attendance reports

## Configuration

### Office Settings
- Latitude/Longitude
- Geofence radius
- IP whitelist

### Leave Settings
- Leave types with properties:
  - Is Paid
  - Is Encashable
  - Require Approval
  - Require Attachment

## Troubleshooting

### Database Connection
```python
python check_database_connection.py
```

### Leave System
```python
python check_leave_tables.py
```

### Test APIs
Use Swagger UI at `/api/docs`

## Support

For issues, check:
1. Database connection
2. Environment variables
3. API documentation
4. Console logs
