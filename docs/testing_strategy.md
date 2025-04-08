# Testing Strategy - Health Diary Backend

## Testing Levels

### 1. Unit Tests
- **Coverage Target**: 90%+ code coverage
- **Tools**: pytest, pytest-cov
- **Areas to Test**:
  - Model methods and validations
  - Serializer validations
  - Service layer functions
  - Utility functions
  - Form validations

#### Example Unit Tests:
```python
# test_models.py
def test_user_creation():
    user = User.objects.create(
        email="test@example.com",
        username="testuser",
        password="testpass123"
    )
    assert user.email == "test@example.com"
    assert user.is_medical_professional == False

# test_serializers.py
def test_meal_serializer_validation():
    data = {
        "date_time": "2024-04-08T12:00:00Z",
        "meal_type": "invalid_type",
    }
    serializer = MealSerializer(data=data)
    assert not serializer.is_valid()
    assert "meal_type" in serializer.errors
```

### 2. Integration Tests
- **Tools**: pytest-django
- **Focus Areas**:
  - Database interactions
  - Cache operations
  - External service integrations
  - API endpoint flows
  - Authentication flows

#### Example Integration Tests:
```python
# test_views.py
@pytest.mark.django_db
def test_create_meal_with_foods():
    client = APIClient()
    user = UserFactory.create()
    client.force_authenticate(user=user)
    
    food = FoodFactory.create()
    meal_data = {
        "date_time": "2024-04-08T12:00:00Z",
        "meal_type": "lunch",
        "foods": [{"food_id": food.id, "amount": 100}]
    }
    
    response = client.post("/api/meals/", meal_data)
    assert response.status_code == 201
    assert MealFood.objects.count() == 1
```

### 3. End-to-End Tests
- **Tools**: pytest-django, Selenium (if needed for frontend integration)
- **Scenarios**:
  - Complete user journeys
  - Multi-step processes
  - Real-world usage patterns

#### Example E2E Test:
```python
# test_journeys.py
def test_user_daily_log_journey():
    # Create user and authenticate
    user = create_and_login_user()
    
    # Log breakfast
    breakfast = create_breakfast(user)
    
    # Create health log
    health_log = create_health_log(user)
    
    # Create sleep log
    sleep_log = create_sleep_log(user)
    
    # Verify daily summary
    summary = get_daily_summary(user)
    assert len(summary["meals"]) == 1
    assert summary["health_log"] is not None
    assert summary["sleep_log"] is not None
```

## Test Categories

### 1. Functional Tests
- API endpoint behavior
- CRUD operations
- Business logic
- Data validation
- Error handling
- Authentication & Authorization

### 2. Performance Tests
- **Tools**: locust, k6
- **Areas to Test**:
  - API response times
  - Database query optimization
  - Cache effectiveness
  - Concurrent user handling

#### Example Performance Test:
```python
# locustfile.py
from locust import HttpUser, task, between

class HealthDiaryUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def view_daily_logs(self):
        self.client.get("/api/health-logs/daily/2024-04-08/")
    
    @task
    def search_foods(self):
        self.client.get("/api/foods/search/?query=apple")
```

### 3. Security Tests
- **Tools**: safety, bandit, OWASP ZAP
- **Areas to Test**:
  - JWT implementation
  - Input validation
  - SQL injection prevention
  - CSRF protection
  - Rate limiting
  - Permission checks

### 4. Data Validation Tests
- Input boundaries
- Data types
- Required fields
- Unique constraints
- Foreign key constraints

## Test Environments

### 1. Development
- Local SQLite database
- Local Redis instance
- Mocked external services

### 2. Testing
- PostgreSQL database
- Redis instance
- Test data fixtures
- Mocked external services

### 3. Staging
- Production-like environment
- Real external services
- Sanitized production data

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:latest
      redis:
        image: redis:latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run unit tests
        run: pytest tests/unit
      
      - name: Run integration tests
        run: pytest tests/integration
      
      - name: Run security checks
        run: |
          safety check
          bandit -r .
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Data Management

### 1. Factories
```python
# factories.py
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

class FoodFactory(DjangoModelFactory):
    class Meta:
        model = Food
    
    name = factory.Sequence(lambda n: f"Food Item {n}")
    calories = factory.Faker('random_int', min=50, max=1000)
```

### 2. Fixtures
- Basic data fixtures for common test scenarios
- Anonymized production data for complex scenarios
- Specific test case fixtures

## Monitoring and Reporting

### 1. Coverage Reports
- Generate HTML coverage reports
- Track coverage trends
- Set minimum coverage thresholds

### 2. Test Reports
- JUnit XML reports
- Test execution times
- Failure analysis
- Trend monitoring

### 3. Performance Metrics
- Response time percentiles
- Error rates
- Resource utilization
- Bottleneck identification

## Best Practices

1. **Test Independence**
   - Each test should be self-contained
   - Clean up test data after each test
   - Avoid test interdependencies

2. **Test Naming**
   - Clear and descriptive names
   - Follow pattern: test_[what]_[expected_behavior]
   - Group related tests in classes

3. **Assertions**
   - Use specific assertions
   - Include meaningful error messages
   - Check both positive and negative cases

4. **Mocking**
   - Mock external services
   - Use appropriate scope
   - Maintain realistic behavior

5. **Documentation**
   - Document test purpose
   - Include example usage
   - Document special setup requirements
``` 