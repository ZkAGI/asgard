#!/bin/bash

# Apply migrations
python manage.py migrate

# Start the Django server
gunicorn --bind 0.0.0.0:8000 asgard.wsgi:application
