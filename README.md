# Asgard
Backend Server for EngageX


This document provides instructions on how to set up the project locally.

## Prerequisites

- Python 3.x
- `virtualenv` (for creating virtual environments)

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/your-django-project.git
   cd your-django-project
   ```

2. Create and activate a virtual environment:
    
    ```bash
    virtualenv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install project dependencies using pip:
    
    ```bash
    pip install -r requirements.txt
   ```

4. Copy the .env.example file and rename it to .env:
    
    ```bash
    cp .env.example .env
   ```


## Database Setup [Postgres]

1. Create database migration:
    
    ```bash
    python manage.py migrate
   ```

