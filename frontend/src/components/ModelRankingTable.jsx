import { Trophy, Scale } from 'lucide-react';

const METRICS = [
  { key: 'accuracy', label: 'Accuracy' },
  { key: 'precision', label: 'Precision' },
  { key: 'recall', label: 'Recall' },
  { key: 'f1', label: 'F1' },
  { key: 'score', label: 'Weighted' },
];

const pct = (value) => `${(value * 100).toFixed(1)}%`;

export default function ModelRankingTable({ evaluation }) {
  const models = evaluation?.ranked_models || [];

  if (models.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-gray-800 flex items-center gap-1.5">
          <Trophy className="w-4 h-4 text-amber-500" />
          Model Ranking
        </h3>
        <span className="text-xs text-gray-400">
          Best: <span className="font-semibold text-gray-700">{evaluation.best_model}</span>
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wider text-gray-400 border-b border-gray-100">
              <th className="py-2 pr-2">#</th>
              <th className="py-2 pr-2">Model</th>
              {METRICS.map((metric) => (
                <th key={metric.key} className="py-2 px-2 text-right">{metric.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {models.map((model, index) => {
              const isBest = index === 0;
              return (
                <tr
                  key={model.model}
                  className={`border-b border-gray-50 ${isBest ? 'bg-amber-50/60' : ''}`}
                >
                  <td className="py-2.5 pr-2 text-gray-500">{index + 1}</td>
                  <td className="py-2.5 pr-2 font-semibold text-gray-800">
                    {model.display_name || model.model}
                    {isBest && <span className="ml-2 text-[10px] uppercase text-amber-600">best</span>}
                    {model.engine && (
                      <div className="text-[10px] font-normal text-gray-400">{model.engine}</div>
                    )}
                  </td>
                  {METRICS.map((metric) => (
                    <td
                      key={metric.key}
                      className={`py-2.5 px-2 text-right font-mono ${
                        isBest ? 'text-amber-800 font-semibold' : 'text-gray-600'
                      }`}
                    >
                      {pct(model[metric.key] ?? 0)}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-gray-500 mt-3 flex items-start gap-1.5">
        <Scale className="w-3.5 h-3.5 mt-0.5 shrink-0 text-gray-400" />
        {evaluation.reason}
      </p>
      {evaluation.tradeoffs?.length > 0 && (
        <ul className="mt-2 space-y-1 text-xs text-gray-500 list-disc list-inside">
          {evaluation.tradeoffs.map((tradeoff) => (
            <li key={tradeoff}>{tradeoff}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
