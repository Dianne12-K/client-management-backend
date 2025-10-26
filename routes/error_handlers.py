from flask import jsonify

def register_error_handlers(app):
    """Register error handlers for the Flask app"""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Route not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request'}), 400

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'message': 'Forbidden'}), 403