import { useState } from 'react';
import { CheckCircle2, XCircle, ChevronDown, ChevronUp, Shield, Clock, Cpu } from 'lucide-react';

export default function AgentAuditCard({ run }) {
  const [open, setOpen] = useState(false);
  const success = run.status === 'success';

  return (
    <div
      className={`bg-white rounded-xl shadow-sm border-l-4 p-4 transition-shadow hover:shadow-md ${
        success ? 'border-violet-400' : 'border-red-400'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <h4 className="text-sm font-bold text-gray-900">{run.agent}</h4>
          <p className="text-xs text-gray-500 mt-0.5">{run.role}</p>
        </div>
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${
            success
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-red-50 text-red-700 border-red-200'
          }`}
        >
          {success ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
          {run.status}
        </span>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1">
          <Cpu className="w-3 h-3" /> {run.model}
        </span>
        <span className="inline-flex items-center gap-1">
          <Clock className="w-3 h-3" /> {run.duration_ms.toFixed(0)} ms
        </span>
      </div>
      {run.suggested_model && (
        <p className="text-xs text-gray-400 mt-1">Suggested model tier: {run.suggested_model}</p>
      )}

      <p className="text-xs text-gray-600 mt-2 leading-relaxed">{run.reasoning}</p>

      {run.error && (
        <p className="text-xs text-red-600 mt-2 font-mono bg-red-50 rounded p-2">{run.error}</p>
      )}

      <div className="flex flex-wrap gap-1 mt-2.5">
        {run.permissions.map((permission) => (
          <span
            key={permission}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-mono bg-violet-50 text-violet-700 border border-violet-100"
          >
            <Shield className="w-2.5 h-2.5" /> {permission}
          </span>
        ))}
      </div>

      {Object.keys(run.output || {}).length > 0 && (
        <div className="mt-3">
          <button
            type="button"
            onClick={() => setOpen((value) => !value)}
            className="flex items-center gap-1 text-xs font-semibold text-violet-600 hover:text-violet-800"
          >
            {open ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            {open ? 'Hide raw output' : 'View raw output'}
          </button>
          {open && (
            <pre className="mt-2 text-[11px] bg-gray-50 border border-gray-100 rounded-lg p-3 overflow-auto max-h-64 text-gray-700 font-mono leading-relaxed">
              {JSON.stringify(run.output, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
