import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { doctorApi } from '@/api/doctorApi';
import { RiskAssessment } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Sparkles, ShieldCheck, HelpCircle } from 'lucide-react';

export const DoctorPatientRisk: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [assessments, setAssessments] = useState<RiskAssessment[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function loadRiskHistory() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await doctorApi.getPatientRiskHistory(id!, 30, 0);
        setAssessments(data.items);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load patient risk assessment history.');
      } finally {
        setIsLoading(false);
      }
    }
    loadRiskHistory();
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading AI risk assessment history..." />
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
          <h2 className="text-base font-bold text-white tracking-tight">AI Screening Risk History</h2>
          <p className="text-xs text-slate-400">
            Multimodal AI risk classification trajectory generated across patient monitoring sessions.
          </p>
        </div>
        <span className="text-xs text-slate-500 font-mono">
          {assessments.length} assessments on record
        </span>
      </div>

      {assessments.length === 0 ? (
        <div className="p-8 text-center bg-slate-950/60 border border-slate-800 rounded-2xl text-xs text-slate-500">
          No AI risk assessments available for this patient.
        </div>
      ) : (
        <div className="space-y-6">
          {assessments.map((item, idx) => (
            <div
              key={item.id}
              className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl"
            >
              {/* Header & Badges */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800/80 gap-3">
                <div className="flex items-center gap-3">
                  <span
                    className={`px-3 py-1 rounded-lg text-xs font-extrabold tracking-wide uppercase ${
                      item.risk_level === 'HIGH'
                        ? 'bg-rose-950 text-rose-300 border border-rose-700'
                        : item.risk_level === 'MEDIUM'
                        ? 'bg-amber-950 text-amber-300 border border-amber-700'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    }`}
                  >
                    {item.risk_level} RISK
                  </span>
                  <div>
                    <span className="text-xs font-bold text-white">
                      Score: <strong className="font-mono text-teal-300">{item.risk_score.toFixed(2)}</strong> / 1.00
                    </span>
                    <p className="text-[11px] text-slate-400">
                      Evaluated: {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="text-right text-[11px] font-mono text-slate-400">
                  <span className="bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                    Model: {item.model_name} ({item.model_version})
                  </span>
                </div>
              </div>

              {/* Contributing Factors */}
              {item.contributing_factors && item.contributing_factors.length > 0 && (
                <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-teal-400" />
                    Observed Contributing Factors
                  </p>
                  <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                    {item.contributing_factors.map((factor, fIdx) => (
                      <li key={fIdx}>{factor}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Safety Notice */}
              <div className="p-3 bg-teal-950/20 border border-teal-800/40 rounded-xl text-[11px] text-teal-300 flex items-start gap-2">
                <HelpCircle className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
                <span>{item.notice || 'AI-assisted screening estimate for clinical decision support. Not a medical diagnosis.'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

