import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ResultCard from '../../components/ResultCard';

const functionCallData = {
  approach: 'function_call',
  approach_label: 'Function Call',
  tools_called: ['predict_species'],
  rag_used: false,
  result: { predicted_species: 'setosa', confidence: 98.5 },
  explanation: 'Matched pattern → executed predict_species',
  query: 'predict 5.1 3.5 1.4 0.2',
};

const combinedToolsData = {
  approach: 'combined_tools',
  approach_label: 'Combined Tools (RAG + Functions)',
  tools_called: ['get_species_stats', 'retrieve_knowledge'],
  rag_used: true,
  results: [
    { tool: 'get_species_stats', result: { species: 'setosa', sample_count: 50 } },
  ],
  knowledge: [
    { doc_id: 'setosa_overview', title: 'Setosa Overview', content: 'Iris setosa...', score: 0.85 },
  ],
  synthesis: '### AI Synthesis\nSetosa is the smallest species.',
  explanation: 'Retrieved knowledge and executed tools',
  query: 'tell me about setosa',
};

describe('ResultCard', () => {
  it('renders null when no data', () => {
    const { container } = render(<ResultCard data={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders Function Call approach badge', () => {
    render(<ResultCard data={functionCallData} />);
    expect(screen.getByText('Function Call')).toBeInTheDocument();
    expect(screen.getByText('No RAG')).toBeInTheDocument();
  });

  it('renders Combined Tools approach badge', () => {
    render(<ResultCard data={combinedToolsData} />);
    expect(screen.getByText('Combined Tools')).toBeInTheDocument();
    expect(screen.getByText('RAG Enabled')).toBeInTheDocument();
  });

  it('displays tool tags', () => {
    render(<ResultCard data={functionCallData} />);
    expect(screen.getByText('predict_species')).toBeInTheDocument();
  });

  it('displays multiple tool tags for combined', () => {
    render(<ResultCard data={combinedToolsData} />);
    const tags = screen.getAllByText('get_species_stats');
    expect(tags.length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('retrieve_knowledge').length).toBeGreaterThanOrEqual(1);
  });

  it('shows tool count', () => {
    render(<ResultCard data={functionCallData} />);
    expect(screen.getByText('1 tool')).toBeInTheDocument();
  });

  it('shows query text', () => {
    render(<ResultCard data={functionCallData} />);
    expect(screen.getByText(/predict 5.1 3.5 1.4 0.2/)).toBeInTheDocument();
  });

  it('renders knowledge section for combined tools', () => {
    render(<ResultCard data={combinedToolsData} />);
    expect(screen.getByText('Retrieved Knowledge (1)')).toBeInTheDocument();
    expect(screen.getByText('Setosa Overview')).toBeInTheDocument();
  });

  it('renders synthesis section for combined tools', () => {
    render(<ResultCard data={combinedToolsData} />);
    expect(screen.getByText('AI Synthesis')).toBeInTheDocument();
  });

  it('renders result JSON for function call', () => {
    render(<ResultCard data={functionCallData} />);
    expect(screen.getByText(/setosa/)).toBeInTheDocument();
  });
});
