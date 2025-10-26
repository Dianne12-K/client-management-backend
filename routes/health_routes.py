from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health Check
    ---
    tags:
      - Health
    responses:
      200:
        description: API is running
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            message:
              type: string
              example: "API is running"
    """
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200