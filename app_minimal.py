import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html", persons_count=0, attendance_today=0, absent_count=0)

@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify({"success": True, "users": []})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)