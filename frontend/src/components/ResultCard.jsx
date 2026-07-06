import { useState } from 'react';
import { Zap, Sparkles, ChevronDown, ChevronUp, Copy, Check, Database, Brain } from 'lucide-react';

export default function ResultCard({ data, isCompare = false, side = 'left' }) {
  const [expandedSections, setExpandedSections] = useState({ knowledge: true, synthesis: true, results: true });
  const [copied, setCopied] = useState(null);

  if (!data) return null;

  const isCombined = data.rag_used || data.approach === 'combined_tools';
  const isFunction = !isCombined;

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const copyToClipboard = async (text, key) => {
    try {
      await navigator.clipboard.writeText(
        typeof text === 'string' ? text : JSON.stringify(text, null, 2)
      );
      setCopied(key);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      // clipboard API not available
    }
  };

  const borderClass = isFunction ? 'card-function' : 'card-combined';
  const animClass = side === 'left' ? 'animate-slide-in-left' : 'animate-slide-in-right';

  return (
    <div className={`${borderClass} ${animClass}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 flex-wrap">
          {isFunction ? (
            <span className="approach-badge-function">
              <Zap className="w-3.5 h-3.5" />
              Function Call
            </span>
          ) : (
            <span className="approach-badge-combined">
              <Sparkles className="w-3.5 h-3.5" />
              Combined Tools
            </span>
          )}
          {data.rag_used ? (
            <span className="rag-badge">
              <Brain className="w-3 h-3" />
              RAG Enabled
            </span>
          ) : (
            <span className="no-rag-badge">
              <Database className="w-3 h-3" />
              No RAG
            </span>
          )}
        </div>
        <span className="text-xs text-gray-400 font-medium">
          {data.tools_called?.length || 0} tool{data.tools_called?.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Tools Called */}
      {data.tools_called?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-4">
          {data.tools_called.map((tool) => (
            <span key={tool} className="tool-tag" title={`Tool: ${tool}`}>
              {tool}
            </span>
          ))}
        </div>
      )}

      {/* Explanation */}
      <p className="text-sm text-gray-500 mb-4 leading-relaxed">{data.explanation}</p>

      {/* Query */}
      <div className="text-xs text-gray-400 mb-4 italic">
        Query: &ldquo;{data.query}&rdquo;
      </div>

      {/* Function Call: Single Result */}
      {isFunction && data.result && (
        <div className="card-result">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Result</span>
            <button
              onClick={() => copyToClipboard(data.result, 'fc-result')}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              title="Copy result"
            >
              {copied === 'fc-result' ? (
                <Check className="w-3.5 h-3.5 text-emerald-500" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-gray-400" />
              )}
            </button>
          </div>
          <pre className="text-xs bg-gray-50 rounded-lg p-3 overflow-x-auto text-gray-700 font-mono leading-relaxed">
            {JSON.stringify(data.result, null, 2)}
          </pre>
        </div>
      )}

      {/* Combined Tools: Multiple Results */}
      {isCombined && data.results?.length > 0 && (
        <div className="space-y-3 mb-3">
          <button
            onClick={() => toggleSection('results')}
            className="flex items-center justify-between w-full text-left"
          >
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Tool Results ({data.results.length})
            </span>
            {expandedSections.results ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
          </button>
          {expandedSections.results &&
            data.results.map((r, i) => (
              <div key={i} className="card-result">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="tool-tag">{r.tool}</span>
                  <button
                    onClick={() => copyToClipboard(r.result, `ct-${i}`)}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                    title="Copy result"
                  >
                    {copied === `ct-${i}` ? (
                      <Check className="w-3 h-3 text-emerald-500" />
                    ) : (
                      <Copy className="w-3 h-3 text-gray-400" />
                    )}
                  </button>
                </div>
                <pre className="text-xs bg-gray-50 rounded-lg p-2.5 overflow-x-auto text-gray-700 font-mono leading-relaxed max-h-48 overflow-y-auto">
                  {JSON.stringify(r.result, null, 2)}
                </pre>
              </div>
            ))}
        </div>
      )}

      {/* Knowledge Section (Combined Only) */}
      {isCombined && data.knowledge?.length > 0 && (
        <div className="mt-3">
          <button
            onClick={() => toggleSection('knowledge')}
            className="flex items-center justify-between w-full text-left mb-3"
          >
            <span className="text-xs font-semibold text-violet-600 uppercase tracking-wider flex items-center gap-1.5">
              <Brain className="w-3.5 h-3.5" />
              Retrieved Knowledge ({data.knowledge.length})
            </span>
            {expandedSections.knowledge ? <ChevronUp className="w-4 h-4 text-violet-400" /> : <ChevronDown className="w-4 h-4 text-violet-400" />}
          </button>
          {expandedSections.knowledge && (
            <div className="space-y-2.5">
              {data.knowledge.map((k) => (
                <div key={k.doc_id} className="card-knowledge">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-violet-800">{k.title}</span>
                    <span className="text-xs text-violet-500 font-medium">
                      {(k.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  {/* Relevance bar */}
                  <div className="w-full bg-violet-200 rounded-full h-1.5 mb-2">
                    <div
                      className="bg-violet-500 h-1.5 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(k.score * 100, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-violet-700 leading-relaxed">{k.content.slice(0, 250)}...</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Synthesis Section (Combined Only) */}
      {isCombined && data.synthesis && (
        <div className="mt-3">
          <button
            onClick={() => toggleSection('synthesis')}
            className="flex items-center justify-between w-full text-left mb-3"
          >
            <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              AI Synthesis
            </span>
            {expandedSections.synthesis ? <ChevronUp className="w-4 h-4 text-emerald-400" /> : <ChevronDown className="w-4 h-4 text-emerald-400" />}
          </button>
          {expandedSections.synthesis && (
            <div className="card-synthesis">
              <p className="text-sm text-emerald-800 leading-relaxed whitespace-pre-wrap">{data.synthesis}</p>
            </div>
          )}
        </div>
      )}

      {/* Timestamp */}
      {data.created_at && (
        <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-400">
          {new Date(data.created_at).toLocaleString()}
        </div>
      )}
    </div>
  );
}
