import { useState, useEffect } from 'react';
import { useStats } from '../hooks/useStats';
import { getKnowledge } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBoundary from '../components/ErrorBoundary';
import {
  BarChart3, Database, Wrench, BookOpen,
  ChevronDown, ChevronUp, Flower2,
} from 'lucide-react';

export default function KnowledgePage() {
  const { stats, loading: statsLoading, error: statsError, refresh } = useStats();
  const [knowledge, setKnowledge] = useState([]);
  const [knowledgeLoading, setKnowledgeLoading] = useState(true);
  const [expandedDocs, setExpandedDocs] = useState({});

  useEffect(() => {
    getKnowledge()
      .then(setKnowledge)
      .catch(() => {})
      .finally(() => setKnowledgeLoading(false));
  }, []);

  const toggleDoc = (docId) => {
    setExpandedDocs((prev) => ({ ...prev, [docId]: !prev[docId] }));
  };

  if (statsLoading || knowledgeLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Knowledge Base</h2>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Knowledge Base</h2>
          <p className="text-sm text-gray-500 mt-1">
            Explore the Iris dataset statistics, feature ranges, and RAG knowledge documents.
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              icon={BarChart3}
              label="Total Samples"
              value={stats.total_samples}
              color="bg-blue-50 text-blue-600"
            />
            <StatCard
              icon={Flower2}
              label="Species"
              value={stats.species_distribution?.length || 3}
              color="bg-pink-50 text-pink-600"
            />
            <StatCard
              icon={BookOpen}
              label="Knowledge Docs"
              value={stats.knowledge_doc_count}
              color="bg-violet-50 text-violet-600"
            />
            <StatCard
              icon={Wrench}
              label="Available Tools"
              value={stats.tools_count}
              color="bg-emerald-50 text-emerald-600"
            />
          </div>
        )}

        {/* Species Distribution */}
        {stats?.species_distribution && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="section-title">
              <Flower2 className="w-5 h-5 text-pink-500" />
              Species Distribution
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {stats.species_distribution.map((s) => (
                <div key={s.species} className="p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700 capitalize">{s.species}</span>
                    <span className="text-lg font-bold text-gray-900">{s.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-violet-400 to-indigo-500 h-2 rounded-full transition-all duration-700"
                      style={{ width: `${(s.count / stats.total_samples) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1.5">
                    {((s.count / stats.total_samples) * 100).toFixed(1)}% of total
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Feature Ranges */}
        {stats?.feature_ranges && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="section-title">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              Feature Ranges (cm)
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-3 font-semibold text-gray-600">Feature</th>
                    <th className="text-right py-2 px-3 font-semibold text-gray-600">Min</th>
                    <th className="text-right py-2 px-3 font-semibold text-gray-600">Max</th>
                    <th className="text-right py-2 px-3 font-semibold text-gray-600">Avg</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(stats.feature_ranges).map(([key, val]) => (
                    <tr key={key} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="py-2.5 px-3 font-medium text-gray-800 capitalize">
                        {key.replace(/_/g, ' ')}
                      </td>
                      <td className="py-2.5 px-3 text-right text-gray-600 font-mono">{val.min}</td>
                      <td className="py-2.5 px-3 text-right text-gray-600 font-mono">{val.max}</td>
                      <td className="py-2.5 px-3 text-right text-gray-600 font-mono">{val.avg}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Knowledge Documents */}
        {knowledge.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="section-title mb-4">
              <BookOpen className="w-5 h-5 text-violet-500" />
              Knowledge Documents
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {knowledge.map((doc) => {
                const isExpanded = expandedDocs[doc.doc_id] ?? false;
                return (
                  <div
                    key={doc.doc_id}
                    className="card-knowledge hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => toggleDoc(doc.doc_id)}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-sm font-semibold text-violet-800">{doc.title}</span>
                        <span className="ml-2 inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-violet-200 text-violet-700">
                          {doc.category}
                        </span>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-violet-400 flex-shrink-0 mt-1" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-violet-400 flex-shrink-0 mt-1" />
                      )}
                    </div>
                    <p className={`text-xs text-violet-700 leading-relaxed mt-2 transition-all ${
                      isExpanded ? '' : 'line-clamp-3'
                    }`}>
                      {doc.content}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Error State */}
        {statsError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
            Failed to load statistics. {' '}
            <button onClick={refresh} className="underline font-semibold hover:text-red-800">
              Retry
            </button>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="stat-card animate-fade-in">
      <div className="flex items-center justify-between">
        <span className="stat-label">{label}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="stat-value mt-2">{value}</div>
    </div>
  );
}
