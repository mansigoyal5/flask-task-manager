from datetime import datetime
import datetime

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]  # For Flask-JWT-Extended

jwt = JWTManager(app)
CORS(app)

# Flask Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

users = {}  # Stores user credentials
tasks = []
task_counter = 1
task_id_counter = 1

# User Authentication Routes
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    users[username] = password
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Validate user
    if users.get(username) == password:
        token_payload = {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }
        access_token = create_access_token(identity=username)

        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/tasks", methods=["POST"])
def create_task():
    global task_id_counter
    data = request.json
    title = data.get("title")
    description = data.get("description")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    task = {
        "id": task_id_counter,
        "title": title,
        "description": description,
        "completed": False
    }
    tasks.append(task)
    task_id_counter += 1  # Increment the counter

    return jsonify({"message": "Task created successfully", "task": task}), 201

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = data.get("title", task["title"])
            task["description"] = data.get("description", task["description"])
            task["completed"] = data.get("completed", task["completed"])
            return jsonify({"message": "Task updated successfully", "task": task}), 200
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return jsonify({"message": "Task deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)