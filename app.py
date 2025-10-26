from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
from config import Config
from swagger_config import swagger_config, swagger_template
from models import db

# Load environment variables
load_dotenv()

swagger = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Initialize Swagger
    global swagger
    swagger = Swagger(app, config=swagger_config, template=swagger_template)

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.client_routes import client_bp
    from routes.payment_routes import payment_bp
    from routes.health_routes import health_bp

    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(client_bp, url_prefix='/api/clients')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')

    # Register error handlers
    from routes.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Flask server on http://localhost:5000")
    print("📚 API Documentation available at http://localhost:5000/api/docs")
    app.run(debug=True, host='0.0.0.0', port=5000)