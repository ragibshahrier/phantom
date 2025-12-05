# Phantom Scheduler

> *"Good evening, I am Phantom, your Victorian Ghost Butler. I shall manage your calendar with the utmost discretion and efficiency."*

An AI-powered scheduling assistant that acts as a Victorian Ghost Butler, managing calendars through natural language conversation. Phantom automatically creates, modifies, and optimizes calendar events based on user input, priority rules, and real-time changes.

## Features

- **Natural Language Scheduling**: Create and manage events using conversational language
- **Intelligent Priority Management**: Automatic conflict resolution based on task priorities (Exam > Study > Gym > Social > Gaming)
- **Auto-Optimization**: Automatically rearranges schedule when changes occur
- **Victorian Ghost Butler Persona**: Unique, engaging interaction style
- **Google Calendar Integration**: Seamless synchronization with external calendars
- **RESTful API**: Comprehensive API for programmatic access
- **JWT Authentication**: Secure token-based authentication
- **Property-Based Testing**: Rigorous correctness verification using Hypothesis

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd phantom-scheduler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Populate default categories
python manage.py populate_categories

# Start the development server
python manage.py runserver
```

Visit `http://localhost:8000/api/docs/` to explore the interactive API documentation.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Redis (for Celery task queue)
- PostgreSQL (optional, for production)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phantom-scheduler
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration (see [Configuration](#configuration) section).

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Populate default categories**
   ```bash
   python manage.py populate_categories
   ```
   
   This creates the default task categories:
   - Exam (Priority: 5)
   - Study (Priority: 4)
   - Gym (Priority: 3)
   - Social (Priority: 2)
   - Gaming (Priority: 1)

7. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`.

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Django Settings

```env
# Django secret key (generate a secure random string for production)
SECRET_KEY=your-secret-key-here

# Debug mode (set to False in production)
DEBUG=True

# Allowed hosts (comma-separated list)
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Database Configuration

```env
# Optional: PostgreSQL database URL
# If not set, SQLite will be used (default for development)
# DATABASE_URL=postgresql://user:password@localhost:5432/phantom_db
```

#### JWT Authentication

```env
# JWT token lifetimes (in minutes)
JWT_ACCESS_TOKEN_LIFETIME=15        # 15 minutes
JWT_REFRESH_TOKEN_LIFETIME=10080    # 7 days
```

#### Google Gemini API

```env
# Required for natural language processing
GEMINI_API_KEY=your-gemini-api-key-here
```

Get your API key from: https://makersuite.google.com/app/apikey

#### Google Calendar Integration

```env
# OAuth2 credentials for Google Calendar sync
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

Set up OAuth2 credentials at: https://console.cloud.google.com/

#### Celery & Redis

```env
# Redis connection for async task processing
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### CORS Settings

```env
# Allowed origins for CORS (comma-separated list)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Installing Redis

Redis is required for Celery task queue functionality.

**Windows:**
```bash
# Using Chocolatey
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Starting Celery Worker

In a separate terminal, start the Celery worker:

```bash
# Activate virtual environment first
celery -A phantom worker -l info
```

## Usage

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "name": "John Doe",
    "password": "secure_password123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Create an Event (Natural Language)

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "message": "Schedule a study session tomorrow at 2pm for 2 hours"
  }'
```

Response:
```json
{
  "response": "Very well, I have scheduled a Study session for tomorrow at 2:00 PM, lasting 2 hours. Your calendar has been updated accordingly.",
  "events_created": [
    {
      "id": 1,
      "title": "Study Session",
      "start_time": "2024-01-15T14:00:00Z",
      "end_time": "2024-01-15T16:00:00Z",
      "category": "Study"
    }
  ]
}
```

### 4. Create an Event (Direct API)

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Gym Workout",
    "description": "Leg day",
    "category": 3,
    "start_time": "2024-01-15T18:00:00Z",
    "end_time": "2024-01-15T19:30:00Z"
  }'
```

### 5. List Events

```bash
# Get all events
curl -X GET http://localhost:8000/api/events/ \
  -H "Authorization: Bearer <your_access_token>"

# Filter by date range
curl -X GET "http://localhost:8000/api/events/?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z" \
  -H "Authorization: Bearer <your_access_token>"

# Filter by category
curl -X GET "http://localhost:8000/api/events/?category=4" \
  -H "Authorization: Bearer <your_access_token>"
```

### 6. Update an Event

```bash
curl -X PUT http://localhost:8000/api/events/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Updated Study Session",
    "start_time": "2024-01-15T15:00:00Z",
    "end_time": "2024-01-15T17:00:00Z"
  }'
```

### 7. Delete an Event

```bash
curl -X DELETE http://localhost:8000/api/events/1/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 8. Refresh Access Token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
```

### 9. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
```

## API Documentation

Phantom provides comprehensive interactive API documentation using OpenAPI 3.0 (Swagger).

### Accessing Documentation

Once the server is running, visit:

- **Swagger UI (Interactive)**: http://localhost:8000/api/docs/
- **ReDoc (Read-Only)**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### API Endpoints

#### Authentication (Public)
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and receive JWT tokens
- `POST /api/auth/logout/` - Logout and blacklist refresh token
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token validity

#### Events (Protected)
- `POST /api/events/` - Create new event
- `GET /api/events/` - List events with filters
- `GET /api/events/{id}/` - Retrieve specific event
- `PUT /api/events/{id}/` - Update event
- `PATCH /api/events/{id}/` - Partial update event
- `DELETE /api/events/{id}/` - Delete event

#### Natural Language Interface (Protected)
- `POST /api/chat/` - Process natural language input

#### Categories (Protected)
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create custom category
- `GET /api/categories/{id}/` - Retrieve category

#### User Preferences (Protected)
- `GET /api/preferences/` - Get user preferences
- `PUT /api/preferences/` - Update preferences

#### Google Calendar Integration (Protected)
- `GET /api/integrations/google/connect/` - Initiate OAuth2 flow
- `GET /api/integrations/google/callback/` - OAuth2 callback
- `GET /api/integrations/google/status/` - Check connection status
- `POST /api/integrations/google/disconnect/` - Disconnect account

For detailed documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Testing

Phantom uses a comprehensive testing strategy combining unit tests and property-based tests.

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=scheduler --cov=ai_agent --cov=integrations

# Run specific test file
pytest scheduler/tests.py

# Run specific test
pytest scheduler/tests.py::TestEventModel::test_event_creation
```

### Running Property-Based Tests

Property-based tests use Hypothesis to verify correctness properties across many randomly generated inputs.

```bash
# Run all property-based tests
pytest -k "property" -v

# Run with Hypothesis statistics
pytest --hypothesis-show-statistics

# Run specific property test
pytest scheduler/tests.py::test_property_priority_conflict_resolution
```

### Test Configuration

Test settings are configured in `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = phantom.settings
python_files = tests.py test_*.py *_tests.py
addopts = --hypothesis-show-statistics --hypothesis-seed=random

# Hypothesis settings
hypothesis_profile = dev
hypothesis_max_examples = 100
```

### Test Coverage

The test suite includes:

- **36 Correctness Properties**: Verified using property-based testing
- **Unit Tests**: Model validation, serializers, API endpoints
- **Integration Tests**: End-to-end workflows
- **Edge Cases**: Empty inputs, boundary values, error conditions

### Continuous Integration

All tests must pass before merging to main branch:

```bash
# Pre-commit checks
pytest
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Client/Frontend│
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────────┐
│     Django REST Framework API       │
│  ┌──────────────────────────────┐  │
│  │   ViewSets & Serializers     │  │
│  └──────────────┬───────────────┘  │
└─────────────────┼───────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌──────────────────┐
│  LangChain      │  │   Scheduling     │
│  AI Agent       │◄─┤   Engine         │
│  (Gemini API)   │  │                  │
└────────┬────────┘  └────────┬─────────┘
         │                    │
         ▼                    ▼
┌──────────────────────────────────────┐
│         Django ORM / Models          │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│         Database (SQLite/PostgreSQL) │
└──────────────────────────────────────┘
```

### Project Structure

```
phantom-scheduler/
├── phantom/              # Django project settings
│   ├── settings.py       # Configuration
│   ├── urls.py           # URL routing
│   └── celery.py         # Celery configuration
├── scheduler/            # Main scheduling app
│   ├── models.py         # Database models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API viewsets
│   ├── services.py       # Business logic
│   └── tests.py          # Tests
├── ai_agent/             # LangChain integration
│   ├── agent.py          # AI agent setup
│   ├── prompts.py        # Prompt templates
│   ├── tools.py          # LangChain tools
│   └── parsers.py        # Output parsers
├── integrations/         # External services
│   ├── google_calendar.py
│   └── sync_service.py
├── logs/                 # Application logs
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── pytest.ini            # Test configuration
└── manage.py             # Django management script
```

### Key Components

1. **Django REST Framework API**: RESTful endpoints for event management
2. **LangChain AI Agent**: Natural language processing using Gemini API
3. **Scheduling Engine**: Priority-based conflict resolution and auto-optimization
4. **Database Layer**: PostgreSQL/SQLite for persistent storage
5. **External Integration**: Google Calendar API synchronization
6. **Celery Task Queue**: Asynchronous task processing

For detailed architecture documentation, see [.kiro/specs/phantom-scheduler/design.md](.kiro/specs/phantom-scheduler/design.md).

## Deployment

### Production Checklist

1. **Security**
   - [ ] Set `DEBUG=False` in production
   - [ ] Generate a strong `SECRET_KEY`
   - [ ] Configure `ALLOWED_HOSTS` properly
   - [ ] Use HTTPS for all connections
   - [ ] Set up CORS correctly
   - [ ] Enable Django security middleware

2. **Database**
   - [ ] Use PostgreSQL instead of SQLite
   - [ ] Set up database backups
   - [ ] Configure connection pooling
   - [ ] Run migrations: `python manage.py migrate`

3. **Static Files**
   - [ ] Collect static files: `python manage.py collectstatic`
   - [ ] Serve static files via CDN or web server

4. **Logging**
   - [ ] Configure log rotation
   - [ ] Set up centralized logging (e.g., Sentry)
   - [ ] Monitor error logs

5. **Performance**
   - [ ] Enable database query optimization
   - [ ] Set up Redis for caching
   - [ ] Configure Celery workers
   - [ ] Use a production WSGI server (Gunicorn, uWSGI)

6. **Monitoring**
   - [ ] Set up health check endpoints
   - [ ] Configure application monitoring
   - [ ] Set up alerts for critical errors

### Deployment with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn phantom.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Deployment with Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "phantom.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:

```bash
docker build -t phantom-scheduler .
docker run -p 8000:8000 --env-file .env phantom-scheduler
```

### Environment-Specific Settings

For production, update `.env`:

```env
DEBUG=False
SECRET_KEY=<generate-strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@db-host:5432/phantom_prod
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Database Migration

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Populate default categories
python manage.py populate_categories
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and small

### Testing Requirements

- All new features must include tests
- Property-based tests for universal properties
- Unit tests for specific examples and edge cases
- All tests must pass before merging

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:

- **Issues**: Open an issue on GitHub
- **Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Specifications**: See [.kiro/specs/phantom-scheduler/](.kiro/specs/phantom-scheduler/)

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/) and [Django REST Framework](https://www.django-rest-framework.org/)
- Natural language processing powered by [LangChain](https://www.langchain.com/) and [Google Gemini](https://deepmind.google/technologies/gemini/)
- Property-based testing with [Hypothesis](https://hypothesis.readthedocs.io/)
- API documentation with [drf-spectacular](https://drf-spectacular.readthedocs.io/)

---

*"Your schedule is in capable hands, I assure you. Now, shall we proceed with your appointments?"* - Phantom
