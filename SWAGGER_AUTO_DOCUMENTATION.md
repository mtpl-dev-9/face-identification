# Swagger Auto-Documentation Guide

## How to Add APIs to Swagger Automatically

Any API route in `app.py` will automatically appear in Swagger UI if you add a docstring with `---` separator.

## Basic Pattern

```python
@app.route("/api/your-endpoint", methods=["GET"])
def your_function():
    """
    Your API Title
    ---
    tags:
      - Your Category Name
    responses:
      200:
        description: Success message
    """
    return jsonify({"success": True})
```

## With Parameters

### Query Parameters (GET)
```python
@app.route("/api/users", methods=["GET"])
def get_users():
    """
    Get Users List
    ---
    tags:
      - Users
    parameters:
      - name: status
        in: query
        type: string
        required: false
      - name: page
        in: query
        type: integer
    responses:
      200:
        description: List of users
    """
    return jsonify({"users": []})
```

### Path Parameters
```python
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get User by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User details
    """
    return jsonify({"user": {}})
```

### Body Parameters (POST/PUT)
```python
@app.route("/api/users", methods=["POST"])
def create_user():
    """
    Create New User
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            age:
              type: integer
    responses:
      200:
        description: User created
    """
    return jsonify({"success": True})
```

## Available Tags in Your Project

- **Analytics** - Dashboard and statistics
- **Attendance** - Clock in/out, breaks
- **Holidays** - Holiday management
- **Settings** - Office settings
- **Leave Management** - Leave types, balances, requests

## Parameter Types

- `string` - Text
- `integer` - Whole numbers
- `number` - Decimals (0.5, 1.5)
- `boolean` - true/false
- `array` - Lists
- `object` - JSON objects

## Parameter Locations

- `query` - URL parameters (?param=value)
- `path` - URL path (/api/users/{id})
- `body` - Request body (JSON)
- `header` - HTTP headers

## Quick Example - Add New API

```python
@app.route("/api/departments", methods=["GET"])
def get_departments():
    """
    Get All Departments
    ---
    tags:
      - Departments
    responses:
      200:
        description: List of departments
    """
    departments = Department.query.all()
    return jsonify({"success": True, "departments": [d.to_dict() for d in departments]})
```

**That's it!** Restart Flask and it appears in Swagger at `http://127.0.0.1:5000/api/docs`

## No Docstring = Not in Swagger

Routes without the `---` docstring won't appear in Swagger (like HTML views):

```python
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")  # Won't appear in Swagger
```
