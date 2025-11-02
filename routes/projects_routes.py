from flask import Blueprint, request, jsonify
from models import db, Project, Client
from middleware import token_required
from datetime import datetime

project_bp = Blueprint('projects', __name__)

@project_bp.route('', methods=['GET'])
@token_required
def get_projects(current_user):
    """
    Get All Projects
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: client_id
        in: query
        type: string
        required: false
        description: Filter projects by client ID
      - name: status
        in: query
        type: string
        required: false
        description: Filter projects by status
    responses:
      200:
        description: List of projects
      401:
        description: Unauthorized
    """
    query = Project.query.filter_by(user_id=current_user.id)

    # Filter by client_id if provided
    client_id = request.args.get('client_id')
    if client_id:
        query = query.filter_by(client_id=client_id)

    # Filter by status if provided
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    projects = query.order_by(Project.created_at.desc()).all()

    # Check if we should include tasks
    include_tasks = request.args.get('include_tasks', 'false').lower() == 'true'

    return jsonify([project.to_dict(include_tasks=include_tasks) for project in projects]), 200

@project_bp.route('', methods=['POST'])
@token_required
def add_project(current_user):
    """
    Add New Project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
    responses:
      201:
        description: Project created successfully
      400:
        description: Missing required fields or invalid client
      401:
        description: Unauthorized
      500:
        description: Server error
    """
    data = request.get_json()

    # Validation
    if not data.get('name'):
        return jsonify({'message': 'Project name is required'}), 400

    if not data.get('clientId'):
        return jsonify({'message': 'Client ID is required'}), 400

    # Verify client exists and belongs to user
    client = Client.query.filter_by(id=data['clientId'], user_id=current_user.id).first()
    if not client:
        return jsonify({'message': 'Client not found or does not belong to you'}), 400

    # Parse dates if provided
    start_date = None
    end_date = None

    if data.get('startDate'):
        try:
            start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid start date format'}), 400

    if data.get('endDate'):
        try:
            end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid end date format'}), 400

    # Create new project
    new_project = Project(
        name=data['name'],
        description=data.get('description', ''),
        status=data.get('status', 'active'),
        start_date=start_date,
        end_date=end_date,
        budget=data.get('budget'),
        client_id=data['clientId'],
        user_id=current_user.id
    )

    try:
        db.session.add(new_project)
        db.session.commit()
        return jsonify(new_project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error adding project', 'error': str(e)}), 500

@project_bp.route('/<string:project_id>', methods=['GET'])
@token_required
def get_project(current_user, project_id):
    """
    Get Project by ID
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: project_id
        in: path
        type: string
        required: true
      - name: include_tasks
        in: query
        type: boolean
        required: false
    responses:
      200:
        description: Project details
      401:
        description: Unauthorized
      404:
        description: Project not found
    """
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

    if not project:
        return jsonify({'message': 'Project not found'}), 404

    include_tasks = request.args.get('include_tasks', 'false').lower() == 'true'
    return jsonify(project.to_dict(include_tasks=include_tasks)), 200

@project_bp.route('/<string:project_id>', methods=['PUT'])
@token_required
def update_project(current_user, project_id):
    """
    Update Project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: project_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
    responses:
      200:
        description: Project updated successfully
      400:
        description: Invalid data
      401:
        description: Unauthorized
      404:
        description: Project not found
      500:
        description: Server error
    """
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

    if not project:
        return jsonify({'message': 'Project not found'}), 404

    data = request.get_json()

    # Update fields
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']
    if 'budget' in data:
        project.budget = data['budget']

    # Update dates if provided
    if 'startDate' in data:
        if data['startDate']:
            try:
                project.start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Invalid start date format'}), 400
        else:
            project.start_date = None

    if 'endDate' in data:
        if data['endDate']:
            try:
                project.end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Invalid end date format'}), 400
        else:
            project.end_date = None

    # Update client if provided
    if 'clientId' in data:
        client = Client.query.filter_by(id=data['clientId'], user_id=current_user.id).first()
        if not client:
            return jsonify({'message': 'Client not found or does not belong to you'}), 400
        project.client_id = data['clientId']

    try:
        db.session.commit()
        return jsonify(project.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating project', 'error': str(e)}), 500

@project_bp.route('/<string:project_id>', methods=['DELETE'])
@token_required
def delete_project(current_user, project_id):
    """
    Delete Project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - name: project_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Project deleted successfully
      401:
        description: Unauthorized
      404:
        description: Project not found
      500:
        description: Server error
    """
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

    if not project:
        return jsonify({'message': 'Project not found'}), 404

    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting project', 'error': str(e)}), 500