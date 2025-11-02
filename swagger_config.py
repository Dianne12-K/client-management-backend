"""
Swagger/OpenAPI Configuration for Client Management API
Place this file in your project root alongside app.py
"""

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "info": {
        "title": "Client Management API",
        "description": "API for managing clients with user authentication and payment tracking. All IDs are UUIDs for enhanced security.",
        "version": "2.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@example.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid", "example": "550e8400-e29b-41d4-a716-446655440000"},
                "email": {"type": "string", "format": "email", "example": "user@example.com"},
                "fullName": {"type": "string", "example": "John Doe"},
                "company": {"type": "string", "example": "Acme Corp"},
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"}
            }
        },
        "Client": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid", "example": "550e8400-e29b-41d4-a716-446655440000"},
                "name": {"type": "string", "example": "Jane Smith"},
                "email": {"type": "string", "format": "email", "example": "jane@example.com"},
                "phone": {"type": "string", "example": "+1234567890"},
                "company": {"type": "string", "example": "Tech Corp"},
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"}
            }
        },
        "Payment": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid", "example": "550e8400-e29b-41d4-a716-446655440000"},
                "amount": {"type": "number", "example": 1000.00},
                "currency": {"type": "string", "example": "USD"},
                "description": {"type": "string", "example": "Monthly service fee"},
                "status": {"type": "string", "example": "completed", "enum": ["pending", "completed", "failed"]},
                "paymentMethod": {"type": "string", "example": "card"},
                "transactionId": {"type": "string", "example": "TXN-ABC123"},
                "clientId": {"type": "string", "format": "uuid", "example": "550e8400-e29b-41d4-a716-446655440000"},
                "clientName": {"type": "string", "example": "Jane Smith"},
                "paymentDate": {"type": "string", "format": "date-time"},
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"}
            }
        },
        "Project": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid",
                    "example": "550e8400-e29b-41d4-a716-446655440000"
                },
                "name": {
                    "type": "string",
                    "example": "Website Redesign"
                },
                "description": {
                    "type": "string",
                    "example": "Complete overhaul of company website"
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "completed", "on_hold", "cancelled"],
                    "example": "active"
                },
                "startDate": {
                    "type": "string",
                    "format": "date-time"
                },
                "endDate": {
                    "type": "string",
                    "format": "date-time"
                },
                "budget": {
                    "type": "number",
                    "example": 50000.00
                },
                "clientId": {
                    "type": "string",
                    "format": "uuid",
                    "example": "550e8400-e29b-41d4-a716-446655440000"
                },
                "clientName": {
                    "type": "string",
                    "example": "Tech Corp"
                },
                "createdAt": {
                    "type": "string",
                    "format": "date-time"
                },
                "updatedAt": {
                    "type": "string",
                    "format": "date-time"
                }
            }
        },
        "Task": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid",
                    "example": "550e8400-e29b-41d4-a716-446655440000"
                },
                "title": {
                    "type": "string",
                    "example": "Design homepage mockup"
                },
                "description": {
                    "type": "string",
                    "example": "Create initial design concepts for the new homepage"
                },
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "completed", "blocked"],
                    "example": "todo"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "example": "medium"
                },
                "dueDate": {
                    "type": "string",
                    "format": "date-time"
                },
                "completedAt": {
                    "type": "string",
                    "format": "date-time"
                },
                "projectId": {
                    "type": "string",
                    "format": "uuid",
                    "example": "550e8400-e29b-41d4-a716-446655440000"
                },
                "projectName": {
                    "type": "string",
                    "example": "Website Redesign"
                },
                "createdAt": {
                    "type": "string",
                    "format": "date-time"
                },
                "updatedAt": {
                    "type": "string",
                    "format": "date-time"
                }
            }
        },

        "SignupRequest": {
            "type": "object",
            "required": ["email", "password", "fullName"],
            "properties": {
                "email": {"type": "string", "format": "email", "example": "user@example.com"},
                "password": {"type": "string", "format": "password", "example": "securePassword123"},
                "fullName": {"type": "string", "example": "John Doe"},
                "company": {"type": "string", "example": "Acme Corp"}
            }
        },
        "LoginRequest": {
            "type": "object",
            "required": ["email", "password"],
            "properties": {
                "email": {"type": "string", "format": "email", "example": "user@example.com"},
                "password": {"type": "string", "format": "password", "example": "securePassword123"}
            }
        },
        "ClientRequest": {
            "type": "object",
            "required": ["name", "email"],
            "properties": {
                "name": {"type": "string", "example": "Jane Smith"},
                "email": {"type": "string", "format": "email", "example": "jane@example.com"},
                "phone": {"type": "string", "example": "+1234567890"},
                "company": {"type": "string", "example": "Tech Corp"}
            }
        },
        "PaymentRequest": {
            "type": "object",
            "required": ["amount", "clientId"],
            "properties": {
                "amount": {"type": "number", "example": 1000.00},
                "currency": {"type": "string", "example": "USD"},
                "description": {"type": "string", "example": "Monthly service fee"},
                "status": {"type": "string", "example": "pending", "enum": ["pending", "completed", "failed"]},
                "paymentMethod": {"type": "string", "example": "card"},
                "clientId": {"type": "string", "format": "uuid", "example": "550e8400-e29b-41d4-a716-446655440000"}
            }
        },
        "Error": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Error message"}
            }
        }
    }
}