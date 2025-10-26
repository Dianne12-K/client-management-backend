"""
API Documentation Strings
Place this file in your project root alongside app.py
Import and use these docstrings in your route functions
"""

health_check_docs = """
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

signup_docs = """
User Signup
---
tags:
  - Authentication
parameters:
  - name: body
    in: body
    required: true
    schema:
      $ref: '#/definitions/SignupRequest'
responses:
  201:
    description: User created successfully
    schema:
      type: object
      properties:
        message:
          type: string
          example: "User created successfully"
        token:
          type: string
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        user:
          $ref: '#/definitions/User'
  400:
    description: Missing required fields
    schema:
      $ref: '#/definitions/Error'
  409:
    description: User already exists
    schema:
      $ref: '#/definitions/Error'
  500:
    description: Server error
    schema:
      $ref: '#/definitions/Error'
"""

login_docs = """
User Login
---
tags:
  - Authentication
parameters:
  - name: body
    in: body
    required: true
    schema:
      $ref: '#/definitions/LoginRequest'
responses:
  200:
    description: Login successful
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Login successful"
        token:
          type: string
          example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        user:
          $ref: '#/definitions/User'
  400:
    description: Missing required fields
    schema:
      $ref: '#/definitions/Error'
  401:
    description: Invalid email or password
    schema:
      $ref: '#/definitions/Error'
"""

get_clients_docs = """
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

add_client_docs = """
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

get_client_docs = """
Get Client by ID
---
tags:
  - Clients
security:
  - Bearer: []
parameters:
  - name: client_id
    in: path
    type: integer
    required: true
    description: The client ID
    example: 1
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

update_client_docs = """
Update Client
---
tags:
  - Clients
security:
  - Bearer: []
parameters:
  - name: client_id
    in: path
    type: integer
    required: true
    description: The client ID
    example: 1
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

delete_client_docs = """
Delete Client
---
tags:
  - Clients
security:
  - Bearer: []
parameters:
  - name: client_id
    in: path
    type: integer
    required: true
    description: The client ID to delete
    example: 1
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