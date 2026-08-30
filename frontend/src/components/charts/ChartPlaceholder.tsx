import React from 'react';
import { BarChart3 } from 'lucide-react';

interface ChartPlaceholderProps {
  title?: string;
  height?: number;
}

export const ChartPlaceholder: React.FC<ChartPlaceholderProps> = ({
  title = 'Longitudinal Visualization',
  height = 200,
}) => {
  return (
    <div
      style={{ height }}
      className="border border-slate-800 rounded-xl bg-slate-950/40 p-4 flex flex-col items-center justify-center text-slate-500 gap-2"
    >
      <BarChart3 className="w-8 h-8 opacity-40 text-teal-400" />
      <span className="text-xs font-medium text-slate-400">{title}</span>
      <span className="text-[11px] text-slate-600">Recharts container configured for upcoming steps</span>
    </div>
  );
};

