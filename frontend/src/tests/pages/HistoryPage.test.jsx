import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import HistoryPage from '../../pages/HistoryPage';

describe('HistoryPage', () => {
  it('renders the page title', () => {
    render(
      <MemoryRouter>
        <HistoryPage />
      </MemoryRouter>
    );
    expect(screen.getByText('Query History')).toBeInTheDocument();
  });
});
