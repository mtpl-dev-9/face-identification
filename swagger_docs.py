"""
Swagger API Documentation Specs
Add these docstrings to your API endpoints in app.py
"""

analytics_dashboard_spec = """
Get Dashboard Analytics
---
tags:
  - Analytics
responses:
  200:
    description: Dashboard statistics including today's attendance, weekly and monthly data
    schema:
      type: object
      properties:
        today:
          type: object
          properties:
            total:
              type: integer
            late:
              type: integer
            overtime:
              type: integer
            ontime:
              type: integer
            absent:
              type: integer
        weekly:
          type: array
          items:
            type: object
            properties:
              day:
                type: string
              count:
                type: integer
        monthly:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
              count:
                type: integer
"""

clock_attendance_spec = """
Clock In/Out with Face Recognition
---
tags:
  - Attendance
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - image
        - action
        - latitude
        - longitude
      properties:
        image:
          type: string
          description: Base64 encoded image data
          example: "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
        action:
          type: string
          enum: [clock_in, clock_out]
          description: Clock in or clock out action
          example: "clock_in"
        latitude:
          type: number
          description: User's current latitude
          example: 23.022797
        longitude:
          type: number
          description: User's current longitude
          example: 72.531968
responses:
  200:
    description: Successfully clocked in/out
    schema:
      type: object
      properties:
        success:
          type: boolean
        person:
          type: object
        attendance:
          type: object
        message:
          type: string
        distance_from_office:
          type: number
  400:
    description: Bad request - missing fields or invalid action
  403:
    description: Access denied - IP not allowed or outside geofence
  404:
    description: Unknown face
  422:
    description: No face detected in image
"""

get_holidays_spec = """
Get Holidays for Month
---
tags:
  - Holidays
parameters:
  - name: year
    in: query
    type: integer
    required: false
    description: Year (defaults to current year)
    example: 2025
  - name: month
    in: query
    type: integer
    required: false
    description: Month (1-12, defaults to current month)
    example: 11
responses:
  200:
    description: List of holidays for the specified month
    schema:
      type: object
      properties:
        success:
          type: boolean
        holidays:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              date:
                type: string
                format: date
              name:
                type: string
              is_weekoff:
                type: boolean
"""

add_holiday_spec = """
Add New Holiday
---
tags:
  - Holidays
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - date
        - name
      properties:
        date:
          type: string
          format: date
          description: Holiday date in YYYY-MM-DD format
          example: "2025-12-25"
        name:
          type: string
          description: Holiday name or description
          example: "Christmas"
        is_weekoff:
          type: boolean
          description: Whether this is a week-off
          example: false
responses:
  200:
    description: Holiday added successfully
    schema:
      type: object
      properties:
        success:
          type: boolean
        holiday:
          type: object
  400:
    description: Bad request - missing fields or invalid date format
"""

get_settings_spec = """
Get Office Settings
---
tags:
  - Settings
responses:
  200:
    description: Office location and geofence settings
    schema:
      type: object
      properties:
        latitude:
          type: number
          example: 23.022797
        longitude:
          type: number
          example: 72.531968
        radius:
          type: number
          example: 10000
"""

update_settings_spec = """
Update Office Settings
---
tags:
  - Settings
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      properties:
        latitude:
          type: number
          description: Office latitude
          example: 23.022797
        longitude:
          type: number
          description: Office longitude
          example: 72.531968
        radius:
          type: number
          description: Geofence radius in meters
          example: 50
responses:
  200:
    description: Settings updated successfully
    schema:
      type: object
      properties:
        success:
          type: boolean
        settings:
          type: object
"""

attendance_latest_spec = """
Get Latest Attendance Records
---
tags:
  - Attendance
responses:
  200:
    description: List of latest 20 attendance records
    schema:
      type: object
      properties:
        success:
          type: boolean
        results:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              person_id:
                type: integer
              timestamp:
                type: string
                format: date-time
              status:
                type: string
              clock_in_time:
                type: string
                format: date-time
              clock_out_time:
                type: string
                format: date-time
"""

break_attendance_spec = """
Break In/Out
---
tags:
  - Attendance
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - action
        - latitude
        - longitude
      properties:
        action:
          type: string
          enum: [break_in, break_out]
          description: Break in or break out action
          example: "break_in"
        latitude:
          type: number
          description: User's current latitude
          example: 23.022797
        longitude:
          type: number
          description: User's current longitude
          example: 72.531968
responses:
  200:
    description: Successfully recorded break
    schema:
      type: object
      properties:
        success:
          type: boolean
        attendance:
          type: object
        message:
          type: string
        distance_from_office:
          type: number
  400:
    description: Bad request
  403:
    description: Access denied
"""
