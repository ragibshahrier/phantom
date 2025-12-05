# Contributing to Phantom Scheduler

Thank you for your interest in contributing to Phantom Scheduler! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10 or higher installed
- Git installed and configured
- A GitHub account
- Basic knowledge of Django and Django REST Framework
- Familiarity with the project's architecture (see [design.md](.kiro/specs/phantom-scheduler/design.md))

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/phantom-scheduler.git
   cd phantom-scheduler
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/original-owner/phantom-scheduler.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-django hypothesis pytest-cov black flake8 mypy
```

### 3. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your development configuration
```

### 4. Run Migrations

```bash
python manage.py migrate
python manage.py populate_categories
```

### 5. Create Test User

```bash
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

### 7. Start Redis and Celery (in separate terminals)

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A phantom worker -l info
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Fixes**: Fix issues reported in GitHub Issues
2. **New Features**: Implement features from the roadmap or propose new ones
3. **Documentation**: Improve README, API docs, or code comments
4. **Tests**: Add or improve unit tests and property-based tests
5. **Performance**: Optimize existing code
6. **Refactoring**: Improve code quality and maintainability

### Before You Start

1. **Check existing issues**: Look for related issues or discussions
2. **Create an issue**: If none exists, create one describing your proposed change
3. **Get feedback**: Wait for maintainer feedback before starting major work
4. **Claim the issue**: Comment on the issue to let others know you're working on it

### Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   pytest
   
   # Run specific tests
   pytest scheduler/tests.py
   
   # Run with coverage
   pytest --cov=scheduler --cov=ai_agent --cov=integrations
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `perf:` for performance improvements
   - `chore:` for maintenance tasks

5. **Keep your branch updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to GitHub and create a PR from your branch
   - Fill out the PR template completely
   - Link related issues

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: Maximum 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized in three groups (standard library, third-party, local)
- **Docstrings**: Use Google-style docstrings

### Code Formatting

Use `black` for automatic formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Linting

Use `flake8` for linting:

```bash
# Run flake8
flake8 scheduler ai_agent integrations

# Configuration in setup.cfg or .flake8
```

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Optional
from datetime import datetime

def create_event(
    title: str,
    start_time: datetime,
    end_time: datetime,
    category_id: int,
    user_id: int
) -> Event:
    """
    Create a new calendar event.
    
    Args:
        title: Event title
        start_time: Event start datetime
        end_time: Event end datetime
        category_id: ID of the event category
        user_id: ID of the user creating the event
        
    Returns:
        The created Event instance
        
    Raises:
        ValidationError: If event data is invalid
    """
    pass
```

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Django Best Practices

1. **Models**
   - Use descriptive field names
   - Add `help_text` to fields
   - Implement `__str__` method
   - Use `Meta` class for ordering and indexes

2. **Views**
   - Use class-based views (ViewSets)
   - Keep views thin, move logic to services
   - Use serializers for validation

3. **Serializers**
   - Validate data in serializers
   - Use `read_only_fields` appropriately
   - Implement custom validation methods

4. **Services**
   - Put business logic in service classes
   - Keep services focused and testable
   - Use transactions for multi-step operations

## Testing Requirements

### Test Coverage

All contributions must include appropriate tests:

- **New features**: Must include both unit tests and property-based tests
- **Bug fixes**: Must include a test that reproduces the bug
- **Refactoring**: Existing tests must pass
- **Minimum coverage**: 80% for new code

### Unit Tests

Write unit tests for specific examples and edge cases:

```python
import pytest
from django.test import TestCase
from scheduler.models import Event, Category

class TestEventModel(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Study",
            priority_level=4
        )
    
    def test_event_creation(self):
        """Test that events can be created with valid data."""
        event = Event.objects.create(
            title="Study Session",
            category=self.category,
            start_time="2024-01-15T14:00:00Z",
            end_time="2024-01-15T16:00:00Z"
        )
        self.assertEqual(event.title, "Study Session")
        self.assertEqual(event.category, self.category)
    
    def test_event_validation_end_before_start(self):
        """Test that events with end_time before start_time are rejected."""
        with self.assertRaises(ValidationError):
            event = Event(
                title="Invalid Event",
                category=self.category,
                start_time="2024-01-15T16:00:00Z",
                end_time="2024-01-15T14:00:00Z"
            )
            event.full_clean()
```

### Property-Based Tests

Write property-based tests for universal properties:

```python
from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase
from scheduler.models import Event

class TestEventProperties(TestCase):
    @given(
        title=st.text(min_size=1, max_size=200),
        duration=st.integers(min_value=1, max_value=480)
    )
    def test_property_event_duration_invariance(self, title, duration):
        """
        Property: For any event, rescheduling should preserve duration.
        
        Feature: phantom-scheduler, Property 6: Duration and category invariance
        Validates: Requirements 3.4
        """
        # Create event
        event = create_test_event(title=title, duration=duration)
        original_duration = event.duration
        
        # Reschedule event
        new_start = event.start_time + timedelta(hours=1)
        event.start_time = new_start
        event.end_time = new_start + timedelta(minutes=original_duration)
        event.save()
        
        # Verify duration unchanged
        assert event.duration == original_duration
```

### Test Organization

- Place tests in `tests.py` or `test_*.py` files
- Group related tests in classes
- Use descriptive test names: `test_<what>_<condition>_<expected>`
- Use fixtures for common setup

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest scheduler/tests.py

# Run specific test
pytest scheduler/tests.py::TestEventModel::test_event_creation

# Run with coverage
pytest --cov=scheduler --cov-report=html

# Run property-based tests only
pytest -k "property"

# Run with Hypothesis statistics
pytest --hypothesis-show-statistics
```

## Pull Request Process

### Before Submitting

1. **Run all tests**: Ensure all tests pass
   ```bash
   pytest
   ```

2. **Check code style**: Format and lint your code
   ```bash
   black .
   flake8 scheduler ai_agent integrations
   ```

3. **Update documentation**: Update README, docstrings, or API docs if needed

4. **Update CHANGELOG**: Add entry describing your changes (if applicable)

5. **Rebase on main**: Ensure your branch is up to date
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Property-based tests included (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
```

### Review Process

1. **Automated checks**: CI/CD will run tests and linting
2. **Code review**: Maintainers will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

### After Merge

1. **Delete your branch**: Clean up your local and remote branches
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your fork**: Sync with upstream
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

## Issue Guidelines

### Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: OS, Python version, Django version
6. **Logs**: Relevant error messages or logs
7. **Screenshots**: If applicable

### Requesting Features

When requesting features, include:

1. **Use case**: Why is this feature needed?
2. **Description**: Detailed description of the feature
3. **Proposed solution**: How you think it should work
4. **Alternatives**: Other solutions you've considered
5. **Additional context**: Any other relevant information

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested
- `wontfix`: This will not be worked on

## Development Tips

### Debugging

1. **Use Django Debug Toolbar** (development only)
   ```bash
   pip install django-debug-toolbar
   ```

2. **Use pdb for debugging**
   ```python
   import pdb; pdb.set_trace()
   ```

3. **Check logs**
   ```bash
   tail -f logs/phantom.log
   tail -f logs/phantom_errors.log
   ```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush

# Create test data
python manage.py shell
>>> from scheduler.models import Event, Category
>>> # Create test data
```

### API Testing

Use the interactive API documentation:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

Or use curl/httpie:
```bash
# Using httpie
http POST localhost:8000/api/auth/login/ username=test password=test

# Using curl
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

## Questions?

If you have questions:

1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Open a new issue with the `question` label

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Phantom Scheduler! 🎉

---

*"Your contributions are most appreciated, dear colleague. Together, we shall build something truly remarkable."* - Phantom
