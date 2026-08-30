import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useHealthTrends, useHealthCheckHistory } from '@/hooks/useHealthCheck';
import { riskApi } from '@/api/riskApi';
import { assignmentApi } from '@/api/assignmentApi';
import { RiskAssessment, AssignedDoctor } from '@/types';
import { SymptomTrendChart } from '@/components/charts/SymptomTrendChart';
import { LifestyleTrendChart } from '@/components/charts/LifestyleTrendChart';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import {
  Activity,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  RotateCcw,
  HelpCircle,
  ClipboardList,
  Eye,
  ShieldAlert,
  UserCheck,
} from 'lucide-react';

export const PatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const [timeframeDays, setTimeframeDays] = useState<number>(14);

  const { data: trendData, isLoading: isTrendsLoading } = useHealthTrends(timeframeDays);
  const { data: historyData, isLoading: isHistoryLoading } = useHealthCheckHistory(5, 0);

  // AI Risk Assessment State
  const [latestAssessment, setLatestAssessment] = useState<RiskAssessment | null>(null);
  const [isRiskLoading, setIsRiskLoading] = useState<boolean>(true);
  const [isCalculatingRisk, setIsCalculatingRisk] = useState<boolean>(false);
  const [riskError, setRiskError] = useState<string | null>(null);

  // Assigned Doctor State
  const [assignedDoc, setAssignedDoc] = useState<AssignedDoctor | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [assessment, doc] = await Promise.allSettled([
          riskApi.getLatestAssessment(),
          assignmentApi.getAssignedDoctor(),
        ]);
        if (assessment.status === 'fulfilled') setLatestAssessment(assessment.value);
        if (doc.status === 'fulfilled') setAssignedDoc(doc.value);
      } catch (err: any) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setIsRiskLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleRecalculateRisk = async () => {
    setIsCalculatingRisk(true);
    setRiskError(null);
    try {
      const newAssessment = await riskApi.calculateRisk();
      setLatestAssessment(newAssessment);
    } catch (err: any) {
      setRiskError(
        err.response?.data?.detail ||
          'Unable to compute AI risk assessment. Please ensure at least one daily health check, screening questionnaire, or eye screening has been recorded.'
      );
    } finally {
      setIsCalculatingRisk(false);
    }
  };

  const todayStr = new Date().toISOString().split('T')[0];
  const hasLoggedToday = historyData?.items?.some((item) => item.check_date === todayStr);

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Welcome Banner & Today's Status */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-teal-950/40 border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
            <Activity className="w-4 h-4" />
            <span>Patient Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Welcome back, {user?.first_name || 'Patient'}
          </h1>
          <p className="text-xs text-slate-400 max-w-xl">
            Track your daily vestibular symptoms, view multi-day recovery trends, and prepare logs for your doctor consultations.
          </p>
        </div>

        {/* Today's Check-in Card */}
        <div className="shrink-0 w-full md:w-auto p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-left space-y-3">
          <div className="flex items-center gap-2">
            {hasLoggedToday ? (
              <>
                <div className="w-7 h-7 rounded-full bg-emerald-950 border border-emerald-700 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-emerald-300">Today's Check-in Complete</p>
                  <p className="text-[10px] text-slate-400">{todayStr}</p>
                </div>
              </>
            ) : (
              <>
                <div className="w-7 h-7 rounded-full bg-amber-950 border border-amber-700 flex items-center justify-center text-amber-400">
                  <Clock className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-amber-300">Today's Check-in Pending</p>
                  <p className="text-[10px] text-slate-400">{todayStr}</p>
                </div>
              </>
            )}
          </div>

          <Link to="/patient/health-check" className="block">
            <Button
              size="sm"
              variant={hasLoggedToday ? 'outline' : 'primary'}
              className="w-full text-xs gap-1.5 justify-center"
            >
              {hasLoggedToday ? "Update Today's Entry" : "Log Today's Symptoms"}
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>
      </div>

      {/* High-Risk Non-Diagnostic Escalation Banner (Step 9 Integration) */}
      {latestAssessment?.risk_level === 'HIGH' && (
        <div className="p-5 bg-gradient-to-r from-rose-950/70 via-slate-900 to-slate-900 border border-rose-800/80 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-rose-950 border border-rose-700 flex items-center justify-center text-rose-300 shrink-0 mt-0.5">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-white">
                Clinical Support & Escalation Prompt
              </h3>
              <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                Your latest AI-assisted screening result is HIGH. This result is not a diagnosis. Consider contacting a healthcare professional for evaluation.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
            <Link to="/patient/emergency">
              <Button size="sm" variant="primary" className="text-xs gap-1.5 bg-rose-600 hover:bg-rose-500 border-none shadow-md">
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Emergency Support</span>
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* Metric Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Avg Dizziness</span>
            <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d</span>
          </div>
          <p className="text-2xl font-bold text-teal-400">
            {isTrendsLoading ? '—' : `${trendData?.average_dizziness ?? 0} / 10`}
          </p>
          <p className="text-[10px] text-slate-500">Vestibular intensity</p>
        </div>

        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Avg Imbalance</span>
            <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d</span>
          </div>
          <p className="text-2xl font-bold text-rose-400">
            {isTrendsLoading ? '—' : `${trendData?.average_imbalance ?? 0} / 10`}
          </p>
          <p className="text-[10px] text-slate-500">Postural unsteadiness</p>
        </div>

        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Avg Sleep</span>
            <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d</span>
          </div>
          <p className="text-2xl font-bold text-indigo-400">
            {isTrendsLoading ? '—' : `${trendData?.average_sleep ?? 0} hrs`}
          </p>
          <p className="text-[10px] text-slate-500">Rest duration</p>
        </div>

        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Avg Stress</span>
            <span className="text-[10px] text-slate-500 font-mono">{timeframeDays}d</span>
          </div>
          <p className="text-2xl font-bold text-amber-400">
            {isTrendsLoading ? '—' : `${trendData?.average_stress ?? 0} / 10`}
          </p>
          <p className="text-[10px] text-slate-500">Subjective tension</p>
        </div>
      </div>

      {/* AI Risk Assessment Card (Live Step 7 Integration) */}
      <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-400">
            <Sparkles className="w-4 h-4" />
            <span>AI-Assisted Screening Risk Assessment</span>
          </div>

          <Button
            size="sm"
            onClick={handleRecalculateRisk}
            isLoading={isCalculatingRisk}
            variant="outline"
            className="text-xs gap-1.5 self-start sm:self-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Recalculate AI Risk</span>
          </Button>
        </div>

        {riskError && (
          <div className="p-3.5 bg-rose-950/40 border border-rose-800/60 rounded-xl text-xs text-rose-300 flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <span>{riskError}</span>
          </div>
        )}

        {isRiskLoading ? (
          <div className="p-6 text-center">
            <LoadingSpinner size="sm" label="Loading latest risk estimate..." />
          </div>
        ) : latestAssessment ? (
          <div className="space-y-4 pt-1">
            {/* Risk Tier & Score Details */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl space-y-1">
                <span className="text-[11px] font-mono uppercase text-slate-400">Screening Risk Tier</span>
                <div>
                  <span
                    className={`inline-block px-3 py-1 rounded-lg text-sm font-extrabold tracking-wide ${
                      latestAssessment.risk_level === 'HIGH'
                        ? 'bg-rose-950 text-rose-300 border border-rose-700'
                        : latestAssessment.risk_level === 'MEDIUM'
                        ? 'bg-amber-950 text-amber-300 border border-amber-700'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    }`}
                  >
                    {latestAssessment.risk_level} RISK
                  </span>
                </div>
              </div>

              <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl space-y-1">
                <span className="text-[11px] font-mono uppercase text-slate-400">Model Risk Score</span>
                <p className="text-xl font-bold font-mono text-white">
                  {latestAssessment.risk_score.toFixed(2)}{' '}
                  <span className="text-xs text-slate-400 font-sans">/ 1.00</span>
                </p>
              </div>

              <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl space-y-1">
                <span className="text-[11px] font-mono uppercase text-slate-400">Model Version</span>
                <p className="text-xs font-mono text-teal-300 pt-1">
                  {latestAssessment.model_name} • {latestAssessment.model_version}
                </p>
              </div>
            </div>

            {/* Contributing Factors */}
            {latestAssessment.contributing_factors.length > 0 && (
              <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl space-y-2">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-teal-400" />
                  Observed Contributing Factors
                </p>
                <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                  {latestAssessment.contributing_factors.map((factor, idx) => (
                    <li key={idx}>{factor}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Disclaimer */}
            <div className="p-3 bg-teal-950/20 border border-teal-800/40 rounded-xl text-[11px] text-teal-300 flex items-start gap-2">
              <HelpCircle className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
              <span>
                VertiCare AI provides an AI-assisted screening and monitoring estimate. It is not a medical diagnosis and does not replace evaluation by a qualified healthcare professional.
              </span>
            </div>
          </div>
        ) : (
          <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-xl text-center space-y-3">
            <p className="text-xs text-slate-400">
              No AI risk assessment calculated yet. Complete your daily symptom check or screening modules to generate an AI risk score.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              <Link to="/patient/health-check">
                <Button size="sm" variant="outline" className="text-xs gap-1">
                  <Activity className="w-3.5 h-3.5 text-teal-400" />
                  <span>Log Health Check</span>
                </Button>
              </Link>
              <Link to="/patient/questionnaire">
                <Button size="sm" variant="outline" className="text-xs gap-1">
                  <ClipboardList className="w-3.5 h-3.5 text-teal-400" />
                  <span>Take Questionnaire</span>
                </Button>
              </Link>
              <Link to="/patient/eye-analysis">
                <Button size="sm" variant="outline" className="text-xs gap-1">
                  <Eye className="w-3.5 h-3.5 text-teal-400" />
                  <span>Eye Screening</span>
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Assigned Clinician Card (Issue 2 Integration) */}
      <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-950/80 border border-teal-700 flex items-center justify-center text-teal-400 shrink-0">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">Assigned Clinician:</span>
              {assignedDoc?.has_assigned_doctor ? (
                <span className="text-xs font-bold text-teal-300">{assignedDoc.doctor_name}</span>
              ) : (
                <span className="text-xs text-slate-400 font-medium">None assigned</span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              {assignedDoc?.has_assigned_doctor
                ? `${assignedDoc.specialization} • Connected for continuous clinical monitoring`
                : 'Connect with your doctor to share your daily logs and screening results.'}
            </p>
          </div>
        </div>

        <Link to="/patient/assigned-doctor" className="shrink-0 self-end sm:self-center">
          <Button size="sm" variant="outline" className="text-xs gap-1.5">
            <span>{assignedDoc?.has_assigned_doctor ? 'View Assigned Doctor' : '+ Add Doctor'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </div>

      {/* Longitudinal Trend Charts */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">Longitudinal Health Trends</h2>
            <p className="text-xs text-slate-400">Symptom evolution based strictly on recorded daily health checks.</p>
          </div>

          {/* Timeframe selector (7 Days / 30 Days) */}
          <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800 self-start">
            <button
              onClick={() => setTimeframeDays(7)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
                timeframeDays === 7 ? 'bg-teal-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              7 Days
            </button>
            <button
              onClick={() => setTimeframeDays(30)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
                timeframeDays === 30 ? 'bg-teal-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              30 Days
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: Dizziness & Imbalance */}
          <div className="p-5 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2 shadow-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                Symptom Severity (0–10)
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">
                {trendData?.total_records ?? 0} data points
              </span>
            </div>
            <SymptomTrendChart
              dataPoints={trendData?.data_points || []}
              isLoading={isTrendsLoading}
            />
          </div>

          {/* Chart 2: Sleep & Stress */}
          <div className="p-5 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2 shadow-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                Sleep & Stress Metrics
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">
                {trendData?.total_records ?? 0} data points
              </span>
            </div>
            <LifestyleTrendChart
              dataPoints={trendData?.data_points || []}
              isLoading={isTrendsLoading}
            />
          </div>
        </div>
      </div>

      {/* Recent Activity Log */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white tracking-tight">Recent Daily Logs</h2>
          <Link
            to="/patient/health-check"
            className="text-xs font-medium text-teal-400 hover:text-teal-300 flex items-center gap-1"
          >
            Open Health Check & History <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isHistoryLoading ? (
          <div className="p-6 text-center bg-slate-950/40 rounded-xl border border-slate-800">
            <LoadingSpinner size="sm" label="Loading recent entries..." />
          </div>
        ) : !historyData || historyData.items.length === 0 ? (
          <div className="p-6 bg-slate-950/40 rounded-xl border border-slate-800 text-center text-xs text-slate-500">
            No daily health checks recorded yet. Use the button above to log your symptoms today.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {historyData.items.slice(0, 3).map((item) => (
              <div
                key={item.id}
                className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2 shadow-sm"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white">{item.check_date}</span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      item.dizziness_severity > 6
                        ? 'bg-rose-950 text-rose-400'
                        : item.dizziness_severity > 3
                        ? 'bg-amber-950 text-amber-400'
                        : 'bg-emerald-950 text-emerald-400'
                    }`}
                  >
                    Dizziness: {item.dizziness_severity}/10
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 space-y-0.5">
                  <p>Imbalance: <strong className="text-slate-200">{item.imbalance_severity}/10</strong></p>
                  <p>Duration: <span className="text-slate-300">{item.episode_duration}</span></p>
                  <p>Sleep: <span className="text-slate-300">{item.sleep_hours}h</span> • Stress: <span className="text-slate-300">{item.stress_level}/10</span></p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
