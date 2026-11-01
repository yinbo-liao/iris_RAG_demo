export default function LoadingSpinner() {
  return (
    <div className="animate-fade-in space-y-4 mt-6">
      {/* Skeleton for a result card header */}
      <div className="bg-white rounded-xl shadow-sm border-l-4 border-gray-200 p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="skeleton h-6 w-28 rounded-full" />
          <div className="skeleton h-6 w-24 rounded-full" />
        </div>
        <div className="flex gap-2 mb-4">
          <div className="skeleton h-5 w-36 rounded-md" />
        </div>
        <div className="skeleton-line mb-2" />
        <div className="skeleton-line-sm mb-4" />

        {/* Skeleton for code block */}
        <div className="skeleton h-24 w-full rounded-lg" />
      </div>
    </div>
  );
}
