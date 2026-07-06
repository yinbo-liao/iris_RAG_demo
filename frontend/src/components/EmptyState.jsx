import { Inbox, Search, Database } from 'lucide-react';

const iconMap = {
  inbox: Inbox,
  search: Search,
  database: Database,
};

export default function EmptyState({
  icon = 'inbox',
  title = 'No data yet',
  description = 'Start by submitting a query to see results here.',
  action,
}) {
  const Icon = iconMap[icon] || Inbox;

  return (
    <div className="flex items-center justify-center py-16 px-4 animate-fade-in">
      <div className="text-center max-w-sm">
        <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <Icon className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-base font-semibold text-gray-700 mb-1.5">{title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed mb-5">{description}</p>
        {action && (
          <button
            onClick={action.onClick}
            className="inline-flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg
                       text-sm font-medium hover:bg-violet-700 transition-colors"
          >
            {action.label}
          </button>
        )}
      </div>
    </div>
  );
}
