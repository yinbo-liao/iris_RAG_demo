import { useState, useCallback, useRef } from 'react';
import { queryIris, compareApproaches } from '../api';

export function useQuery() {
  const [query, setQuery] = useState('');
  const [approach, setApproach] = useState('function_call');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const resultRef = useRef(null);

  const submitQuery = useCallback(async (overrideApproach) => {
    const approachToUse = overrideApproach || approach;
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await queryIris(query.trim(), approachToUse);
      setResult(data);
      resultRef.current = data;
      // Smooth scroll to results
      setTimeout(() => {
        resultRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [query, approach]);

  const submitCompare = useCallback(async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await compareApproaches(query.trim());
      setResult(data);
      resultRef.current = data;
      setTimeout(() => {
        resultRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [query]);

  return {
    query,
    setQuery,
    approach,
    setApproach,
    result,
    loading,
    error,
    submitQuery,
    submitCompare,
    resultRef,
  };
}
