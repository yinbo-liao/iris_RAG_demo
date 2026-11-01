import { useState, useEffect, useCallback } from 'react';
import { getHistory, clearHistory as clearHistoryRequest } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import ErrorBoundary from '../components/ErrorBoundary';
import { Zap, Sparkles, Network, Brain, Clock, ChevronDown, ChevronUp, Trash2 } from 'lucide-react';

const RELATIVE_TIME = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });

function timeAgo(dateStr) {
  const diff = new Date(dateStr) - new Date();
  const seconds = Math.round(diff / 1000);
  const minutes = Math.round(seconds / 60);
  const hours = Math.round(minutes / 60);
  const days = Math.round(hours / 24);

  if (Math.abs(days) > 0) return RELATIVE_TIME.format(days, 'day');
  if (Math.abs(hours) > 0) return RELATIVE_TIME.format(hours, 'hour');
  if (Math.abs(minutes) > 0) return RELATIVE_TIME.format(minutes, 'minute');
  return 'Just now';
}

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory(50);
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const clearHistory = async () => {
    if (!confirm('Clear all query history? This cannot be undone.')) return;
    try {
      await clearHistoryRequest();
      setHistory([]);
      setExpandedId(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Query History</h2>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Query History</h2>
            <p className="text-sm text-gray-500 mt-1">
              {history.length} query {history.length !== 1 ? 'entries' : 'entry'} logged
            </p>
          </div>
          {history.length > 0 && (
            <button
              onClick={clearHistory}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50
                         rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Clear All
            </button>
          )}
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
            {error}
            <button onClick={fetchHistory} className="ml-2 underline font-semibold">Retry</button>
          </div>
        )}

        {/* Empty State */}
        {!error && history.length === 0 && (
          <EmptyState
            icon="inbox"
            title="No query history"
            description="Your query history will appear here after you submit your first query."
          />
        )}

        {/* History List */}
        {history.length > 0 && (
          <div className="space-y-3">
            {history.map((entry) => {
              const isExpanded = expandedId === entry.id;
              const isMultiAgent = entry.approach === 'multi_agent';
              const isCombined = entry.approach === 'combined_tools';
              const ragUsed = entry.rag_used === 'yes';
              // Multi-agent logs store the winning model's F1 (0-1); other
              // approaches have no confidence at all.
              const confidencePct = entry.confidence == null
                ? null
                : (isMultiAgent ? entry.confidence * 100 : entry.confidence);

              return (
                <div
                  key={entry.id}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow animate-fade-in"
                >
                  {/* Summary Row */}
                  <button
                    onClick={() => toggleExpand(entry.id)}
                    className="w-full text-left p-4 flex items-center gap-4"
                  >
                    {/* Approach Badge */}
                    {isMultiAgent ? (
                      <span className="rag-badge flex-shrink-0" title="Multi-agent pipeline">
                        <Network className="w-3 h-3" />
                        Multi-Agent
                      </span>
                    ) : isCombined ? (
                      <span className="approach-badge-combined flex-shrink-0">
                        <Sparkles className="w-3 h-3" />
                        Combined
                      </span>
                    ) : (
                      <span className="approach-badge-function flex-shrink-0">
                        <Zap className="w-3 h-3" />
                        Function
                      </span>
                    )}

                    {/* RAG Badge */}
                    {ragUsed ? (
                      <span className="rag-badge flex-shrink-0">
                        <Brain className="w-3 h-3" />
                        RAG
                      </span>
                    ) : (
                      <span className="no-rag-badge flex-shrink-0">No RAG</span>
                    )}

                    {/* Query Text */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800 font-medium truncate">
                        {entry.query_text}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {timeAgo(entry.created_at)}
                        {entry.tools_called?.length > 0 && (
                          <>
                            <span className="mx-1">·</span>
                            {entry.tools_called.length} tool{entry.tools_called.length !== 1 ? 's' : ''}
                          </>
                        )}
                      </p>
                    </div>

                    {/* Expand Icon */}
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    )}
                  </button>

                  {/* Expanded Detail */}
                  {isExpanded && entry.result_data && (
                    <div className="px-4 pb-4 border-t border-gray-100 pt-3 animate-fade-in">
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {entry.tools_called?.map((tool) => (
                          <span key={tool} className="tool-tag">{tool}</span>
                        ))}
                      </div>
                      <pre className="text-xs bg-gray-50 rounded-lg p-3 overflow-x-auto text-gray-700 font-mono leading-relaxed max-h-64 overflow-y-auto">
                        {JSON.stringify(entry.result_data, null, 2)}
                      </pre>
                      {confidencePct != null && (
                        <p className="text-xs text-gray-400 mt-2">
                          {isMultiAgent ? 'Best model F1' : 'Confidence'}: {confidencePct.toFixed(1)}%
                        </p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}
