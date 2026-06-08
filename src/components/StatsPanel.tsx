interface StatsPanelProps {
  count: number
  onClear: () => void
}

export default function StatsPanel({ count, onClear }: StatsPanelProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="bg-white/10 rounded-lg px-4 py-2">
        <span className="text-white/60 text-sm">Documents</span>
        <span className="ml-2 text-white font-semibold">{count}</span>
      </div>
      {count > 0 && (
        <button
          onClick={onClear}
          className="px-3 py-2 text-sm text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
        >
          Clear All
        </button>
      )}
    </div>
  )
}
