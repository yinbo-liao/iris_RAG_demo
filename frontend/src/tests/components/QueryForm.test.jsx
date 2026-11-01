import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import QueryForm from '../../components/QueryForm';

const defaultProps = {
  query: '',
  setQuery: vi.fn(),
  approach: 'function_call',
  setApproach: vi.fn(),
  loading: false,
  onSubmit: vi.fn(),
  onCompare: vi.fn(),
  showCompare: true,
};

function renderForm(props = {}) {
  return render(
    <MemoryRouter>
      <QueryForm {...defaultProps} {...props} />
    </MemoryRouter>
  );
}

describe('QueryForm', () => {
  it('renders textarea and approach buttons', () => {
    renderForm();
    expect(screen.getByPlaceholderText(/predict species/i)).toBeInTheDocument();
    expect(screen.getByText('Function Call')).toBeInTheDocument();
    expect(screen.getByText('Combined Tools')).toBeInTheDocument();
  });

  it('calls setQuery when typing', async () => {
    const setQuery = vi.fn();
    renderForm({ setQuery });
    const textarea = screen.getByPlaceholderText(/predict species/i);
    await userEvent.type(textarea, 'hello');
    expect(setQuery).toHaveBeenCalled();
  });

  it('calls setApproach when clicking Combined Tools', async () => {
    const setApproach = vi.fn();
    renderForm({ setApproach });
    await userEvent.click(screen.getByText('Combined Tools'));
    expect(setApproach).toHaveBeenCalledWith('combined_tools');
  });

  it('displays Function Call as selected by default', () => {
    renderForm();
    const fcButton = screen.getByText('Function Call').closest('button');
    expect(fcButton.className).toContain('border-amber-400');
  });

  it('calls onSubmit when submit button clicked', async () => {
    const onSubmit = vi.fn();
    renderForm({ query: 'test query', onSubmit });
    await userEvent.click(screen.getByText('Submit Query'));
    expect(onSubmit).toHaveBeenCalled();
  });

  it('disables submit when query is empty', () => {
    renderForm({ query: '' });
    const button = screen.getByText('Submit Query');
    expect(button).toBeDisabled();
  });

  it('shows Compare Both button when showCompare is true', () => {
    renderForm({ showCompare: true });
    expect(screen.getByText('Compare Both')).toBeInTheDocument();
  });

  it('hides Compare Both when showCompare is false', () => {
    renderForm({ showCompare: false });
    expect(screen.queryByText('Compare Both')).not.toBeInTheDocument();
  });

  it('shows sample query chips', () => {
    renderForm();
    expect(screen.getByText('Predict species')).toBeInTheDocument();
    expect(screen.getByText('Species stats')).toBeInTheDocument();
    expect(screen.getByText('Compare species')).toBeInTheDocument();
  });

  it('populates query when sample chip is clicked', async () => {
    const setQuery = vi.fn();
    renderForm({ setQuery });
    await userEvent.click(screen.getByText('Predict species'));
    expect(setQuery).toHaveBeenCalledWith(expect.stringContaining('predict'));
  });

  it('submits the clicked sample text explicitly', async () => {
    const onSubmit = vi.fn();
    renderForm({ query: '', onSubmit });
    await userEvent.click(screen.getByText('Predict species'));
    expect(onSubmit).toHaveBeenCalledWith(expect.stringContaining('predict'));
  });

  it('shows loading state on submit button when loading', () => {
    renderForm({ loading: true, query: 'test' });
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  it('disables approach buttons when loading', () => {
    renderForm({ loading: true });
    const buttons = screen.getAllByRole('button');
    const approachButtons = buttons.filter(b =>
      b.textContent.includes('Function Call') || b.textContent.includes('Combined Tools')
    );
    approachButtons.forEach(b => expect(b).toBeDisabled());
  });
});
