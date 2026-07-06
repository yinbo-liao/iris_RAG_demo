import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import QueryPage from '../../pages/QueryPage';

describe('QueryPage', () => {
  it('renders the page title', () => {
    render(
      <MemoryRouter>
        <QueryPage />
      </MemoryRouter>
    );
    expect(screen.getByText('Query Iris Dataset')).toBeInTheDocument();
  });

  it('renders QueryForm with textarea', () => {
    render(
      <MemoryRouter>
        <QueryPage />
      </MemoryRouter>
    );
    expect(screen.getByPlaceholderText(/predict species/i)).toBeInTheDocument();
  });

  it('renders empty state initially', () => {
    render(
      <MemoryRouter>
        <QueryPage />
      </MemoryRouter>
    );
    expect(screen.getByText('Ready to explore')).toBeInTheDocument();
  });

  it('renders approach selector', () => {
    render(
      <MemoryRouter>
        <QueryPage />
      </MemoryRouter>
    );
    expect(screen.getByText('Function Call')).toBeInTheDocument();
    expect(screen.getByText('Combined Tools')).toBeInTheDocument();
  });
});
