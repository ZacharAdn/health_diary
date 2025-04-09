# Health Diary Project

A health diary application built with Django and REST API that allows users to track meals, health metrics, sleep patterns, and receive health insights through data analytics.

## Features

- **User Management**: Registration, authentication, and profile management
- **Meal Tracking**: Log meals with detailed food information
- **Health Logging**: Track physical feelings, mental state, and other health metrics
- **Sleep Tracking**: Monitor sleep duration and quality
- **Health Analytics**: Correlate food with health metrics and identify potential triggers
- **Export Data**: Export user data for external analysis
- **Frontend Interface**: Simple HTML/CSS/JS frontend for interacting with the API

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- SQLite (included with Django)

### Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv health_diary_venv

# Activate the virtual environment
# On macOS/Linux:
source health_diary_venv/bin/activate
# On Windows:
# health_diary_venv\Scripts\activate
```

### Install Dependencies

```bash
# Install requirements
pip install -r requirements.txt
```

### Database Setup

```bash
# Run migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser
```

## Running the Application

### Backend

```bash
# Start the development server
python manage.py runserver
```

The server will start at http://127.0.0.1:8000/

### Frontend

The application includes a simple frontend interface to interact with the API.

#### Option 1: Direct browser access
Simply open the `frontend/index.html` file in your browser.

#### Option 2: Using a static server
```bash
# If you have Node.js installed, you can use http-server
npm install -g http-server
cd frontend
http-server
```

Visit the URL provided by http-server (usually http://localhost:8080) in your browser.

## API Documentation

API documentation is available at:
- Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/
- ReDoc: http://127.0.0.1:8000/api/schema/redoc/

### Main API Endpoints

- **Authentication**:
  - Register: `POST /api/auth/register/`
  - Login: `POST /api/auth/login/`
  - Refresh Token: `POST /api/auth/token/refresh/`

- **User Management**:
  - User Details: `GET/PUT/DELETE /api/user/`
  - Profile: `GET/PUT /api/profile/`

- **Food**:
  - List/Create Foods: `GET/POST /api/foods/`
  - Retrieve/Update/Delete Food: `GET/PUT/DELETE /api/foods/{id}/`

- **Meals**:
  - List/Create Meals: `GET/POST /api/meals/`
  - Retrieve/Update/Delete Meal: `GET/PUT/DELETE /api/meals/{id}/`
  - Daily Meals: `GET /api/meals/daily/{date}/`
  - Weekly Meals: `GET /api/meals/weekly/{date}/`

- **Health Logs**:
  - List/Create Health Logs: `GET/POST /api/health-logs/`
  - Retrieve/Update/Delete Health Log: `GET/PUT/DELETE /api/health-logs/{id}/`
  - Daily Health: `GET /api/health-logs/daily/{date}/`
  - Weekly Health: `GET /api/health-logs/weekly/{date}/`
  - Monthly Health: `GET /api/health-logs/monthly/{date}/`

- **Sleep**:
  - List/Create Sleep Logs: `GET/POST /api/sleep/`
  - Retrieve/Update/Delete Sleep Log: `GET/PUT/DELETE /api/sleep/{id}/`
  - Weekly Sleep: `GET /api/sleep/weekly/{date}/`
  - Monthly Sleep: `GET /api/sleep/monthly/{date}/`

- **Analytics**:
  - Health Trends: `GET /api/analytics/health-trends/`
  - Food Correlations: `GET /api/analytics/food-correlations/`
  - Sleep Analysis: `GET /api/analytics/sleep-analysis/`
  - Symptom Triggers: `GET /api/analytics/symptoms-triggers/`

- **Export Data**:
  - Health Data: `GET /api/export/health-data/`
  - Meal Data: `GET /api/export/meal-data/`
  - All Data: `GET /api/export/all-data/`

## Known Issues

### Admin Interface

There is a known issue with the Admin interface due to problems with the `UserAdmin` class in `core/admin.py`. This issue prevents the Django server from starting when the admin configurations are active.

**Temporary fix**: The admin configurations in `core/admin.py` are currently commented out to allow the API server to run. If you need the admin interface, you'll need to debug and fix the issues with the `UserAdmin` class.

### Virtual Environment

Make sure to always activate the virtual environment before running any Django commands:

```bash
source health_diary_venv/bin/activate
```

## Frontend Features

The frontend interface includes:

- User registration and login
- Dashboard with health metrics visualization
- Forms for adding meals, health logs, and sleep data
- Analytics view for insights on health and food correlations
- Responsive design with right-to-left (RTL) Hebrew support

For more information about the frontend, see the [Frontend README](frontend/README.md).

## Development

### Project Structure

- `core/`: Main application with models, views, and services
- `health_diary_project/`: Project settings and main URL configuration
- `docs/`: Documentation files including user stories and testing strategy
- `frontend/`: Simple HTML/CSS/JS frontend interface

### Contributing

1. Create a new branch for each feature or bugfix
2. Write tests for new features
3. Ensure all tests pass before submitting pull requests
4. Follow the project's code style and documentation standards

## License

This project is licensed under the MIT License - see the LICENSE file for details. 