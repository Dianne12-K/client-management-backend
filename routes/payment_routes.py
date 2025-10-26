from flask import Blueprint, request, jsonify
from models import db, Payment, Client
from middleware import token_required
import uuid

payment_bp = Blueprint('payments', __name__)

@payment_bp.route('', methods=['GET'])
@token_required
def get_payments(current_user):
    """
    Get All Payments
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - name: client_id
        in: query
        type: string
        required: false
        description: Filter payments by client UUID
      - name: status
        in: query
        type: string
        required: false
        description: Filter payments by status (pending, completed, failed)
    responses:
      200:
        description: List of payments
        schema:
          type: array
          items:
            $ref: '#/definitions/Payment'
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
    """
    query = Payment.query.filter_by(user_id=current_user.id)

    # Filter by client_id if provided
    client_id = request.args.get('client_id')
    if client_id:
        query = query.filter_by(client_id=client_id)

    # Filter by status if provided
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    payments = query.order_by(Payment.payment_date.desc()).all()
    return jsonify([payment.to_dict() for payment in payments]), 200

@payment_bp.route('', methods=['POST'])
@token_required
def add_payment(current_user):
    """
    Add New Payment
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/PaymentRequest'
    responses:
      201:
        description: Payment created successfully
        schema:
          $ref: '#/definitions/Payment'
      400:
        description: Missing required fields or invalid client
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
    if not data.get('amount') or not data.get('clientId'):
        return jsonify({'message': 'Amount and client ID are required'}), 400

    # Verify client belongs to user
    client = Client.query.filter_by(id=data['clientId'], user_id=current_user.id).first()
    if not client:
        return jsonify({'message': 'Client not found'}), 400

    # Generate unique transaction ID
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    # Create new payment
    new_payment = Payment(
        amount=data['amount'],
        currency=data.get('currency', 'USD'),
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        payment_method=data.get('paymentMethod', ''),
        transaction_id=transaction_id,
        client_id=data['clientId'],
        user_id=current_user.id
    )

    try:
        db.session.add(new_payment)
        db.session.commit()
        return jsonify(new_payment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error adding payment', 'error': str(e)}), 500

@payment_bp.route('/<string:payment_id>', methods=['GET'])
@token_required
def get_payment(current_user, payment_id):
    """
    Get Payment by ID
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - name: payment_id
        in: path
        type: string
        required: true
        description: The payment UUID
        example: "550e8400-e29b-41d4-a716-446655440000"
    responses:
      200:
        description: Payment details
        schema:
          $ref: '#/definitions/Payment'
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Payment not found
        schema:
          $ref: '#/definitions/Error'
    """
    payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()

    if not payment:
        return jsonify({'message': 'Payment not found'}), 404

    return jsonify(payment.to_dict()), 200

@payment_bp.route('/<string:payment_id>', methods=['PUT'])
@token_required
def update_payment(current_user, payment_id):
    """
    Update Payment
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - name: payment_id
        in: path
        type: string
        required: true
        description: The payment UUID
        example: "550e8400-e29b-41d4-a716-446655440000"
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              example: 1500.00
            status:
              type: string
              example: "completed"
            description:
              type: string
              example: "Updated payment description"
            paymentMethod:
              type: string
              example: "bank_transfer"
    responses:
      200:
        description: Payment updated successfully
        schema:
          $ref: '#/definitions/Payment'
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Payment not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
    payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()

    if not payment:
        return jsonify({'message': 'Payment not found'}), 404

    data = request.get_json()

    # Update fields
    if 'amount' in data:
        payment.amount = data['amount']
    if 'status' in data:
        payment.status = data['status']
    if 'description' in data:
        payment.description = data['description']
    if 'paymentMethod' in data:
        payment.payment_method = data['paymentMethod']

    try:
        db.session.commit()
        return jsonify(payment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating payment', 'error': str(e)}), 500

@payment_bp.route('/<string:payment_id>', methods=['DELETE'])
@token_required
def delete_payment(current_user, payment_id):
    """
    Delete Payment
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - name: payment_id
        in: path
        type: string
        required: true
        description: The payment UUID to delete
        example: "550e8400-e29b-41d4-a716-446655440000"
    responses:
      200:
        description: Payment deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Payment deleted successfully"
      401:
        description: Unauthorized - Invalid or missing token
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Payment not found
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/Error'
    """
    payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()

    if not payment:
        return jsonify({'message': 'Payment not found'}), 404

    try:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message': 'Payment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting payment', 'error': str(e)}), 500