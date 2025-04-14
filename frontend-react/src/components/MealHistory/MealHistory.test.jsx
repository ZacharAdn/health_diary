import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import MealHistory from './MealHistory';

// Mock axios
jest.mock('axios');

describe('MealHistory Component', () => {
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
    },
    {
      id: 3,
      date_time: '2024-06-02T08:00:00Z',
      meal_type: 'breakfast',
      foods: [
        { id: 5, name: 'יוגורט', amount: 200 },
        { id: 6, name: 'גרנולה', amount: 50 }
      ]
    }
  ];

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    // Default mock implementation
    axios.get.mockResolvedValue({ data: mockMeals });
  });

  test('renders component with loading state', () => {
    render(<MealHistory userId={1} />);
    
    // Check loading indicator
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });

  test('loads and displays meals data correctly', async () => {
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Check if meals are displayed
    expect(screen.getByTestId('meal-item-1')).toBeInTheDocument();
    expect(screen.getByTestId('meal-item-2')).toBeInTheDocument();
    expect(screen.getByTestId('meal-item-3')).toBeInTheDocument();
    
    // Check content
    expect(screen.getByText('ארוחת בוקר')).toBeInTheDocument();
    expect(screen.getByText('ארוחת צהריים')).toBeInTheDocument();
    expect(screen.getByText('סלט ירקות')).toBeInTheDocument();
    expect(screen.getByText('אורז מלא')).toBeInTheDocument();
  });

  test('filters meals by date correctly', async () => {
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Filter by date
    fireEvent.change(screen.getByTestId('date-filter'), { 
      target: { value: '2024-06-02' }
    });
    
    // Check filtered results
    expect(screen.queryByTestId('meal-item-1')).not.toBeInTheDocument();
    expect(screen.queryByTestId('meal-item-2')).not.toBeInTheDocument();
    expect(screen.getByTestId('meal-item-3')).toBeInTheDocument();
    expect(screen.getByText('יוגורט')).toBeInTheDocument();
  });

  test('filters meals by meal type correctly', async () => {
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Filter by meal type
    fireEvent.click(screen.getByTestId('meal-type-filter-breakfast'));
    
    // Check filtered results
    expect(screen.getByTestId('meal-item-1')).toBeInTheDocument();
    expect(screen.queryByTestId('meal-item-2')).not.toBeInTheDocument();
    expect(screen.getByTestId('meal-item-3')).toBeInTheDocument();
    expect(screen.getByText('סלט ירקות')).toBeInTheDocument();
    expect(screen.getByText('יוגורט')).toBeInTheDocument();
    expect(screen.queryByText('אורז מלא')).not.toBeInTheDocument();
  });

  test('handles meal deletion correctly', async () => {
    // Mock successful delete
    axios.delete.mockResolvedValue({ data: { success: true } });
    
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Click delete button
    fireEvent.click(screen.getByTestId('delete-meal-1'));
    
    // Confirm delete in modal
    fireEvent.click(screen.getByTestId('confirm-delete'));
    
    // Check API call
    expect(axios.delete).toHaveBeenCalledWith('api/meals/1/');
    
    // Check meal removed from UI
    await waitFor(() => {
      expect(screen.queryByTestId('meal-item-1')).not.toBeInTheDocument();
    });
  });

  test('handles error state correctly when API fails', async () => {
    // Mock API error
    axios.get.mockRejectedValue(new Error('Failed to fetch meals'));
    
    render(<MealHistory userId={1} />);
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });
    
    // Check error message
    expect(screen.getByText(/לא ניתן לטעון את היסטוריית הארוחות/i)).toBeInTheDocument();
    
    // Try reload button
    fireEvent.click(screen.getByTestId('reload-button'));
    
    // Check API call
    expect(axios.get).toHaveBeenCalledTimes(2);
  });

  test('displays empty state correctly when no meals found', async () => {
    // Mock empty response
    axios.get.mockResolvedValue({ data: [] });
    
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Check empty state
    expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    expect(screen.getByText(/לא נמצאו ארוחות/i)).toBeInTheDocument();
    expect(screen.getByTestId('add-meal-button')).toBeInTheDocument();
  });

  test('switches between list and grid views', async () => {
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Check default view (list)
    expect(screen.getByTestId('list-view')).toBeInTheDocument();
    expect(screen.queryByTestId('grid-view')).not.toBeInTheDocument();
    
    // Switch to grid view
    fireEvent.click(screen.getByTestId('grid-view-toggle'));
    
    // Check grid view is active
    expect(screen.queryByTestId('list-view')).not.toBeInTheDocument();
    expect(screen.getByTestId('grid-view')).toBeInTheDocument();
  });

  test('opens edit mode for a meal', async () => {
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Click edit button
    fireEvent.click(screen.getByTestId('edit-meal-1'));
    
    // Check edit form appeared
    expect(screen.getByTestId('edit-meal-form')).toBeInTheDocument();
    
    // Check prefilled data
    expect(screen.getByDisplayValue('סלט ירקות')).toBeInTheDocument();
    expect(screen.getByDisplayValue('לחם מלא')).toBeInTheDocument();
  });

  test('successfully edits a meal', async () => {
    // Mock successful update
    axios.put.mockResolvedValue({ 
      data: {
        ...mockMeals[0],
        foods: [
          { id: 1, name: 'סלט ירקות', amount: 250 },
          { id: 2, name: 'לחם מלא', amount: 50 }
        ]
      }
    });
    
    render(<MealHistory userId={1} />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
    
    // Click edit button
    fireEvent.click(screen.getByTestId('edit-meal-1'));
    
    // Edit amount
    const amountInput = screen.getByTestId('food-amount-1');
    fireEvent.change(amountInput, { target: { value: '250' } });
    
    // Save changes
    fireEvent.click(screen.getByTestId('save-changes'));
    
    // Check API call
    expect(axios.put).toHaveBeenCalledWith('api/meals/1/', expect.objectContaining({
      foods: expect.arrayContaining([
        expect.objectContaining({ id: 1, amount: 250 })
      ])
    }));
    
    // Check updated value in UI
    await waitFor(() => {
      expect(screen.getByText('250 גרם')).toBeInTheDocument();
    });
  });
}); 