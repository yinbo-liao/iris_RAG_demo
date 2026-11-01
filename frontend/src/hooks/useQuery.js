import { useState, useCallback, useRef } from 'react';
import { queryIris, compareApproaches } from '../api';

export function useQuery({ submitFn = queryIris, compareFn = compareApproaches } = {}) {
  const [query, setQuery] = useState('');
  const [approach, setApproach] = useState('function_call');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const resultRef = useRef(null);
  // Ref rather than state so rapid Enter presses in the same tick cannot both
  // start a request before React has re-rendered with loading=true.
  const inFlightRef = useRef(false);

  const submitQuery = useCallback(async (overrideApproach, explicitQuery) => {
    const approachToUse = overrideApproach || approach;
    // Callers may pass the text explicitly (e.g. sample-query chips) so the
    // submission does not depend on a re-render having picked up setQuery yet.
    const text = (explicitQuery ?? query).trim();
    if (!text || inFlightRef.current) return;

    inFlightRef.current = true;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await submitFn(text, approachToUse);
      setResult(data);
      resultRef.current = data;
      // Smooth scroll to results
      setTimeout(() => {
        resultRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      inFlightRef.current = false;
      setLoading(false);
    }
  }, [query, approach, submitFn]);

  const submitCompare = useCallback(async () => {
    if (!query.trim() || inFlightRef.current) return;

    inFlightRef.current = true;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await compareFn(query.trim());
      setResult(data);
      resultRef.current = data;
      setTimeout(() => {
        resultRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError(err.message);
    } finally {
      inFlightRef.current = false;
      setLoading(false);
    }
  }, [query, compareFn]);

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
