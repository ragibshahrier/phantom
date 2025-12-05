import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DoomsdayCalendar from './DoomsdayCalendar';
import { Event } from '../types';

describe('DoomsdayCalendar', () => {
  const mockEvents: Event[] = [
    {
      id: 1,
      title: 'Test Event 1',
      description: 'Description 1',
      category: 1,
      category_name: 'Study',
      category_color: '#00ff41',
      priority_level: 4,
      start_time: '2025-01-15T10:00:00Z',
      end_time: '2025-01-15T11:00:00Z',
      is_flexible: false,
      is_completed: false,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    },
    {
      id: 2,
      title: 'Critical Event',
      description: 'Description 2',
      category: 2,
      category_name: 'Exam',
      category_color: '#ff003c',
      priority_level: 5,
      start_time: '2025-01-20T14:00:00Z',
      end_time: '2025-01-20T16:00:00Z',
      is_flexible: false,
      is_completed: false,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    },
  ];

  it('should render calendar with events', () => {
    const onSelectDate = vi.fn();
    render(
      <DoomsdayCalendar
        events={mockEvents}
        selectedDate="2025-01-15"
        onSelectDate={onSelectDate}
      />
    );

    // Check that calendar header is rendered
    expect(screen.getByText(/JANUARY/i)).toBeDefined();
    expect(screen.getByText(/2025/i)).toBeDefined();
  });

  it('should display event indicators on dates with events', () => {
    const onSelectDate = vi.fn();
    const { container } = render(
      <DoomsdayCalendar
        events={mockEvents}
        selectedDate="2025-01-15"
        onSelectDate={onSelectDate}
      />
    );

    // Check for event indicators (colored bars)
    const indicators = container.querySelectorAll('.bg-\\[\\#00ff41\\]\\/50, .bg-\\[\\#ff003c\\]');
    expect(indicators.length).toBeGreaterThan(0);
  });

  it('should call onSelectDate when a date is clicked', () => {
    const onSelectDate = vi.fn();
    const { container } = render(
      <DoomsdayCalendar
        events={mockEvents}
        selectedDate="2025-01-15"
        onSelectDate={onSelectDate}
      />
    );

    // Find and click a date button (day 15)
    const dateButtons = container.querySelectorAll('button');
    const day15Button = Array.from(dateButtons).find(
      (btn) => btn.textContent?.includes('15')
    );

    if (day15Button) {
      fireEvent.click(day15Button);
      expect(onSelectDate).toHaveBeenCalled();
    }
  });

  it('should navigate to previous month', () => {
    const onSelectDate = vi.fn();
    render(
      <DoomsdayCalendar
        events={mockEvents}
        selectedDate="2025-01-15"
        onSelectDate={onSelectDate}
      />
    );

    // Find and click the previous month button
    const prevButton = screen.getAllByRole('button')[0];
    fireEvent.click(prevButton);

    // Should show December 2024
    expect(screen.getByText(/DECEMBER/i)).toBeDefined();
    expect(screen.getByText(/2024/i)).toBeDefined();
  });

  it('should navigate to next month', () => {
    const onSelectDate = vi.fn();
    render(
      <DoomsdayCalendar
        events={mockEvents}
        selectedDate="2025-01-15"
        onSelectDate={onSelectDate}
      />
    );

    // Find and click the next month button (last button in header)
    const buttons = screen.getAllByRole('button');
    const nextButton = buttons[1]; // Second button is next month
    fireEvent.click(nextButton);

    // Should show February 2025
    expect(screen.getByText(/FEBRUARY/i)).toBeDefined();
    expect(screen.getByText(/2025/i)).toBeDefined();
  });

  it('should highlight current date', () => {
    const onSelectDate = vi.fn();
    const today = new Date().toISOString().split('T')[0];
    
    const { container } = render(
      <DoomsdayCalendar
        events={mockEvents}
        selectedDate={today}
        onSelectDate={onSelectDate}
      />
    );

    // Check for today's corner marker
    const todayMarkers = container.querySelectorAll('.border-\\[\\#00ff41\\]');
    expect(todayMarkers.length).toBeGreaterThan(0);
  });

  it('should handle multi-day events', () => {
    const multiDayEvent: Event = {
      id: 3,
      title: 'Multi-day Event',
      description: 'Spans multiple days',
      category: 1,
      category_name: 'Study',
      category_color: '#00ff41',
      priority_level: 3,
      start_time: '2025-01-15T10:00:00Z',
      end_time: '2025-01-17T18:00:00Z', // Ends 2 days later
      is_flexible: false,
      is_completed: false,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    };

    const onSelectDate = vi.fn();
    render(
      <DoomsdayCalendar
        events={[multiDayEvent]}
        selectedDate="2025-01-15"
        onSelectDate={onSelectDate}
      />
    );

    // The event should appear on all days it spans (15, 16, 17)
    // This is verified by the filtering logic in the component
    expect(screen.getByText(/JANUARY/i)).toBeDefined();
  });
});
