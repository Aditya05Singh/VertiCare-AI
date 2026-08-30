import React from 'react';
import { Activity, Server, Layers, Cpu, ShieldCheck } from 'lucide-react';
import { useHealth } from '@/hooks/useHealth';
import { Button } from '@/components/ui/button';
import { ChartPlaceholder } from '@/components/charts/ChartPlaceholder';

export const OverviewPage: React.FC = () => {
  const { data: health, isLoading, refetch } = useHealth();

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          VertiCare AI — System Foundation
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Academic healthcare software platform for vertigo screening, continuous monitoring, and clinician decision support.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Backend Status</span>
            <Server className="w-4 h-4 text-teal-400" />
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                isLoading
                  ? 'bg-amber-400'
                  : health?.status === 'ok'
                  ? 'bg-emerald-400'
                  : 'bg-rose-400'
              }`}
            />
            <span className="text-base font-semibold text-white">
              {isLoading ? 'Checking...' : health?.status === 'ok' ? 'Online' : 'Offline'}
            </span>
          </div>
          <p className="text-[11px] text-slate-500">Service: {health?.service || 'verticare-backend'}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Database Engine</span>
            <Layers className="w-4 h-4 text-cyan-400" />
          </div>
          <span className="text-base font-semibold text-white block">PostgreSQL 16</span>
          <p className="text-[11px] text-slate-500">SQLAlchemy 2.0 + Alembic configured</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Client Stack</span>
            <Activity className="w-4 h-4 text-indigo-400" />
          </div>
          <span className="text-base font-semibold text-white block">React + TS + Vite</span>
          <p className="text-[11px] text-slate-500">Tailwind CSS + TanStack Query</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Medical Safety</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <span className="text-base font-semibold text-white block">Active Disclaimers</span>
          <p className="text-[11px] text-slate-500">Non-diagnostic decision support</p>
        </div>
      </div>

      <div className="p-6 rounded-xl bg-slate-950/40 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-white">System Connectivity & Health Check</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Verifies FastAPI REST API communication via TanStack Query.
            </p>
          </div>
          <Button size="sm" variant="outline" onClick={() => refetch()} isLoading={isLoading}>
            Refresh Status
          </Button>
        </div>

        <div className="p-3 bg-slate-900 rounded-lg border border-slate-800/80 font-mono text-xs text-slate-300">
          <div className="flex items-center justify-between text-slate-500 text-[11px] mb-1">
            <span>GET /health response payload:</span>
            <span>HTTP 200 OK</span>
          </div>
          <pre>{JSON.stringify(health || { status: 'offline', service: 'verticare-backend' }, null, 2)}</pre>
        </div>
      </div>

      <ChartPlaceholder title="Longitudinal Analytics Engine (Preview Placeholder)" height={180} />
    </div>
  );
};

