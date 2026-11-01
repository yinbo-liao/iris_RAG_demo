export default function KnowledgeList({ documents }) {
  return (
    <div className="space-y-2.5">
      {documents.map((doc) => (
        <div key={doc.doc_id} className="card-knowledge">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-violet-800">{doc.title}</span>
            <span className="text-xs text-violet-500 font-medium">
              {(doc.score * 100).toFixed(1)}%
            </span>
          </div>
          {/* Relevance bar */}
          <div className="w-full bg-violet-200 rounded-full h-1.5 mb-2">
            <div
              className="bg-violet-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(doc.score * 100, 100)}%` }}
            />
          </div>
          <p className="text-xs text-violet-700 leading-relaxed">{doc.content.slice(0, 250)}...</p>
        </div>
      ))}
    </div>
  );
}
