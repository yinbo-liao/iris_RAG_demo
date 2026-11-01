import { useEffect, useState } from 'react';
import {
  Network,
  Play,
  BookOpen,
  ListChecks,
  Gauge,
  Users,
  Loader2,
} from 'lucide-react';
import { runMultiAgent, getAgentRegistry } from '../api';
import { useQuery } from '../hooks/useQuery';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import AgentAuditCard from '../components/AgentAuditCard';
import ModelRankingTable from '../components/ModelRankingTable';
import KnowledgeList from '../components/KnowledgeList';

const SAMPLE_REQUESTS = [
  'Analyze Iris dataset and recommend the best classifier.',
  'Which model separates versicolor from virginica most reliably?',
  'Explain how petal width drives classification performance.',
];

const CONFIDENCE_STYLES = {
  high: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-red-100 text-red-700 border-red-200',
};

export default function AgentPage() {
  const { query, setQuery, result, loading, error, submitQuery, resultRef } = useQuery({
    submitFn: runMultiAgent,
  });
  const [registry, setRegistry] = useState([]);

  useEffect(() => {
    let active = true;
    getAgentRegistry()
      .then((data) => {
        if (active) setRegistry(data);
      })
      .catch(() => {
        /* registry is decorative; the pipeline still works without it */
      });
    return () => {
      active = false;
    };
  }, []);

  const useSample = (sample) => {
    setQuery(sample);
    setTimeout(() => {
      document.getElementById('agent-submit')?.focus();
    }, 0);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Network className="w-6 h-6 text-violet-600" />
          Multi-Agent Analytics
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          An orchestrator delegates EDA, model training, evaluation, and knowledge retrieval to
          seven least-privilege agents, then synthesizes an executive report.
        </p>
      </div>

      {/* Request form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 space-y-4">
        <label htmlFor="agent-query" className="block text-sm font-semibold text-gray-700">
          Analytics request
        </label>
        <textarea
          id="agent-query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              submitQuery();
            }
          }}
          placeholder="e.g., Analyze the Iris dataset and recommend the best classifier."
          rows={3}
          disabled={loading}
          className="w-full px-4 py-3 rounded-lg border border-gray-200 text-gray-900 placeholder-gray-400
                     focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-shadow
                     disabled:bg-gray-50 disabled:text-gray-400 resize-none text-sm"
        />
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{query.length} characters</span>
          <span>Enter to run · Shift+Enter for a new line</span>
        </div>

        <button
          id="agent-submit"
          type="button"
          onClick={() => submitQuery()}
          disabled={loading || !query.trim()}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-violet-600 text-white rounded-xl
                     font-semibold text-sm hover:bg-violet-700 focus:ring-2 focus:ring-violet-500 focus:ring-offset-2
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin w-4 h-4" />
              Agents working...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Run Multi-Agent Analysis
            </>
          )}
        </button>

        <div className="pt-1">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Try a sample request
          </p>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_REQUESTS.map((sample) => (
              <button
                key={sample}
                type="button"
                disabled={loading}
                onClick={() => useSample(sample)}
                className="px-3 py-1.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600
                           hover:bg-violet-100 hover:text-violet-700 border border-gray-200
                           hover:border-violet-200 transition-all disabled:opacity-50"
              >
                {sample}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 animate-fade-in">
          {error}
        </div>
      )}

      {loading && <LoadingSpinner />}

      {!loading && !result && !error && (
        <>
          <EmptyState
            icon="search"
            title="Run the agent team"
            description="Submit a request above. The orchestrator will plan the work, fan out to the specialist agents, and return an evidence-backed recommendation."
          />
          {registry.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <h3 className="text-sm font-bold text-gray-800 flex items-center gap-1.5 mb-3">
                <Users className="w-4 h-4 text-violet-500" />
                Agent Roster ({registry.length})
              </h3>
              <div className="grid gap-2 sm:grid-cols-2">
                {registry.map((agent) => (
                  <div key={agent.agent} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                    <p className="text-sm font-semibold text-gray-800">{agent.agent}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{agent.role}</p>
                    <p className="text-[11px] text-violet-600 mt-1 font-mono">
                      {agent.allowed_inputs.length > 0
                        ? `inputs: ${agent.allowed_inputs.join(', ')}`
                        : 'no external inputs'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {!loading && result && (
        <div ref={resultRef} className="space-y-5 animate-fade-in">
          {/* Final report */}
          <div className="bg-white rounded-xl shadow-sm border-l-4 border-violet-500 p-5">
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <p className="text-xs font-semibold text-violet-600 uppercase tracking-wider">
                  Executive Report
                </p>
                <h3 className="text-lg font-bold text-gray-900 mt-1">{result.final_report.headline}</h3>
              </div>
              <span
                className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${
                  CONFIDENCE_STYLES[result.final_report.confidence] || CONFIDENCE_STYLES.low
                }`}
              >
                {result.final_report.confidence} confidence
              </span>
            </div>

            <p className="text-sm text-gray-600 mt-3 leading-relaxed">{result.final_report.summary}</p>

            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mt-4 mb-2">
              Recommendations
            </h4>
            <ul className="space-y-1.5">
              {result.final_report.recommendations.map((recommendation) => (
                <li key={recommendation} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-violet-400 shrink-0" />
                  {recommendation}
                </li>
              ))}
            </ul>

            <div className="flex flex-wrap gap-x-5 gap-y-1 mt-4 pt-3 border-t border-gray-100 text-xs text-gray-400">
              <span className="inline-flex items-center gap-1">
                <Gauge className="w-3 h-3" /> {result.duration_ms.toFixed(0)} ms total
              </span>
              <span className="inline-flex items-center gap-1">
                <Users className="w-3 h-3" /> {result.agent_count} agents
              </span>
              <span className="font-mono">run {result.run_id.slice(0, 8)}</span>
            </div>
          </div>

          {/* Plan */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="text-sm font-bold text-gray-800 flex items-center gap-1.5 mb-3">
              <ListChecks className="w-4 h-4 text-violet-500" />
              Orchestration Plan
            </h3>
            <ol className="space-y-2">
              {result.plan.map((step, index) => (
                <li key={step} className="flex items-start gap-3 text-sm text-gray-700">
                  <span className="w-5 h-5 rounded-full bg-violet-100 text-violet-700 text-xs font-bold
                                   flex items-center justify-center shrink-0 mt-0.5">
                    {index + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
          </div>

          {/* Ranking */}
          <ModelRankingTable evaluation={result.evaluation} />

          {/* Agent audit trail */}
          <div>
            <h3 className="text-sm font-bold text-gray-800 mb-3">Agent Audit Trail</h3>
            <div className="grid gap-3 md:grid-cols-2">
              {result.agents.map((run) => (
                <AgentAuditCard key={run.agent} run={run} />
              ))}
            </div>
          </div>

          {/* Knowledge */}
          {result.knowledge?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <h3 className="text-sm font-bold text-gray-800 flex items-center gap-1.5 mb-3">
                <BookOpen className="w-4 h-4 text-violet-500" />
                Retrieved Knowledge ({result.knowledge.length})
              </h3>
              <KnowledgeList documents={result.knowledge} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
