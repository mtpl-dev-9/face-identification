"""
Swagger/OpenAPI Configuration for Face Recognition Attendance System
"""

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Face Recognition Attendance System API",
        "description": "Complete API documentation. **To authorize:** 1) Login at /api/auth/login 2) Copy access_token 3) Click Authorize button 4) Enter: Bearer YOUR_TOKEN",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@example.com"
        }
    },
    "host": "127.0.0.1:5000",
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: Bearer YOUR_ACCESS_TOKEN"
        }
    }
}
