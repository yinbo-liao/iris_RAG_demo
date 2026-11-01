import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import AgentPage from '../../pages/AgentPage';
import { runMultiAgent, getAgentRegistry } from '../../api';

vi.mock('../../api', () => ({
  runMultiAgent: vi.fn(),
  getAgentRegistry: vi.fn(),
  queryIris: vi.fn(),
  compareApproaches: vi.fn(),
}));

const agentRun = {
  agent: 'Data Pattern Analysis Agent',
  role: 'Exploratory data analysis',
  model: 'deterministic-python',
  suggested_model: 'GPT-4o-mini',
  permissions: ['read:iris_dataset'],
  status: 'success',
  duration_ms: 12.5,
  reasoning: 'Inspected class balance and correlations.',
  output: { sample_count: 150 },
  error: null,
};

const pipelineResult = {
  run_id: 'abcdef0123456789abcdef0123456789',
  query: 'Analyze Iris dataset and recommend the best classifier.',
  plan: ['Decompose the request.', 'Train classifiers in parallel.', 'Synthesize the report.'],
  agents: [agentRun],
  agent_count: 1,
  pattern_analysis: {},
  model_results: [],
  evaluation: {
    ranking: ['SVM', 'Random Forest'],
    best_model: 'SVM',
    ranked_models: [
      { model: 'SVM', accuracy: 0.95, precision: 0.95, recall: 0.95, f1: 0.95, score: 0.95 },
      { model: 'Random Forest', accuracy: 0.9, precision: 0.9, recall: 0.9, f1: 0.9, score: 0.9 },
    ],
    reason: 'SVM ranks first with weighted score 0.95.',
    tradeoffs: ['Random Forest is cheaper to train.'],
  },
  knowledge: [
    { doc_id: 'setosa_overview', title: 'Iris Setosa Overview', content: 'Small petals.', score: 0.5 },
  ],
  citations: [],
  final_report: {
    headline: 'Recommended classifier: SVM',
    summary: 'SVM ranked first on macro F1.',
    confidence: 'high',
    recommendations: ['Adopt SVM as the primary classifier.'],
    evidence: {},
  },
  duration_ms: 1234.5,
};

const renderPage = () =>
  render(
    <MemoryRouter>
      <AgentPage />
    </MemoryRouter>
  );

describe('AgentPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Pending promise: avoids an async state update in tests that do not assert on the roster.
    getAgentRegistry.mockReturnValue(new Promise(() => {}));
  });

  it('renders the page title and form', () => {
    renderPage();
    expect(screen.getByText('Multi-Agent Analytics')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /run multi-agent analysis/i })).toBeInTheDocument();
  });

  it('renders the empty state initially', () => {
    renderPage();
    expect(screen.getByText('Run the agent team')).toBeInTheDocument();
  });

  it('shows the agent roster from the registry endpoint', async () => {
    getAgentRegistry.mockResolvedValue([
      {
        agent: 'Evaluation Agent',
        role: 'Ranks models',
        model: 'deterministic-python',
        suggested_model: 'GPT-4o-mini',
        permissions: ['read:model_metrics'],
        allowed_inputs: ['model_results'],
      },
    ]);
    renderPage();
    expect(await screen.findByText('Agent Roster (1)')).toBeInTheDocument();
    expect(screen.getByText('Evaluation Agent')).toBeInTheDocument();
    expect(screen.getByText(/inputs: model_results/)).toBeInTheDocument();
  });

  it('submits the request and renders the full report', async () => {
    const user = userEvent.setup();
    runMultiAgent.mockResolvedValue(pipelineResult);
    renderPage();

    await user.type(
      screen.getByPlaceholderText(/analyze the iris dataset/i),
      '  Analyze Iris dataset  '
    );
    await user.click(screen.getByRole('button', { name: /run multi-agent analysis/i }));

    // useQuery passes the (unused) approach argument as its second parameter.
    await waitFor(() =>
      expect(runMultiAgent).toHaveBeenCalledWith('Analyze Iris dataset', expect.anything())
    );

    expect(await screen.findByText('Recommended classifier: SVM')).toBeInTheDocument();
    expect(screen.getByText('high confidence')).toBeInTheDocument();
    expect(screen.getByText('Adopt SVM as the primary classifier.')).toBeInTheDocument();
    expect(screen.getByText('Model Ranking')).toBeInTheDocument();
    expect(screen.getByText('best')).toBeInTheDocument();
    expect(screen.getByText('Agent Audit Trail')).toBeInTheDocument();
    expect(screen.getByText('Data Pattern Analysis Agent')).toBeInTheDocument();
    expect(screen.getByText('Iris Setosa Overview')).toBeInTheDocument();
    expect(screen.getByText('Orchestration Plan')).toBeInTheDocument();
  });

  it('shows an error when the pipeline fails', async () => {
    const user = userEvent.setup();
    runMultiAgent.mockRejectedValue(new Error('Agent pipeline unavailable'));
    renderPage();

    await user.type(screen.getByPlaceholderText(/analyze the iris dataset/i), 'run');
    await user.click(screen.getByRole('button', { name: /run multi-agent analysis/i }));

    expect(await screen.findByText('Agent pipeline unavailable')).toBeInTheDocument();
  });

  it('disables submit for an empty query', () => {
    renderPage();
    expect(screen.getByRole('button', { name: /run multi-agent analysis/i })).toBeDisabled();
  });
});
