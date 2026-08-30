import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { DailyHealthTrendPoint } from '@/types';
import { Activity } from 'lucide-react';

interface SymptomTrendChartProps {
  dataPoints: DailyHealthTrendPoint[];
  isLoading?: boolean;
}

export const SymptomTrendChart: React.FC<SymptomTrendChartProps> = ({
  dataPoints,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center bg-slate-900/40 rounded-xl border border-slate-800 animate-pulse">
        <p className="text-xs text-slate-500">Loading symptom trends...</p>
      </div>
    );
  }

  if (!dataPoints || dataPoints.length === 0) {
    return (
      <div className="h-64 flex flex-col items-center justify-center bg-slate-900/30 rounded-xl border border-slate-800 p-6 text-center">
        <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-500 mb-2">
          <Activity className="w-5 h-5" />
        </div>
        <p className="text-sm font-medium text-slate-300">Not enough symptom data yet</p>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          Complete your daily health checks to visualize your dizziness and imbalance severity trends over time.
        </p>
      </div>
    );
  }

  const formattedData = dataPoints.map((pt) => ({
    ...pt,
    shortDate: pt.date.slice(5), // MM-DD
  }));

  return (
    <div className="h-72 w-full pt-2">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formattedData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
          <XAxis
            dataKey="shortDate"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#475569' }}
          />
          <YAxis
            domain={[0, 10]}
            ticks={[0, 2, 4, 6, 8, 10]}
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#475569' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '0.5rem',
              color: '#f8fafc',
              fontSize: '12px',
            }}
          />
          <Legend
            verticalAlign="top"
            align="right"
            height={32}
            wrapperStyle={{ fontSize: '11px', color: '#cbd5e1' }}
          />
          <Line
            type="monotone"
            dataKey="dizziness_severity"
            name="Dizziness Severity (0-10)"
            stroke="#14b8a6"
            strokeWidth={2.5}
            dot={{ fill: '#14b8a6', r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="imbalance_severity"
            name="Imbalance Severity (0-10)"
            stroke="#f43f5e"
            strokeWidth={2.5}
            dot={{ fill: '#f43f5e', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

