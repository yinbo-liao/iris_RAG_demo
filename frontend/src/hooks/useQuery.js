import { useState, useCallback, useRef } from 'react';
import { runMultiAgent } from '../api';

export function useQuery({ submitFn = runMultiAgent } = {}) {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const resultRef = useRef(null);
  // Ref rather than state so rapid Enter presses in the same tick cannot both
  // start a request before React has re-rendered with loading=true.
  const inFlightRef = useRef(false);

  const submitQuery = useCallback(async () => {
    const text = query.trim();
    if (!text || inFlightRef.current) return;

    inFlightRef.current = true;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await submitFn(text);
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
  }, [query, submitFn]);

  return {
    query,
    setQuery,
    result,
    loading,
    error,
    submitQuery,
    resultRef,
  };
}
