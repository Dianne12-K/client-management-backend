from flask import Blueprint, request, jsonify
from models import db, Task, Project
from middleware import token_required
from datetime import datetime

task_bp = Blueprint('tasks', __name__)

@task_bp.route('', methods=['GET'])
@token_required
def get_tasks(current_user):
    """
    Get All Tasks
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: project_id
        in: query
        type: string
        required: false
        description: Filter tasks by project ID
      - name: status
        in: query
        type: string
        required: false
        description: Filter tasks by status
      - name: priority
        in: query
        type: string
        required: false
        description: Filter tasks by priority
    responses:
      200:
        description: List of tasks
      401:
        description: Unauthorized
    """
    query = Task.query.filter_by(user_id=current_user.id)

    # Filter by project_id if provided
    project_id = request.args.get('project_id')
    if project_id:
        query = query.filter_by(project_id=project_id)

    # Filter by status if provided
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    # Filter by priority if provided
    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority)

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200

@task_bp.route('', methods=['POST'])
@token_required
def add_task(current_user):
    """
    Add New Task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
    responses:
      201:
        description: Task created successfully
      400:
        description: Missing required fields or invalid project
      401:
        description: Unauthorized
      500:
        description: Server error
    """
    data = request.get_json()

    # Validation
    if not data.get('title'):
        return jsonify({'message': 'Task title is required'}), 400

    if not data.get('projectId'):
        return jsonify({'message': 'Project ID is required'}), 400

    # Verify project exists and belongs to user
    project = Project.query.filter_by(id=data['projectId'], user_id=current_user.id).first()
    if not project:
        return jsonify({'message': 'Project not found or does not belong to you'}), 400

    # Parse due date if provided
    due_date = None
    if data.get('dueDate'):
        try:
            due_date = datetime.fromisoformat(data['dueDate'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid due date format'}), 400

    # Create new task
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 'medium'),
        due_date=due_date,
        project_id=data['projectId'],
        user_id=current_user.id
    )

    try:
        db.session.add(new_task)
        db.session.commit()
        return jsonify(new_task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error adding task', 'error': str(e)}), 500

@task_bp.route('/<string:task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    """
    Get Task by ID
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Task details
      401:
        description: Unauthorized
      404:
        description: Task not found
    """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    return jsonify(task.to_dict()), 200

@task_bp.route('/<string:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    """
    Update Task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
    responses:
      200:
        description: Task updated successfully
      400:
        description: Invalid data
      401:
        description: Unauthorized
      404:
        description: Task not found
      500:
        description: Server error
    """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    data = request.get_json()

    # Update fields
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
        # If status is completed, set completed_at
        if data['status'] == 'completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif data['status'] != 'completed':
            task.completed_at = None
    if 'priority' in data:
        task.priority = data['priority']

    # Update due date if provided
    if 'dueDate' in data:
        if data['dueDate']:
            try:
                task.due_date = datetime.fromisoformat(data['dueDate'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Invalid due date format'}), 400
        else:
            task.due_date = None

    # Update project if provided
    if 'projectId' in data:
        project = Project.query.filter_by(id=data['projectId'], user_id=current_user.id).first()
        if not project:
            return jsonify({'message': 'Project not found or does not belong to you'}), 400
        task.project_id = data['projectId']

    try:
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating task', 'error': str(e)}), 500

@task_bp.route('/<string:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    """
    Delete Task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Task deleted successfully
      401:
        description: Unauthorized
      404:
        description: Task not found
      500:
        description: Server error
    """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting task', 'error': str(e)}), 500