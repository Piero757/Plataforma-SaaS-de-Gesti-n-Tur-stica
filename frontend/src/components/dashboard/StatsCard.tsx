export function StatsCard({ title, value, change, icon, changeType }: any) {
  const isPositive = change >= 0;
  
  return (
    <div className="stat-card flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <h3 className="text-2xl font-bold text-gray-900 mt-1">{value}</h3>
        </div>
        <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center text-xl">
          {icon}
        </div>
      </div>
      
      {change !== undefined && (
        <div className="flex items-center gap-2 text-sm">
          <span className={`font-medium ${
            changeType === 'neutral' ? 'text-gray-600' :
            (isPositive ? 'text-green-600' : 'text-red-600')
          }`}>
            {isPositive ? '↑' : '↓'} {Math.abs(change)}%
          </span>
          <span className="text-gray-400">vs mes anterior</span>
        </div>
      )}
    </div>
  );
}
