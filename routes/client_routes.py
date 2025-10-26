from flask import Blueprint, request, jsonify
from models import db, Client
from middleware import token_required

client_bp = Blueprint('clients', __name__)

@client_bp.route('', methods=['GET'])
@token_required
def get_clients(current_user):
    """
    Get All Clients
    ---
    tags:
      - Clients
    security:
      - Bearer: []
    responses:
      200:
        description: List of clients
        schema:
          type: array
          items:
            $ref: '#/definitions/Client'
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
    """
    clients = Client.query.filter_by(user_id=current_user.id).order_by(Client.created_at.desc()).all()
    return jsonify([client.to_dict() for client in clients]), 200

@client_bp.route('', methods=['POST'])
@token_required
def add_client(current_user):
    """
    Add New Client
    ---
    tags:
      - Clients
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ClientRequest'
    responses:
      201:
        description: Client created successfully
        schema:
          $ref: '#/definitions/Client'
      400:
        description: Missing required fields
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
    data = request.get_json()

    # Validation
    if not data.get('name') or not data.get('email'):
        return jsonify({'message': 'Name and email are required'}), 400

    # Create new client
    new_client = Client(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', ''),
        company=data.get('company', ''),
        user_id=current_user.id
    )

    try:
        db.session.add(new_client)
        db.session.commit()
        return jsonify(new_client.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error adding client', 'error': str(e)}), 500

@client_bp.route('/<string:client_id>', methods=['GET'])
@token_required
def get_client(current_user, client_id):
    """
    Get Client by ID
    ---
    tags:
      - Clients
    security:
      - Bearer: []
    parameters:
      - name: client_id
        in: path
        type: string
        required: true
        description: The client UUID
        example: "550e8400-e29b-41d4-a716-446655440000"
    responses:
      200:
        description: Client details
        schema:
          $ref: '#/definitions/Client'
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Client not found
        schema:
          $ref: '#/definitions/Error'
    """
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first()

    if not client:
        return jsonify({'message': 'Client not found'}), 404

    return jsonify(client.to_dict()), 200

@client_bp.route('/<string:client_id>', methods=['PUT'])
@token_required
def update_client(current_user, client_id):
    """
    Update Client
    ---
    tags:
      - Clients
    security:
      - Bearer: []
    parameters:
      - name: client_id
        in: path
        type: string
        required: true
        description: The client UUID
        example: "550e8400-e29b-41d4-a716-446655440000"
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Jane Smith Updated"
            email:
              type: string
              format: email
              example: "jane.updated@example.com"
            phone:
              type: string
              example: "+1234567890"
            company:
              type: string
              example: "New Tech Corp"
    responses:
      200:
        description: Client updated successfully
        schema:
          $ref: '#/definitions/Client'
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Client not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first()

    if not client:
        return jsonify({'message': 'Client not found'}), 404

    data = request.get_json()

    # Update fields
    if 'name' in data:
        client.name = data['name']
    if 'email' in data:
        client.email = data['email']
    if 'phone' in data:
        client.phone = data['phone']
    if 'company' in data:
        client.company = data['company']

    try:
        db.session.commit()
        return jsonify(client.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating client', 'error': str(e)}), 500

@client_bp.route('/<string:client_id>', methods=['DELETE'])
@token_required
def delete_client(current_user, client_id):
    """
    Delete Client
    ---
    tags:
      - Clients
    security:
      - Bearer: []
    parameters:
      - name: client_id
        in: path
        type: string
        required: true
        description: The client UUID to delete
        example: "550e8400-e29b-41d4-a716-446655440000"
    responses:
      200:
        description: Client deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Client deleted successfully"
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Client not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first()

    if not client:
        return jsonify({'message': 'Client not found'}), 404

    try:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting client', 'error': str(e)}), 500