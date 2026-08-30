import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { doctorApi } from '@/api/doctorApi';
import { DoctorDashboardSummary } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import {
  Users,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  Shield,
  Activity,
  ClipboardList,
  Eye,
} from 'lucide-react';

export const DoctorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DoctorDashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await doctorApi.getDashboardSummary();
        setSummary(data);
      } catch (err: any) {
        let msg = 'Failed to load clinician dashboard.';
        if (err.response?.data?.detail) {
          const detail = err.response.data.detail;
          if (typeof detail === 'string') msg = detail;
          else if (Array.isArray(detail)) msg = detail.map((d: any) => d.msg).join(', ');
        } else if (err.message) {
          msg = err.message;
        }
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading clinician dashboard metrics..." />
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="p-6 bg-rose-950/30 border border-rose-800/50 rounded-xl text-xs text-rose-300">
        {error || 'Unable to load dashboard data.'}
      </div>
    );
  }

  const dist = summary.risk_distribution;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Clinician Welcome Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-teal-950/40 border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
            <Shield className="w-4 h-4" />
            <span>Clinician Decision Support Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Dr. {user?.first_name} {user?.last_name}
          </h1>
          <p className="text-xs text-slate-400 max-w-xl">
            Monitor assigned patient vestibular health trends, review multimodal screening assessments, and record clinical decision notes.
          </p>
        </div>

        <Link to="/doctor/patients">
          <Button size="sm" variant="primary" className="text-xs gap-1.5 shrink-0">
            <Users className="w-3.5 h-3.5" />
            <span>View All Assigned Patients</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </div>

      {/* Summary KPI Cards (Strictly Real Counts) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Assigned */}
        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Assigned Cohort</span>
            <Users className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold font-mono text-white">
            {summary.total_assigned_patients}
          </p>
          <p className="text-[10px] text-slate-500">Active assigned patients</p>
        </div>

        {/* High Risk Tier */}
        <div className="p-5 bg-slate-950/80 border border-rose-900/40 rounded-2xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-rose-400 text-xs">
            <span>High Risk Priority</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold font-mono text-rose-400">
            {dist.HIGH}
          </p>
          <p className="text-[10px] text-slate-500">Screening score $\ge 0.70$</p>
        </div>

        {/* Medium Risk Tier */}
        <div className="p-5 bg-slate-950/80 border border-amber-900/40 rounded-2xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-amber-400 text-xs">
            <span>Medium Risk</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold font-mono text-amber-400">
            {dist.MEDIUM}
          </p>
          <p className="text-[10px] text-slate-500">Screening score 0.35–0.69</p>
        </div>

        {/* Low Risk Tier */}
        <div className="p-5 bg-slate-950/80 border border-emerald-900/40 rounded-2xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-emerald-400 text-xs">
            <span>Low Risk / Stable</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold font-mono text-emerald-400">
            {dist.LOW}
          </p>
          <p className="text-[10px] text-slate-500">Screening score $\le 0.34$</p>
        </div>
      </div>

      {/* Recent Assigned Patient Activity Feed */}
      <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-400">
            <Activity className="w-4 h-4" />
            <span>Recent Assigned Patient Activity</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">
            {summary.recent_activity.length} recent events
          </span>
        </div>

        {summary.total_assigned_patients === 0 ? (
          <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-xl space-y-2">
            <Users className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">No patients assigned yet.</p>
            <p className="text-xs text-slate-500">
              When patients are assigned to your clinician account, their monitoring activity and screening assessments will appear here.
            </p>
          </div>
        ) : summary.recent_activity.length === 0 ? (
          <div className="p-6 text-center bg-slate-900/40 border border-slate-800 rounded-xl text-xs text-slate-500">
            No recent activity recorded by your assigned patients yet.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {summary.recent_activity.map((act, idx) => (
              <div key={idx} className="py-3.5 flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 mt-0.5">
                    {act.activity_type === 'HEALTH_CHECK' ? (
                      <Activity className="w-4 h-4 text-teal-400" />
                    ) : act.activity_type === 'QUESTIONNAIRE' ? (
                      <ClipboardList className="w-4 h-4 text-indigo-400" />
                    ) : act.activity_type === 'EYE_ANALYSIS' ? (
                      <Eye className="w-4 h-4 text-cyan-400" />
                    ) : (
                      <Sparkles className="w-4 h-4 text-amber-400" />
                    )}
                  </div>
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <Link
                        to={`/doctor/patients/${act.patient_id}`}
                        className="text-xs font-bold text-white hover:text-teal-400 transition"
                      >
                        {act.patient_name}
                      </Link>
                      {act.risk_level && (
                        <span
                          className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                            act.risk_level === 'HIGH'
                              ? 'bg-rose-950 text-rose-300 border border-rose-800'
                              : act.risk_level === 'MEDIUM'
                              ? 'bg-amber-950 text-amber-300 border border-amber-800'
                              : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          }`}
                        >
                          {act.risk_level} RISK
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300">{act.description}</p>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-[10px] text-slate-500 font-mono">
                    {new Date(act.timestamp).toLocaleDateString()} {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

