import React from 'react';
import { useOutletContext, Link, useParams } from 'react-router-dom';
import { DoctorPatientDossier } from '@/types';
import { Button } from '@/components/ui/button';
import {
  Activity,
  ClipboardList,
  Eye,
  Sparkles,
  FileEdit,
  ArrowRight,
  ShieldCheck,
  Phone,
  Calendar,
  AlertCircle,
} from 'lucide-react';

interface ContextType {
  dossier: DoctorPatientDossier;
}

export const DoctorPatientOverview: React.FC = () => {
  const { dossier } = useOutletContext<ContextType>();
  const { id } = useParams<{ id: string }>();

  const latestHc = dossier.latest_health_check;
  const latestQ = dossier.latest_questionnaire;
  const latestEye = dossier.latest_eye_analysis;
  const latestRisk = dossier.latest_risk_assessment;

  return (
    <div className="space-y-6">
      {/* Patient Profile Quick Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-2 shadow-sm">
          <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400">
            Demographic Profile
          </span>
          <div className="text-xs text-slate-300 space-y-1">
            <p>Date of Birth: <strong className="text-white">{dossier.date_of_birth}</strong></p>
            <p>Gender: <strong className="text-white">{dossier.gender}</strong></p>
            <p>Email: <strong className="text-white">{dossier.email}</strong></p>
          </div>
        </div>

        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-2 shadow-sm">
          <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400">
            Emergency Contacts
          </span>
          <div className="text-xs text-slate-300 space-y-1">
            <p>Name: <strong className="text-white">{dossier.emergency_contact_name || 'Not provided'}</strong></p>
            <p>Phone: <strong className="text-white">{dossier.emergency_contact_phone || 'Not provided'}</strong></p>
          </div>
        </div>

        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-2 shadow-sm">
          <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400">
            Clinical Records Status
          </span>
          <div className="text-xs text-slate-300 space-y-1">
            <p>Clinical Notes: <strong className="text-teal-400">{dossier.recent_notes_count} authored</strong></p>
            <p>
              AI Risk Estimate:{' '}
              <strong className={latestRisk ? 'text-teal-400' : 'text-slate-500'}>
                {latestRisk ? `${latestRisk.risk_level} (${latestRisk.risk_score.toFixed(2)})` : 'Not computed'}
              </strong>
            </p>
          </div>
        </div>
      </div>

      {/* Multimodal Monitoring Quick Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Modality 1: Latest Daily Health Check */}
        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3 shadow-lg flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-400">
                <Activity className="w-4 h-4" />
                <span>Daily Health Monitoring</span>
              </div>
              {latestHc && (
                <span className="text-[10px] text-slate-500 font-mono">{latestHc.check_date}</span>
              )}
            </div>

            {latestHc ? (
              <div className="grid grid-cols-2 gap-2 p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-300">
                <p>Dizziness: <strong className="text-teal-300">{latestHc.dizziness_severity} / 10</strong></p>
                <p>Imbalance: <strong className="text-rose-300">{latestHc.imbalance_severity} / 10</strong></p>
                <p>Sleep: <strong className="text-white">{latestHc.sleep_hours} hrs</strong></p>
                <p>Stress: <strong className="text-amber-300">{latestHc.stress_level} / 10</strong></p>
                <p className="col-span-2 text-[11px] text-slate-400">
                  Duration: {latestHc.episode_duration} • Nausea: {latestHc.nausea ? 'Yes' : 'No'}
                </p>
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-3">No daily health checks logged yet.</p>
            )}
          </div>

          <Link to={`/doctor/patients/${id}/health`}>
            <Button size="sm" variant="outline" className="w-full text-xs gap-1.5 justify-center">
              <span>View Health Check History & Trends</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>

        {/* Modality 2: Questionnaire Screening */}
        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3 shadow-lg flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-400">
                <ClipboardList className="w-4 h-4" />
                <span>Adaptive Questionnaire</span>
              </div>
              {latestQ?.completed_at && (
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(latestQ.completed_at).toLocaleDateString()}
                </span>
              )}
            </div>

            {latestQ ? (
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-300 space-y-1">
                <p>Status: <strong className="text-emerald-400">Completed</strong></p>
                <p>Questions Answered: <strong className="text-white">{latestQ.total_questions_answered}</strong></p>
                <p className="text-[11px] text-slate-400 truncate">
                  Latest completed screening traversal available for clinician review.
                </p>
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-3">No completed questionnaires yet.</p>
            )}
          </div>

          <Link to={`/doctor/patients/${id}/questionnaire`}>
            <Button size="sm" variant="outline" className="w-full text-xs gap-1.5 justify-center">
              <span>View Completed Questionnaire</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>

        {/* Modality 3: Eye Movement Screening */}
        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3 shadow-lg flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400">
                <Eye className="w-4 h-4" />
                <span>Eye Movement Screening (CV)</span>
              </div>
              {latestEye && (
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(latestEye.created_at).toLocaleDateString()}
                </span>
              )}
            </div>

            {latestEye ? (
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-300 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Pattern:</span>
                  <strong className="text-teal-300 font-semibold">
                    {latestEye.screening?.label ? latestEye.screening.label.replace(/_/g, ' ') : 'Features Recorded'}
                  </strong>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Tracking Quality:</span>
                  <strong className="text-cyan-300 font-mono">
                    {(latestEye.quality_summary.valid_ratio * 100).toFixed(0)}% valid
                  </strong>
                </div>
                <p className="text-[11px] text-slate-400">
                  {Array.isArray(latestEye.features) ? latestEye.features.length : Object.keys(latestEye.features || {}).length} kinematic features recorded.
                </p>
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-3">No eye-movement sessions recorded yet.</p>
            )}
          </div>

          <Link to={`/doctor/patients/${id}/eye-analysis`}>
            <Button size="sm" variant="outline" className="w-full text-xs gap-1.5 justify-center">
              <span>View Eye Kinematics & Tracking</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>

        {/* Modality 4: AI Risk Assessment */}
        <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3 shadow-lg flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-400">
                <Sparkles className="w-4 h-4" />
                <span>AI Screening Risk Assessment</span>
              </div>
              {latestRisk && (
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(latestRisk.created_at).toLocaleDateString()}
                </span>
              )}
            </div>

            {latestRisk ? (
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-300 space-y-1">
                <div className="flex items-center justify-between">
                  <span>Risk Category:</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      latestRisk.risk_level === 'HIGH'
                        ? 'bg-rose-950 text-rose-300 border border-rose-700'
                        : latestRisk.risk_level === 'MEDIUM'
                        ? 'bg-amber-950 text-amber-300 border border-amber-700'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    }`}
                  >
                    {latestRisk.risk_level}
                  </span>
                </div>
                <p>Model Score: <strong className="text-white font-mono">{latestRisk.risk_score.toFixed(2)} / 1.00</strong></p>
                <p className="text-[10px] text-slate-500 font-mono">
                  Model: {latestRisk.model_name} • {latestRisk.model_version}
                </p>
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-3">No AI risk assessment calculated yet.</p>
            )}
          </div>

          <Link to={`/doctor/patients/${id}/risk`}>
            <Button size="sm" variant="outline" className="w-full text-xs gap-1.5 justify-center">
              <span>View Risk History & Contributing Factors</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
