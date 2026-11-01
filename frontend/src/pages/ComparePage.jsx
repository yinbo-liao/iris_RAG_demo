import { useRef } from 'react';
import QueryForm from '../components/QueryForm';
import ResultCard from '../components/ResultCard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { useQuery } from '../hooks/useQuery';
import { GitCompare } from 'lucide-react';

export default function ComparePage() {
  const {
    query, setQuery, approach, setApproach,
    result, loading, error, submitCompare, resultRef,
  } = useQuery();

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Compare Approaches</h2>
        <p className="text-sm text-gray-500 mt-1">
          See how Function Call and Combined Tools process the same query differently.
        </p>
      </div>

      <div className="max-w-3xl">
        <QueryForm
          query={query}
          setQuery={setQuery}
          approach={approach}
          setApproach={setApproach}
          loading={loading}
          onSubmit={null}
          onCompare={submitCompare}
          showCompare={true}
          showApproach={false}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 animate-fade-in">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LoadingSpinner />
          <LoadingSpinner />
        </div>
      )}

      {/* Results */}
      {!loading && result && (
        <div ref={resultRef}>
          {/* VS Divider */}
          <div className="flex items-center justify-center my-4">
            <div className="flex items-center gap-3 px-6 py-2 bg-violet-100 text-violet-700 rounded-full font-bold text-sm shadow-sm">
              <GitCompare className="w-4 h-4" />
              VS
              <GitCompare className="w-4 h-4" />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-stagger">
            <ResultCard data={result.function_call} isCompare side="left" />
            <ResultCard data={result.combined_tools} isCompare side="right" />
          </div>

          {/* Diff summary */}
          <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="text-sm font-bold text-gray-700 mb-3">Key Differences</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <DiffItem
                label="Tools Called"
                left={result.function_call.tools_called?.length || 0}
                right={result.combined_tools.tools_called?.length || 0}
              />
              <DiffItem
                label="RAG Used"
                left="No"
                right="Yes"
                leftColor="text-gray-400"
                rightColor="text-violet-600"
              />
              <DiffItem
                label="Knowledge Docs"
                left={0}
                right={result.combined_tools.knowledge?.length || 0}
              />
              <DiffItem
                label="Has Synthesis"
                left="No"
                right={result.combined_tools.synthesis ? 'Yes' : 'No'}
                leftColor="text-gray-400"
                rightColor="text-emerald-600"
              />
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !result && !error && (
        <EmptyState
          icon="search"
          title="Compare both approaches"
          description="Type a query and click 'Compare Both' to see how Function Call and Combined Tools process it side by side."
        />
      )}
    </div>
  );
}

function DiffItem({ label, left, right, leftColor, rightColor }) {
  return (
    <div className="text-center p-3 rounded-lg bg-gray-50">
      <p className="text-xs text-gray-400 font-medium mb-1.5">{label}</p>
      <div className="flex items-center justify-center gap-2 text-sm font-bold">
        <span className={leftColor || 'text-amber-600'}>{left}</span>
        <span className="text-gray-300">vs</span>
        <span className={rightColor || 'text-emerald-600'}>{right}</span>
      </div>
    </div>
  );
}
