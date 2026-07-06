import { useEffect } from 'react';
import { Zap, Sparkles, Send, GitCompare, ArrowRight } from 'lucide-react';

const SAMPLE_QUERIES = [
  { label: 'Predict species', query: 'predict species for 5.1 3.5 1.4 0.2' },
  { label: 'Species stats', query: 'stats for setosa' },
  { label: 'Compare species', query: 'compare setosa and versicolor' },
  { label: 'Filter flowers', query: 'filter flowers with petal length between 3 and 6' },
  { label: 'List all', query: 'list all iris species' },
];

export default function QueryForm({
  query,
  setQuery,
  approach,
  setApproach,
  loading,
  onSubmit,
  onCompare,
  showCompare = true,
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        onCompare?.();
      } else if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        onSubmit?.();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onSubmit, onCompare]);

  const handleSampleClick = (sampleQuery) => {
    setQuery(sampleQuery);
    // Auto-submit with current approach after a short delay
    setTimeout(() => onSubmit?.(), 200);
  };

  return (
    <div className="w-full animate-fade-in">
      {/* Query Input */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 space-y-4">
        <label className="block text-sm font-semibold text-gray-700">
          Enter your query
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., predict species for sepal_length=5.1 sepal_width=3.5 petal_length=1.4 petal_width=0.2"
          rows={3}
          disabled={loading}
          className="w-full px-4 py-3 rounded-lg border border-gray-200 text-gray-900 placeholder-gray-400
                     focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-shadow
                     disabled:bg-gray-50 disabled:text-gray-400 resize-none text-sm"
        />
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{query.length} characters</span>
          <span>Enter to submit · Ctrl+Enter to compare</span>
        </div>
      </div>

      {/* Approach Selector */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        <button
          type="button"
          disabled={loading}
          onClick={() => setApproach('function_call')}
          className={`p-4 rounded-xl border-2 text-left transition-all duration-200 ${
            approach === 'function_call'
              ? 'border-amber-400 bg-amber-50 shadow-sm'
              : 'border-gray-200 bg-white hover:border-amber-200 hover:bg-amber-50/50'
          }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <Zap className={`w-5 h-5 ${approach === 'function_call' ? 'text-amber-600' : 'text-gray-400'}`} />
            <span className={`font-semibold text-sm ${approach === 'function_call' ? 'text-amber-800' : 'text-gray-700'}`}>
              Function Call
            </span>
          </div>
          <p className="text-xs text-gray-500 ml-7">Single tool · Fast · No RAG</p>
        </button>

        <button
          type="button"
          disabled={loading}
          onClick={() => setApproach('combined_tools')}
          className={`p-4 rounded-xl border-2 text-left transition-all duration-200 ${
            approach === 'combined_tools'
              ? 'border-emerald-400 bg-emerald-50 shadow-sm'
              : 'border-gray-200 bg-white hover:border-emerald-200 hover:bg-emerald-50/50'
          }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className={`w-5 h-5 ${approach === 'combined_tools' ? 'text-emerald-600' : 'text-gray-400'}`} />
            <span className={`font-semibold text-sm ${approach === 'combined_tools' ? 'text-emerald-800' : 'text-gray-700'}`}>
              Combined Tools
            </span>
          </div>
          <p className="text-xs text-gray-500 ml-7">Multi-tool · RAG · Synthesis</p>
        </button>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3 mt-4">
        <button
          onClick={() => onSubmit?.()}
          disabled={loading || !query.trim()}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-violet-600 text-white rounded-xl
                     font-semibold text-sm hover:bg-violet-700 focus:ring-2 focus:ring-violet-500 focus:ring-offset-2
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
        >
          {loading ? (
            <>
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Processing...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Submit Query
            </>
          )}
        </button>

        {showCompare && (
          <button
            onClick={onCompare}
            disabled={loading || !query.trim()}
            className="flex items-center justify-center gap-2 px-5 py-3 border-2 border-gray-200 text-gray-700
                       rounded-xl font-semibold text-sm hover:border-violet-300 hover:text-violet-700 hover:bg-violet-50
                       disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <GitCompare className="w-4 h-4" />
            Compare Both
          </button>
        )}
      </div>

      {/* Sample Queries */}
      <div className="mt-5">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2.5">Try a sample query</p>
        <div className="flex flex-wrap gap-2">
          {SAMPLE_QUERIES.map((sq) => (
            <button
              key={sq.label}
              type="button"
              disabled={loading}
              onClick={() => handleSampleClick(sq.query)}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium
                         bg-gray-100 text-gray-600 hover:bg-violet-100 hover:text-violet-700
                         border border-gray-200 hover:border-violet-200 transition-all
                         disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              {sq.label}
              <ArrowRight className="w-3 h-3 opacity-0 -ml-1 group-hover:opacity-100 group-hover:ml-0 transition-all" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
