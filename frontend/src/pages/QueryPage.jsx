import { useRef } from 'react';
import QueryForm from '../components/QueryForm';
import ResultCard from '../components/ResultCard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { useQuery } from '../hooks/useQuery';

export default function QueryPage() {
  const {
    query, setQuery, approach, setApproach,
    result, loading, error, submitQuery, resultRef,
  } = useQuery();

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Query Iris Dataset</h2>
        <p className="text-sm text-gray-500 mt-1">
          Ask a question about the Iris flower dataset using natural language.
        </p>
      </div>

      <QueryForm
        query={query}
        setQuery={setQuery}
        approach={approach}
        setApproach={setApproach}
        loading={loading}
        onSubmit={() => submitQuery()}
        onCompare={null}
        showCompare={false}
      />

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 animate-fade-in">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && <LoadingSpinner />}

      {/* Result */}
      {!loading && result && (
        <div ref={resultRef}>
          <ResultCard data={result} />
        </div>
      )}

      {/* Empty State */}
      {!loading && !result && !error && (
        <EmptyState
          icon="search"
          title="Ready to explore"
          description="Type a query above to analyze the Iris dataset. Try predicting a species, getting statistics, or comparing flowers."
        />
      )}
    </div>
  );
}
