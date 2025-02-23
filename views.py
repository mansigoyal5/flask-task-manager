from flask import Blueprint, request, jsonify
from models import Task, db
from flask_jwt_extended import jwt_required, get_jwt_identity

task_bp = Blueprint("task", __name__)

@task_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{"id": t.id, "title": t.title, "description": t.description, "status": t.status} for t in tasks])

@task_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    data = request.json
    task = Task(title=data["title"], description=data["description"])
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created successfully"}), 201

@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.json
    task.status = data.get("status", task.status)
    db.session.commit()
    return jsonify({"message": "Task updated successfully"})

@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"})
