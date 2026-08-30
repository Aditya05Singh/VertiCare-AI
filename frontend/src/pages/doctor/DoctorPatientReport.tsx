import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { doctorApi } from '@/api/doctorApi';
import { DoctorPatientReport as ReportType } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import {
  FileText,
  Printer,
  ShieldCheck,
  Activity,
  ClipboardList,
  Eye,
  Sparkles,
  HelpCircle,
} from 'lucide-react';

export const DoctorPatientReport: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<ReportType | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function loadReport() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await doctorApi.getPatientReport(id!);
        setReport(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to compile clinical report summary.');
      } finally {
        setIsLoading(false);
      }
    }
    loadReport();
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Compiling multimodal clinical report summary..." />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="p-6 bg-rose-950/30 border border-rose-800/50 rounded-xl text-xs text-rose-300">
        {error || 'Unable to load report.'}
      </div>
    );
  }

  const hs = report.health_summary;
  const qSummary = report.questionnaire_summary;
  const eyeSummary = report.eye_analysis_summary;
  const latestRisk = report.latest_risk;

  return (
    <div className="space-y-6">
      {/* Header & Print Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight">Clinical Monitoring & Screening Report</h2>
          <p className="text-xs text-slate-400">
            Consolidated overview generated on {new Date(report.generated_at).toLocaleString()}.
          </p>
        </div>

        <Button
          size="sm"
          variant="outline"
          onClick={() => window.print()}
          className="text-xs gap-1.5 self-start sm:self-auto"
        >
          <Printer className="w-3.5 h-3.5" />
          <span>Print / Export Summary</span>
        </Button>
      </div>

      {/* Structured Report Container */}
      <div className="p-8 bg-slate-950/90 border border-slate-800 rounded-2xl space-y-8 shadow-2xl">
        {/* Report Header Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-400 mb-1">
              <ShieldCheck className="w-4 h-4" />
              <span>VertiCare AI • Clinician Decision Support Summary</span>
            </div>
            <h1 className="text-xl font-extrabold text-white">{report.patient_name}</h1>
            <p className="text-xs text-slate-400">Patient Identifier: {report.patient_id}</p>
          </div>

          <div className="text-right text-xs text-slate-400 space-y-0.5">
            <p>Generated: {new Date(report.generated_at).toLocaleDateString()}</p>
            <p className="text-[10px] text-slate-500 font-mono">Report ID: RPT-{report.patient_id.slice(0, 8)}</p>
          </div>
        </div>

        {/* Section 1: 14-Day Health Tracking Averages */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Activity className="w-4 h-4 text-teal-400" />
            1. Longitudinal Health Check Averages (14-Day Window)
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
              <span className="text-slate-500 block text-[10px]">Avg Dizziness</span>
              <strong className="text-teal-300 text-base">{hs.average_dizziness} / 10</strong>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
              <span className="text-slate-500 block text-[10px]">Avg Imbalance</span>
              <strong className="text-rose-300 text-base">{hs.average_imbalance} / 10</strong>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
              <span className="text-slate-500 block text-[10px]">Avg Sleep</span>
              <strong className="text-white text-base">{hs.average_sleep} hrs</strong>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs">
              <span className="text-slate-500 block text-[10px]">Avg Stress</span>
              <strong className="text-amber-300 text-base">{hs.average_stress} / 10</strong>
            </div>
          </div>
        </div>

        {/* Section 2: Questionnaire Screening Summary */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <ClipboardList className="w-4 h-4 text-indigo-400" />
            2. Questionnaire Screening Summary
          </h3>
          {qSummary ? (
            <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-2">
              <p className="text-[11px] text-slate-400">
                Completed on: {qSummary.completed_at ? new Date(qSummary.completed_at).toLocaleString() : 'Recent'}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                {qSummary.answers.map((a) => (
                  <div key={a.question_code} className="p-2 bg-slate-950/60 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] text-slate-500 font-mono block">{a.question_code}</span>
                    <p className="text-slate-300">{a.question_text}</p>
                    <strong className="text-teal-300 text-[11px]">
                      {typeof a.answer === 'boolean' ? (a.answer ? 'Yes' : 'No') : Array.isArray(a.answer) ? a.answer.join(', ') : String(a.answer)}
                    </strong>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 p-4 bg-slate-900/40 rounded-xl border border-slate-800">
              No completed questionnaire session on record.
            </p>
          )}
        </div>

        {/* Section 3: Eye Movement Screening Summary */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Eye className="w-4 h-4 text-cyan-400" />
            3. Eye-Movement Screening Summary (CV)
          </h3>
          {eyeSummary ? (
            <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-2">
              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span>Recorded: {new Date(eyeSummary.created_at).toLocaleString()}</span>
                <span className="font-mono text-cyan-300">
                  Tracking Quality: {((eyeSummary.quality?.valid_ratio || 0) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
                {Object.entries(eyeSummary.features).map(([fName, fVal]) => (
                  <div key={fName} className="p-2 bg-slate-950/60 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] text-slate-500 font-mono block truncate">
                      {fName.replace(/_/g, ' ')}
                    </span>
                    <strong className="text-white font-mono text-xs">
                      {typeof fVal === 'number' ? fVal.toFixed(3) : String(fVal)}
                    </strong>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 p-4 bg-slate-900/40 rounded-xl border border-slate-800">
              No eye-movement screening session on record.
            </p>
          )}
        </div>

        {/* Section 4: AI Screening Risk Estimate */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            4. AI Screening Risk Assessment
          </h3>
          {latestRisk ? (
            <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-3 text-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase ${
                      latestRisk.risk_level === 'HIGH'
                        ? 'bg-rose-950 text-rose-300 border border-rose-700'
                        : latestRisk.risk_level === 'MEDIUM'
                        ? 'bg-amber-950 text-amber-300 border border-amber-700'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    }`}
                  >
                    {latestRisk.risk_level} RISK
                  </span>
                  <span className="text-white font-mono font-bold">
                    Score: {latestRisk.risk_score.toFixed(2)} / 1.00
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">
                  {latestRisk.model_name} • {latestRisk.model_version}
                </span>
              </div>

              {latestRisk.contributing_factors?.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80">
                  <p className="text-[11px] font-semibold text-slate-300 mb-1">Key Contributing Factors:</p>
                  <ul className="text-xs text-slate-300 space-y-0.5 list-disc list-inside">
                    {latestRisk.contributing_factors.map((f, idx) => (
                      <li key={idx}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500 p-4 bg-slate-900/40 rounded-xl border border-slate-800">
              No AI risk assessment calculated yet.
            </p>
          )}
        </div>

        {/* Section 5: Clinician Notes */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <FileText className="w-4 h-4 text-teal-400" />
            5. Clinician Decision Support Notes ({report.clinical_notes.length})
          </h3>
          {report.clinical_notes.length === 0 ? (
            <p className="text-xs text-slate-500 p-4 bg-slate-900/40 rounded-xl border border-slate-800">
              No clinical notes recorded for this patient.
            </p>
          ) : (
            <div className="space-y-2">
              {report.clinical_notes.map((n) => (
                <div key={n.id} className="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-bold text-white">{n.doctor_name} ({n.note_type.replace(/_/g, ' ')})</span>
                    <span className="text-slate-500 font-mono">{new Date(n.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="text-slate-300 whitespace-pre-wrap">{n.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Medical Safety Disclaimer */}
        <div className="p-4 bg-teal-950/20 border border-teal-800/40 rounded-xl text-xs text-teal-300 flex items-start gap-2.5">
          <HelpCircle className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
          <span>{report.disclaimer}</span>
        </div>
      </div>
    </div>
  );
};

