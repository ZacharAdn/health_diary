# MealHistory Component Tests

This directory contains tests for the MealHistory component, which provides a comprehensive view of meal history with filtering, editing, and analysis capabilities.

## Test Types

The tests are organized into three levels:

1. **Unit Tests** - Test individual component functionality in isolation
2. **Integration Tests** - Test interactions with other components and services
3. **End-to-End Tests** - Test complete user flows in a real browser environment

## Unit Tests

Located in `MealHistory.test.jsx`, these tests verify:

- Basic rendering and loading states
- Data fetching and display
- Filtering functionality (date, meal type)
- View switching (list/grid)
- Error handling
- Empty state handling
- Meal editing and deletion

### Running Unit Tests

```bash
# Run all unit tests
npm test

# Run only MealHistory tests
npm test -- -t "MealHistory"

# Run with coverage
npm test -- --coverage
```

## Integration Tests

Located in `MealHistory.integration.test.jsx`, these tests verify:

- Integration with MealForm when adding meals
- Integration with Dashboard analytics
- URL parameter synchronization
- Data export functionality
- Sharing with healthcare providers
- Analytics integration

### Running Integration Tests

```bash
# Run integration tests
npm test -- MealHistory.integration.test.jsx
```

## End-to-End Tests

Located in `src/tests/MealHistory.e2e.test.js`, these tests verify complete user journeys:

- Navigating to MealHistory through the application
- Filtering and sorting meals
- Adding new meals
- Editing meals
- Deleting meals
- Switching view types
- Exporting and sharing data
- Analyzing meal patterns
- Advanced filtering

### Running E2E Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npx playwright test

# Run only MealHistory E2E tests
npx playwright test MealHistory.e2e.test.js

# Run with UI mode
npx playwright test --ui
```

## Test Data Attributes

For consistent testing, the component uses these data attributes:

| Attribute | Description |
|-----------|-------------|
| `data-testid="meal-history-container"` | Main container element |
| `data-testid="loading-indicator"` | Loading spinner |
| `data-testid="meal-item-{id}"` | Individual meal item |
| `data-testid="meal-type-badge"` | Badge showing meal type |
| `data-testid="meal-date"` | Element showing meal date |
| `data-testid="list-view"` | List view container |
| `data-testid="grid-view"` | Grid view container |
| `data-testid="date-filter"` | Date filter input |
| `data-testid="meal-type-filter-{type}"` | Meal type filter button |
| `data-testid="edit-meal-{id}"` | Edit button for meal |
| `data-testid="delete-meal-{id}"` | Delete button for meal |
| `data-testid="confirm-delete"` | Confirmation button in delete dialog |
| `data-testid="empty-state"` | Empty state container |
| `data-testid="error-message"` | Error message container |
| `data-testid="add-meal-button"` | Button to add new meal |

## Mock Setup

The tests use various mocks to simulate API responses and context providers:

- Axios requests are mocked to return predefined data
- Context providers are mocked to provide necessary state
- Child components are selectively mocked for integration tests
- Browser APIs (localStorage, history) are mocked for certain tests

## Test Coverage Requirements

The MealHistory component tests should maintain:

- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: Cover all major integration points
- **E2E Tests**: Cover all key user journeys

## Troubleshooting Tests

If tests are failing, check:

1. Data attribute changes - ensure the component's data-testid attributes match the tests
2. API response format changes - update mocked API responses
3. Component logic changes - review test assertions

## Adding New Tests

When adding new functionality to MealHistory, follow these guidelines:

1. Add unit tests for the new functionality
2. Add integration tests if it interacts with other components
3. Update E2E tests if it affects user journeys
4. Update the README if new data attributes are added 