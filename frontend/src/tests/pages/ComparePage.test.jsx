import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ComparePage from '../../pages/ComparePage';

describe('ComparePage', () => {
  it('renders the page title', () => {
    render(
      <MemoryRouter>
        <ComparePage />
      </MemoryRouter>
    );
    expect(screen.getByText('Compare Approaches')).toBeInTheDocument();
  });

  it('renders Compare Both button', () => {
    render(
      <MemoryRouter>
        <ComparePage />
      </MemoryRouter>
    );
    expect(screen.getByText('Compare Both')).toBeInTheDocument();
  });

  it('renders empty state initially', () => {
    render(
      <MemoryRouter>
        <ComparePage />
      </MemoryRouter>
    );
    expect(screen.getByText('Compare both approaches')).toBeInTheDocument();
  });
});
