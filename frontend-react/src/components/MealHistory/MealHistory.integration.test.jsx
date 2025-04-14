import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MealProvider } from '../../contexts/MealContext';
import { AuthProvider } from '../../contexts/AuthContext';
import axios from 'axios';
import MealHistory from './MealHistory';
import Dashboard from '../../pages/Dashboard';

// Mock axios
jest.mock('axios');

// Mock child components to simplify testing
jest.mock('../MealForm/MealForm', () => {
  return function MockMealForm(props) {
    return (
      <div data-testid="meal-form-mock">
        <button
          data-testid="save-meal-button"
          onClick={() => props.onSave({ id: 999, meal_type: 'snack', foods: [] })}
        >
          Save Meal
        </button>
      </div>
    );
  };
});

// Wrap with necessary providers
const renderWithProviders = (ui) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <MealProvider>
          {ui}
        </MealProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('MealHistory Integration Tests', () => {
  // Sample meals data
  const mockMeals = [
    {
      id: 1,
      date_time: '2024-06-01T08:00:00Z',
      meal_type: 'breakfast',
      foods: [
        { id: 1, name: 'סלט ירקות', amount: 200 },
        { id: 2, name: 'לחם מלא', amount: 50 }
      ]
    },
    {
      id: 2,
      date_time: '2024-06-01T13:00:00Z',
      meal_type: 'lunch',
      foods: [
        { id: 3, name: 'אורז מלא', amount: 150 },
        { id: 4, name: 'חזה עוף', amount: 120 }
      ]
    }
  ];
  
  // Sample user data
  const mockUser = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com'
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Default mock implementations
    axios.get.mockImplementation((url) => {
      if (url.includes('/meals')) {
        return Promise.resolve({ data: mockMeals });
      }
      if (url.includes('/user')) {
        return Promise.resolve({ data: mockUser });
      }
      return Promise.resolve({ data: [] });
    });
    
    // Local storage mock
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => JSON.stringify({ token: 'fake-token' })),
        setItem: jest.fn(),
        removeItem: jest.fn()
      },
      writable: true
    });
  });

  test('integrates with MealForm when adding a new meal', async () => {
    // Mock successful post
    axios.post.mockResolvedValue({ 
      data: { 
        id: 999, 
        date_time: '2024-06-03T10:00:00Z', 
        meal_type: 'snack', 
        foods: [] 
      }
    });
    
    renderWithProviders(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Click add meal button
    fireEvent.click(screen.getByTestId('add-meal-button'));
    
    // Check meal form rendered
    expect(screen.getByTestId('meal-form-mock')).toBeInTheDocument();
    
    // Save new meal
    fireEvent.click(screen.getByTestId('save-meal-button'));
    
    // Verify API call
    expect(axios.post).toHaveBeenCalled();
    
    // Verify meal list is refreshed
    expect(axios.get).toHaveBeenCalledTimes(2);
  });

  test('integrates with Dashboard and updates analytics when meal is deleted', async () => {
    // Mock successful delete
    axios.delete.mockResolvedValue({ data: { success: true } });
    
    // Mock analytics data
    const mockAnalytics = {
      totalMeals: 10,
      mealDistribution: { breakfast: 3, lunch: 3, dinner: 3, snack: 1 }
    };
    
    axios.get.mockImplementation((url) => {
      if (url.includes('/meals')) {
        return Promise.resolve({ data: mockMeals });
      }
      if (url.includes('/analytics')) {
        return Promise.resolve({ data: mockAnalytics });
      }
      return Promise.resolve({ data: [] });
    });
    
    renderWithProviders(<Dashboard />);
    
    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.queryByTestId('dashboard-loading')).not.toBeInTheDocument();
    });
    
    // Find and click delete meal button
    fireEvent.click(screen.getByTestId('delete-meal-1'));
    
    // Confirm delete
    fireEvent.click(screen.getByTestId('confirm-delete'));
    
    // Verify API call
    expect(axios.delete).toHaveBeenCalledWith('api/meals/1/');
    
    // Check analytics is refreshed
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('analytics'), expect.anything());
    });
  });

  test('filters are synchronized with URL parameters', async () => {
    // Setup mock window.history and location
    const pushStateSpy = jest.spyOn(window.history, 'pushState');
    Object.defineProperty(window, 'location', {
      value: {
        search: '?date=2024-06-01&mealType=breakfast'
      },
      writable: true
    });
    
    renderWithProviders(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Check initial filter state from URL
    expect(screen.getByTestId('date-filter')).toHaveValue('2024-06-01');
    expect(screen.getByTestId('meal-type-filter-breakfast')).toHaveAttribute('aria-pressed', 'true');
    
    // Change filter
    fireEvent.click(screen.getByTestId('meal-type-filter-lunch'));
    
    // Check URL was updated
    expect(pushStateSpy).toHaveBeenCalledWith(
      expect.anything(),
      expect.anything(),
      expect.stringContaining('mealType=lunch')
    );
  });

  test('integrates with analytics component to show meal patterns', async () => {
    renderWithProviders(
      <div>
        <MealHistory userId={1} />
        <div data-testid="analytics-component" />
      </div>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Click analyze button
    fireEvent.click(screen.getByTestId('analyze-meals-button'));
    
    // Check analytics component received data
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining('analytics/meals'),
      expect.anything()
    );
  });

  test('exports meal history to PDF', async () => {
    // Mock document.createElement for canvas
    const mockCanvas = {
      getContext: jest.fn().mockReturnValue({
        fillText: jest.fn(),
        fillRect: jest.fn()
      }),
      toDataURL: jest.fn().mockReturnValue('data:image/png;base64,fake-data')
    };
    
    jest.spyOn(document, 'createElement').mockImplementation((tag) => {
      if (tag === 'canvas') return mockCanvas;
      return document.createElement(tag);
    });
    
    renderWithProviders(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Click export button
    fireEvent.click(screen.getByTestId('export-button'));
    
    // Select PDF format
    fireEvent.click(screen.getByTestId('export-pdf'));
    
    // Check if canvas was created for PDF generation
    expect(document.createElement).toHaveBeenCalledWith('canvas');
  });

  test('shares meal history data with healthcare provider', async () => {
    // Mock sharing endpoint
    axios.post.mockResolvedValue({ 
      data: { success: true, shareUrl: 'https://example.com/shared/abc123' } 
    });
    
    renderWithProviders(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Click share button
    fireEvent.click(screen.getByTestId('share-button'));
    
    // Enter provider email
    fireEvent.change(screen.getByTestId('provider-email'), {
      target: { value: 'doctor@example.com' }
    });
    
    // Set expiration date
    fireEvent.change(screen.getByTestId('share-expiration'), {
      target: { value: '2024-07-01' }
    });
    
    // Confirm share
    fireEvent.click(screen.getByTestId('confirm-share'));
    
    // Check API call
    expect(axios.post).toHaveBeenCalledWith(
      'api/share/meals/',
      expect.objectContaining({
        recipientEmail: 'doctor@example.com',
        expirationDate: '2024-07-01'
      })
    );
    
    // Check success message
    await waitFor(() => {
      expect(screen.getByText(/הקישור נשלח/i)).toBeInTheDocument();
      expect(screen.getByText('https://example.com/shared/abc123')).toBeInTheDocument();
    });
  });
}); 