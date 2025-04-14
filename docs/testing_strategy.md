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
  - התחלתיים בפרופיל המשתמש
  - עיבוד גודל מנה לכמות
  - עיבוד נתונים מפורטים של יציאות
  - רכיב MealHistory ותצוגת היסטוריית ארוחות

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

# test_profile_data.py
def test_profile_initial_data():
    data = {
        "age": 35,
        "weight": 70.5,
        "height": 175,
        "medical_conditions": "אלרגיה לבוטנים, אסטמה",
        "exercise_frequency": "medium"
    }
    serializer = ProfileSerializer(data=data)
    assert serializer.is_valid()
    
# test_portion_size.py
def test_portion_size_conversion():
    food = Food.objects.create(name="לחם", base_portion=30)
    assert calculate_amount(food, "small") == 15
    assert calculate_amount(food, "medium") == 30
    assert calculate_amount(food, "large") == 45
    
# test_stool_log.py
def test_stool_log_details():
    data = {
        "date": "2024-04-08",
        "time": "08:30:00",
        "type": "3",  # Bristol stool scale
        "color": "brown",
        "notes": "קלה ומהירה"
    }
    serializer = StoolLogSerializer(data=data)
    assert serializer.is_valid()

# test_meal_history.py
def test_meal_history_component():
    # בדיקת רינדור בסיסי של הרכיב
    component = render(<MealHistory userId={1} />)
    assert component.getByTestId('meal-history-container')
    
def test_meal_history_filtering():
    # בדיקת פונקציונליות סינון
    component = render(<MealHistory userId={1} />)
    
    # בדיקת סינון לפי תאריך
    fireEvent.change(component.getByTestId('date-filter'), { target: { value: '2024-06-01' } })
    assert component.getByText('מציג תוצאות מתאריך 01/06/2024')
    
    # בדיקת סינון לפי סוג ארוחה
    fireEvent.click(component.getByTestId('meal-type-filter-breakfast'))
    assert component.getByText('מציג ארוחות בוקר בלבד')
    
def test_meal_history_empty_state():
    # בדיקת מצב ריק (ללא ארוחות)
    component = render(<MealHistory userId={999} />)  # משתמש ללא ארוחות
    assert component.getByText('לא נמצאו ארוחות')
    assert component.getByTestId('add-meal-button')
```

### 2. Integration Tests
- **Tools**: pytest-django
- **Focus Areas**:
  - Database interactions
  - Cache operations
  - External service integrations
  - API endpoint flows
  - Authentication flows
  - תהליך הרשמה עם נתונים התחלתיים
  - עדכון רשומה יומית מלאה
  - שמירת יציאות מפורטות
  - אינטגרציה של MealHistory עם API ורכיבים אחרים

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

@pytest.mark.django_db
def test_create_meal_with_portion_sizes():
    client = APIClient()
    user = UserFactory.create()
    client.force_authenticate(user=user)
    
    food = FoodFactory.create(base_portion=50)
    meal_data = {
        "date_time": "2024-04-08T12:00:00Z",
        "meal_type": "lunch",
        "foods": [{"food_id": food.id, "portion_size": "large"}]
    }
    
    response = client.post("/api/meals/", meal_data)
    assert response.status_code == 201
    meal_food = MealFood.objects.first()
    assert meal_food.amount == 75  # 1.5x base portion

@pytest.mark.django_db
def test_register_with_profile_data():
    client = APIClient()
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "securepass123",
        "password2": "securepass123",
        "profile": {
            "age": 28,
            "weight": 65.5,
            "height": 170,
            "medical_conditions": "ללא בעיות",
            "exercise_frequency": "high"
        }
    }
    
    response = client.post("/api/auth/register/", user_data)
    assert response.status_code == 201
    assert Profile.objects.count() == 1
    profile = Profile.objects.first()
    assert profile.age == 28
    assert profile.exercise_frequency == "high"

@pytest.mark.django_db
def test_daily_log_summary():
    client = APIClient()
    user = UserFactory.create()
    client.force_authenticate(user=user)
    
    # יצירת רשומה יומית מלאה
    date = "2024-04-08"
    summary_data = {
        "date": date,
        "meals": [
            {"meal_type": "breakfast", "foods": [{"food_id": 1, "amount": 100}]},
            {"meal_type": "lunch", "foods": [{"food_id": 2, "portion_size": "medium"}]}
        ],
        "health_log": {
            "physical_feeling": 4,
            "mental_feeling": 3,
            "stool_quality": "normal"
        },
        "sleep": {
            "duration": 7.5,
            "quality": 4
        }
    }
    
    response = client.post("/api/daily-summary/", summary_data)
    assert response.status_code == 201
    
    # בדיקה שכל הרשומות נוצרו
    assert Meal.objects.filter(user=user, date_time__date=date).count() == 2
    assert HealthLog.objects.filter(user=user, date=date).count() == 1
    assert Sleep.objects.filter(user=user, date=date).count() == 1

# test_meal_history_integration.js
test('loads user meal data correctly', async () => {
  // מדמה קריאת API מוצלחת 
  fetchMock.mockResponseOnce(JSON.stringify([
    { id: 1, date_time: '2024-06-01T08:00:00Z', meal_type: 'breakfast', foods: [{name: 'סלט', amount: 200}] },
    { id: 2, date_time: '2024-06-01T13:00:00Z', meal_type: 'lunch', foods: [{name: 'אורז', amount: 150}] }
  ]));
  
  const { getByTestId, getAllByTestId } = render(<MealHistory userId={1} />);
  
  // וידוא טעינה
  expect(getByTestId('loading-indicator')).toBeInTheDocument();
  
  // המתנה לסיום טעינה
  await waitFor(() => {
    expect(getAllByTestId('meal-item')).toHaveLength(2);
  });
  
  // בדיקה שהנתונים מוצגים נכון
  expect(getByTestId('meal-item-1')).toHaveTextContent('ארוחת בוקר');
  expect(getByTestId('meal-item-1')).toHaveTextContent('סלט');
  expect(getByTestId('meal-item-2')).toHaveTextContent('ארוחת צהריים');
});

test('handles meal deletion correctly', async () => {
  // מדמה קריאות API
  fetchMock.mockResponseOnce(JSON.stringify([
    { id: 1, date_time: '2024-06-01T08:00:00Z', meal_type: 'breakfast', foods: [{name: 'סלט', amount: 200}] }
  ]));
  
  // מדמה מחיקה מוצלחת
  fetchMock.mockResponseOnce(JSON.stringify({ success: true }), { method: 'DELETE' });
  
  const { getByTestId, queryByTestId } = render(<MealHistory userId={1} />);
  
  // המתנה לטעינת הרכיב
  await waitFor(() => {
    expect(getByTestId('meal-item-1')).toBeInTheDocument();
  });
  
  // מחיקת ארוחה
  fireEvent.click(getByTestId('delete-meal-1'));
  fireEvent.click(getByTestId('confirm-delete'));
  
  // וידוא מחיקה מהתצוגה
  await waitFor(() => {
    expect(queryByTestId('meal-item-1')).not.toBeInTheDocument();
  });
});
```

### 3. End-to-End Tests
- **Tools**: pytest-django, Selenium (if needed for frontend integration)
- **Scenarios**:
  - Complete user journeys
  - Multi-step processes
  - Real-world usage patterns
  - סיפור הרשמה והזנת נתונים התחלתיים
  - תיעוד יומי שלם

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

def test_new_user_onboarding_journey():
    # הרשמה עם נתונים בסיסיים
    user = register_new_user({
        "username": "test_journey",
        "email": "journey@test.com",
        "password": "secure123"
    })
    
    # השלמת פרופיל עם נתונים התחלתיים
    profile = complete_profile(user, {
        "age": 30,
        "weight": 75,
        "height": 180,
        "medical_conditions": "צליאק",
        "exercise_frequency": "medium"
    })
    
    # הוספת מאכלים מועדפים
    add_favorite_foods(user, ["אורז מלא", "עוף", "סלט ירקות"])
    
    # תיעוד יום ראשון מלא
    log_complete_day(user, {
        "meals": [
            {"meal_type": "breakfast", "foods": [{"name": "גרנולה", "portion_size": "medium"}]},
            {"meal_type": "lunch", "foods": [{"name": "סלט", "portion_size": "large"}]}
        ],
        "health_log": {"physical_feeling": 4, "mental_feeling": 4},
        "sleep": {"duration": 8, "quality": 4}
    })
    
    # אימות שכל הנתונים נשמרו ומוצגים נכון
    profile_data = get_user_profile(user)
    assert profile_data["age"] == 30
    assert len(get_user_meals(user)) == 2
    assert get_user_health_logs(user)[0]["physical_feeling"] == 4
```

## Test Categories

### 1. Functional Tests
- API endpoint behavior
- CRUD operations
- Business logic
- Data validation
- Error handling
- Authentication & Authorization
- המרת גודל מנה לכמות
- עיבוד ושמירת נתונים רפואיים
- סיכום נתונים יומי

### 2. Performance Tests
- **Tools**: locust, k6
- **Areas to Test**:
  - API response times
  - Database query optimization
  - Cache effectiveness
  - Concurrent user handling
  - עומס בעדכון נתונים מרובים בבת אחת

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
        
    @task
    def submit_daily_summary(self):
        # בדיקת ביצועים לעדכון יומי מלא
        self.client.post("/api/daily-summary/", {
            "date": "2024-04-08",
            "meals": [
                {"meal_type": "breakfast", "foods": [{"food_id": 1, "portion_size": "medium"}]},
                {"meal_type": "lunch", "foods": [{"food_id": 2, "amount": 100}]},
                {"meal_type": "dinner", "foods": [{"food_id": 3, "portion_size": "large"}]}
            ],
            "health_log": {
                "physical_feeling": 4,
                "mental_feeling": 3,
                "stool_logs": [
                    {"time": "08:00:00", "type": "3", "notes": "רגילה"},
                    {"time": "16:00:00", "type": "4", "notes": "אחרי ארוחת צהריים"}
                ]
            },
            "sleep": {
                "duration": 7.5,
                "quality": 4
            }
        })
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
  - אבטחת נתונים רפואיים רגישים

### 4. Data Validation Tests
- Input boundaries
- Data types
- Required fields
- Unique constraints
- Foreign key constraints
- אימות נתונים רפואיים
- אימות טווחי ערכים של נתונים אישיים
- אימות מידות ויחידות במערכת

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
    
class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile
    
    user = factory.SubFactory(UserFactory)
    age = factory.Faker('random_int', min=18, max=80)
    weight = factory.Faker('random_int', min=45, max=120)
    height = factory.Faker('random_int', min=150, max=200)
    medical_conditions = factory.Faker('sentence')
    exercise_frequency = factory.Iterator(['low', 'medium', 'high'])
    
class StoolLogFactory(DjangoModelFactory):
    class Meta:
        model = StoolLog
    
    health_log = factory.SubFactory('factories.HealthLogFactory')
    time = factory.Faker('time_object')
    type = factory.Faker('random_element', elements=['1', '2', '3', '4', '5', '6', '7'])
    color = factory.Faker('random_element', elements=['brown', 'green', 'yellow', 'black', 'red'])
    notes = factory.Faker('sentence')
```

### 2. Fixtures
- Basic data fixtures for common test scenarios
- Anonymized production data for complex scenarios
- Specific test case fixtures
- נתוני פרופיל מותאמים למקרי בדיקה
- טבלאות המרה לגדלי מנות

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