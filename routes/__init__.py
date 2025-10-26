from .auth_routes import auth_bp
from .client_routes import client_bp
from .payment_routes import payment_bp
from .health_routes import health_bp
from .error_handlers import register_error_handlers

__all__ = [
    'auth_bp',
    'client_bp',
    'payment_bp',
    'health_bp',
    'register_error_handlers'
]