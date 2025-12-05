#!/bin/bash
# Script to run intelligent scheduling tests

# Activate virtual environment
source venv/bin/activate

# Run the tests
python manage.py test ai_agent.test_intelligent_scheduling --verbosity=2

# Deactivate virtual environment
deactivate
