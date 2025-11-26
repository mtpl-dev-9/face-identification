# Swagger API Documentation Setup Guide

## Installation

### Step 1: Install Required Package

```bash
pip install flasgger
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

### Step 3: Access Swagger UI

Open your browser and navigate to:

```
http://127.0.0.1:5000/api/docs
```

## Features

### Interactive API Documentation
- **Swagger UI**: Beautiful, interactive API documentation
- **Try it out**: Test APIs directly from the browser
- **Request/Response Examples**: See sample requests and responses
- **Schema Validation**: Automatic validation of request/response data

### Available Endpoints

The Swagger UI will automatically document all your API endpoints:

1. **Analytics APIs**
   - `GET /api/analytics/dashboard` - Get dashboard statistics

2. **Person Management APIs**
   - `POST /api/register-face` - Register new person with face
   - `POST /api/register-face-live` - Register person with live camera
   - `DELETE /api/persons/{person_id}` - Delete person

3. **Attendance APIs**
   - `POST /api/attendance/clock` - Clock in/out with face recognition
   - `POST /api/attendance/live-mark` - Mark attendance from live camera
   - `POST /api/attendance/break` - Break in/out
   - `GET /api/attendance/latest` - Get latest attendance records

4. **Settings APIs**
   - `GET /api/settings` - Get office settings
   - `POST /api/settings` - Update office settings
   - `GET /api/allowed-ips` - Get allowed IPs
   - `POST /api/allowed-ips` - Add allowed IP
   - `DELETE /api/allowed-ips/{ip_id}` - Delete allowed IP

5. **Holiday Management APIs**
   - `GET /api/holidays` - Get holidays for month
   - `POST /api/holidays` - Add new holiday
   - `DELETE /api/holidays/{holiday_id}` - Delete holiday

## Adding Documentation to Endpoints

To add detailed documentation to any endpoint, use docstrings with YAML format:

```python
@app.route("/api/example", methods=["POST"])
def api_example():
    """
    Example API Endpoint
    ---
    tags:
      - Example
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
            age:
              type: integer
              example: 30
    responses:
      200:
        description: Success response
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
      400:
        description: Bad request
    """
    # Your code here
    pass
```

## Customization

### Change Swagger UI URL

Edit `swagger_config.py`:

```python
swagger_config = {
    "specs_route": "/api/docs"  # Change this to your preferred URL
}
```

### Update API Information

Edit `swagger_template` in `swagger_config.py`:

```python
swagger_template = {
    "info": {
        "title": "Your API Title",
        "description": "Your API Description",
        "version": "1.0.0"
    }
}
```

## Testing APIs

### Using Swagger UI

1. Navigate to `http://127.0.0.1:5000/api/docs`
2. Click on any endpoint to expand it
3. Click "Try it out" button
4. Fill in the required parameters
5. Click "Execute" to test the API
6. View the response below

### Using cURL

Export API specification and use with cURL:

```bash
curl -X GET http://127.0.0.1:5000/apispec.json
```

### Using Postman

1. Go to Swagger UI: `http://127.0.0.1:5000/api/docs`
2. Copy the API spec URL: `http://127.0.0.1:5000/apispec.json`
3. In Postman, go to Import → Link → Paste URL
4. All endpoints will be imported automatically

## Troubleshooting

### Swagger UI not loading

1. Check if flasgger is installed: `pip show flasgger`
2. Verify swagger_config.py exists
3. Check console for errors

### Endpoints not showing

1. Ensure endpoints return JSON responses
2. Check if routes are registered correctly
3. Restart the Flask application

### CORS Issues

CORS is already configured in the app. If you face issues:

```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## Production Deployment

For production, update `swagger_config.py`:

```python
swagger_template = {
    "host": "your-domain.com",  # Change from 127.0.0.1:5000
    "schemes": ["https"],        # Change from http to https
}
```

## Additional Resources

- Flasgger Documentation: https://github.com/flasgger/flasgger
- Swagger Specification: https://swagger.io/specification/
- OpenAPI 3.0: https://spec.openapis.org/oas/v3.0.0
