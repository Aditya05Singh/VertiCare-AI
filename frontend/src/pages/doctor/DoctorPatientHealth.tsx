import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { doctorApi } from '@/api/doctorApi';
import { DailyHealthCheck, DailyHealthTrendResponse } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { SymptomTrendChart } from '@/components/charts/SymptomTrendChart';
import { LifestyleTrendChart } from '@/components/charts/LifestyleTrendChart';
import { Activity, Calendar, AlertCircle } from 'lucide-react';

export const DoctorPatientHealth: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [trends, setTrends] = useState<DailyHealthTrendResponse | null>(null);
  const [history, setHistory] = useState<DailyHealthCheck[]>([]);
  const [timeframeDays, setTimeframeDays] = useState<number>(14);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function loadHealthData() {
      setIsLoading(true);
      setError(null);
      try {
        const [trendRes, histRes] = await Promise.all([
          doctorApi.getPatientHealthTrends(id!, timeframeDays),
          doctorApi.getPatientHealthHistory(id!, 30, 0),
        ]);
        setTrends(trendRes);
        setHistory(histRes.items);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load patient health check records.');
      } finally {
        setIsLoading(false);
      }
    }
    loadHealthData();
  }, [id, timeframeDays]);

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading health check history and trend charts..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-950/30 border border-rose-800/50 rounded-xl text-xs text-rose-300">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Timeframe selector header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight">Longitudinal Symptom Tracking</h2>
          <p className="text-xs text-slate-400">
            Symptom evolution based strictly on patient-submitted daily health check records.
          </p>
        </div>

        <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800 self-start">
          {[7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setTimeframeDays(d)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
                timeframeDays === d
                  ? 'bg-teal-600 text-white shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {/* Average Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Avg Dizziness</span>
          <p className="text-2xl font-bold text-teal-400">{trends?.average_dizziness ?? 0} / 10</p>
          <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d window</span>
        </div>

        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Avg Imbalance</span>
          <p className="text-2xl font-bold text-rose-400">{trends?.average_imbalance ?? 0} / 10</p>
          <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d window</span>
        </div>

        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Avg Sleep</span>
          <p className="text-2xl font-bold text-indigo-400">{trends?.average_sleep ?? 0} hrs</p>
          <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d window</span>
        </div>

        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1">
          <span className="text-xs text-slate-400">Avg Stress</span>
          <p className="text-2xl font-bold text-amber-400">{trends?.average_stress ?? 0} / 10</p>
          <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d window</span>
        </div>
      </div>

      {/* Trend Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-2 shadow-lg">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Dizziness & Imbalance Severity (0–10)
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">
              {trends?.total_records ?? 0} data points
            </span>
          </div>
          <SymptomTrendChart dataPoints={trends?.data_points || []} isLoading={isLoading} />
        </div>

        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-2 shadow-lg">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Sleep Duration & Stress Levels
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">
              {trends?.total_records ?? 0} data points
            </span>
          </div>
          <LifestyleTrendChart dataPoints={trends?.data_points || []} isLoading={isLoading} />
        </div>
      </div>

      {/* Health Check History Table */}
      <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-400">
            <Activity className="w-4 h-4" />
            <span>Health Check Log Entries</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">
            {history.length} records available
          </span>
        </div>

        {history.length === 0 ? (
          <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-xl text-xs text-slate-500">
            No daily health checks recorded yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3">Dizziness</th>
                  <th className="py-2.5 px-3">Imbalance</th>
                  <th className="py-2.5 px-3">Duration</th>
                  <th className="py-2.5 px-3">Sleep</th>
                  <th className="py-2.5 px-3">Stress</th>
                  <th className="py-2.5 px-3">Symptoms</th>
                  <th className="py-2.5 px-3">Triggers</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-2.5 px-3 font-mono font-semibold text-white">{h.check_date}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          h.dizziness_severity > 6
                            ? 'bg-rose-950 text-rose-300'
                            : h.dizziness_severity > 3
                            ? 'bg-amber-950 text-amber-300'
                            : 'bg-emerald-950 text-emerald-300'
                        }`}
                      >
                        {h.dizziness_severity}/10
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-rose-300">{h.imbalance_severity}/10</td>
                    <td className="py-2.5 px-3 text-slate-400 capitalize">{h.episode_duration}</td>
                    <td className="py-2.5 px-3">{h.sleep_hours}h</td>
                    <td className="py-2.5 px-3 text-amber-300">{h.stress_level}/10</td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-400">
                      {[h.nausea && 'Nausea', h.headache && 'Headache'].filter(Boolean).join(', ') || 'None'}
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-400">
                      {h.triggers?.length ? h.triggers.join(', ') : 'None'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

