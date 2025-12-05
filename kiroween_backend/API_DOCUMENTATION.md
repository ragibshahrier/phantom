# Phantom Scheduler API Documentation

## Overview

The Phantom Scheduler API provides comprehensive interactive documentation using drf-spectacular (OpenAPI 3.0). The documentation is automatically generated from the Django REST Framework views and includes detailed information about all endpoints, request/response formats, and authentication requirements.

## Accessing the Documentation

Once the development server is running, you can access the API documentation at the following URLs:

### Swagger UI (Interactive)
**URL:** `http://localhost:8000/api/docs/`

Swagger UI provides an interactive interface where you can:
- Browse all available API endpoints organized by tags
- View detailed request/response schemas
- Test API endpoints directly from the browser
- Authenticate using JWT tokens
- See example requests and responses

**Features:**
- Deep linking to specific operations
- Persistent authorization (JWT tokens remain active during session)
- Operation ID display for easy reference
- Filtering capabilities to find endpoints quickly

### ReDoc (Read-Only)
**URL:** `http://localhost:8000/api/redoc/`

ReDoc provides a clean, read-only documentation interface with:
- Three-panel layout for easy navigation
- Expandable request/response examples
- Search functionality
- Downloadable OpenAPI specification

### OpenAPI Schema (JSON/YAML)
**URL:** `http://localhost:8000/api/schema/`

The raw OpenAPI 3.0 schema in YAML format. This can be:
- Downloaded for offline use
- Imported into API testing tools (Postman, Insomnia, etc.)
- Used to generate client SDKs
- Integrated into CI/CD pipelines

## API Endpoint Categories

The API is organized into the following categories:

### 1. Authentication
- User registration
- Login (JWT token generation)
- Token refresh
- Logout (token blacklisting)

### 2. Events
- Create calendar events
- List events with filtering (date range, category, priority)
- Retrieve specific events
- Update events
- Delete events

### 3. Categories
- List task categories with priority levels
- Create custom categories
- Retrieve category details

### 4. Chat
- Process natural language scheduling requests
- Retrieve conversation history

### 5. Preferences
- Get user preferences (timezone, default duration, etc.)
- Update user preferences

### 6. Integrations
- Connect Google Calendar (OAuth2)
- Check connection status
- Disconnect Google Calendar

## Using the Interactive Documentation

### Step 1: Start the Server
```bash
python manage.py runserver
```

### Step 2: Open Swagger UI
Navigate to `http://localhost:8000/api/docs/` in your browser.

### Step 3: Authenticate
1. Register a new user account using the `/api/auth/register/` endpoint
2. Login using the `/api/auth/login/` endpoint to receive JWT tokens
3. Click the "Authorize" button at the top of the Swagger UI
4. Enter your access token in the format: `Bearer <your_access_token>`
5. Click "Authorize" to save the token

### Step 4: Test Endpoints
- Click on any endpoint to expand it
- Click "Try it out" to enable the request form
- Fill in the required parameters
- Click "Execute" to send the request
- View the response below

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

Access tokens expire after 15 minutes. Use the refresh token to obtain a new access token without re-authenticating.

## Query Parameters

Many endpoints support query parameters for filtering:

### Events List (`/api/events/`)
- `start_date`: Filter events that end after this date (ISO 8601 format)
- `end_date`: Filter events that start before this date (ISO 8601 format)
- `category`: Filter by category ID
- `priority`: Filter by minimum priority level

Example:
```
GET /api/events/?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z&category=2
```

## Response Formats

All responses are in JSON format. Successful responses include:
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully

Error responses include:
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: External service (AI, Google Calendar) temporarily unavailable

## Generating the Schema

To regenerate the OpenAPI schema file:

```bash
python manage.py spectacular --color --file schema.yml
```

This creates a `schema.yml` file in the project root that can be used with external tools.

## Configuration

The API documentation is configured in `phantom/settings.py`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Phantom Scheduler API',
    'DESCRIPTION': '...',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
}
```

## Testing the Documentation

Run the test script to verify all documentation endpoints are accessible:

```bash
python test_api_docs.py
```

This will check:
- OpenAPI schema endpoint (`/api/schema/`)
- Swagger UI endpoint (`/api/docs/`)
- ReDoc endpoint (`/api/redoc/`)

## Additional Resources

- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [ReDoc Documentation](https://redocly.com/docs/redoc/)

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 8.1**: POST requests to create events return 201 with event details
- **Requirement 8.2**: GET requests return events in JSON format with filtering
- **Requirement 8.3**: PUT requests update events and return updated resource
- **Requirement 8.4**: DELETE requests remove events and return 204 status

All endpoints are fully documented with request/response schemas, authentication requirements, and example usage.
