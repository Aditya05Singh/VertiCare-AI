import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { doctorApi } from '@/api/doctorApi';
import { EyeAnalysisSession } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import {
  Eye,
  HelpCircle,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Activity,
  ShieldAlert,
  Info,
} from 'lucide-react';

export const DoctorPatientEyeAnalysis: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [sessions, setSessions] = useState<EyeAnalysisSession[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function loadEyeSessions() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await doctorApi.getPatientEyeAnalyses(id!);
        setSessions(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load eye-movement screening history.');
      } finally {
        setIsLoading(false);
      }
    }
    loadEyeSessions();
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading eye-movement screening sessions..." />
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight">Eye-Movement Screening History</h2>
          <p className="text-xs text-slate-400">
            Webcam-based ocular kinematics and evidence-based AI screening interpretation.
          </p>
        </div>
        <span className="text-xs text-slate-500 font-mono">
          {sessions.length} recorded sessions
        </span>
      </div>

      {sessions.length === 0 ? (
        <div className="p-8 text-center bg-slate-950/60 border border-slate-800 rounded-2xl text-xs text-slate-500">
          No eye-movement screening sessions recorded for this patient.
        </div>
      ) : (
        <div className="space-y-6">
          {sessions.map((sess, idx) => {
            const featuresList = Array.isArray(sess.features)
              ? sess.features.map((f: any) => ({ name: f.feature_name, value: f.feature_value }))
              : Object.entries(sess.features || {}).map(([name, value]: [string, any]) => ({
                  name,
                  value: Number(value),
                }));

            const screening = sess.screening;

            return (
              <div
                key={sess.id}
                className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-5 shadow-xl"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-teal-950 border border-teal-800 flex items-center justify-center text-teal-400">
                      <Eye className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">
                        Screening Session #{sessions.length - idx}
                      </h3>
                      <p className="text-[11px] text-slate-400">
                        Recorded: {new Date(sess.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase bg-teal-950 text-teal-300 border border-teal-800">
                      {sess.analysis_status}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                      Quality: {(sess.quality_summary.valid_ratio * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* AI Screening Interpretation Card (Evidence-Based) */}
                {screening && screening.status === 'AVAILABLE' ? (
                  <div className="p-5 bg-gradient-to-br from-slate-900 via-slate-900/90 to-teal-950/40 border border-teal-800/80 rounded-xl space-y-3 shadow-lg">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-teal-400" />
                        <span className="text-xs font-bold uppercase tracking-wider text-teal-300">
                          AI Screening Interpretation
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
                        <span>{screening.model_name}</span>
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-teal-300">v{screening.model_version}</span>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-baseline gap-3">
                      <h4 className="text-base font-extrabold text-white tracking-tight">
                        {screening.label.replace(/_/g, ' ')}
                      </h4>
                      {screening.confidence !== null && screening.confidence !== undefined && (
                        <span className="px-2 py-0.5 rounded bg-teal-950 border border-teal-700 text-teal-300 text-xs font-mono font-bold">
                          Model Probability: {(screening.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      {screening.explanation}
                    </p>

                    {screening.contributing_factors && screening.contributing_factors.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider block">
                          Key Contributing Kinematic Factors:
                        </span>
                        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs text-slate-300">
                          {screening.contributing_factors.map((factor, fIdx) => (
                            <li key={fIdx} className="flex items-center gap-1.5">
                              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 shrink-0" />
                              <span>{factor}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : screening && screening.status === 'UNAVAILABLE' ? (
                  <div className="p-4 bg-amber-950/30 border border-amber-800/60 rounded-xl text-xs text-amber-300 space-y-1">
                    <div className="flex items-center gap-2 font-bold text-amber-200">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      <span>AI Screening Interpretation Unavailable</span>
                    </div>
                    <p>{screening.explanation || 'Image or tracking quality was insufficient to produce an AI screening observation.'}</p>
                  </div>
                ) : null}

                {/* Technical Quality Metrics */}
                <div className="space-y-2">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Technical Tracking Quality
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
                      <span className="text-slate-500 block text-[10px]">Valid Ratio</span>
                      <strong className="text-teal-300">
                        {(sess.quality_summary.valid_ratio * 100).toFixed(1)}%
                      </strong>
                    </div>
                    <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
                      <span className="text-slate-500 block text-[10px]">Face Detected</span>
                      <strong className="text-white">
                        {(sess.quality_summary.face_detected_ratio * 100).toFixed(1)}%
                      </strong>
                    </div>
                    <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
                      <span className="text-slate-500 block text-[10px]">Valid Frames</span>
                      <strong className="text-white">
                        {sess.quality_summary.valid_frames} / {sess.quality_summary.total_frames}
                      </strong>
                    </div>
                    <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
                      <span className="text-slate-500 block text-[10px]">Quality Sufficiency</span>
                      <strong className={sess.quality_summary.is_sufficient ? 'text-emerald-400' : 'text-rose-400'}>
                        {sess.quality_summary.is_sufficient ? 'Sufficient' : 'Insufficient'}
                      </strong>
                    </div>
                  </div>
                </div>

                {/* Extracted Kinematic Features */}
                <div className="space-y-2">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Observed Eye-Movement Features
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {featuresList.map((f) => (
                      <div
                        key={f.name}
                        className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-0.5"
                      >
                        <span className="text-[10px] text-slate-400 font-mono uppercase block truncate">
                          {f.name.replace(/_/g, ' ')}
                        </span>
                        <strong className="text-white font-mono text-sm">
                          {typeof f.value === 'number' ? f.value.toFixed(3) : String(f.value)}
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Non-diagnostic notice & Domain Shift Alert */}
                <div className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl text-[11px] text-slate-400 space-y-1.5">
                  <div className="flex items-start gap-2">
                    <Info className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
                    <span>
                      <strong>AI Screening Notice:</strong> This output represents an AI-assisted screening observation and does not constitute a confirmed neurological diagnosis. Clinical interpretation must be performed by a qualified physician.
                    </span>
                  </div>
                  <div className="flex items-start gap-2 text-slate-500">
                    <ShieldAlert className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                    <span>
                      <strong>Webcam Domain Shift:</strong> Ocular movements captured using consumer RGB webcams under room lighting do not replace infrared video-oculography (VNG/VOG) in darkness.
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
