import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { doctorApi } from '@/api/doctorApi';
import { SessionSummary } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ClipboardList, Calendar, CheckCircle2, HelpCircle } from 'lucide-react';

export const DoctorPatientQuestionnaire: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    async function loadQuestionnaires() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await doctorApi.getPatientQuestionnaires(id!);
        setSessions(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load questionnaire screening history.');
      } finally {
        setIsLoading(false);
      }
    }
    loadQuestionnaires();
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading completed questionnaire sessions..." />
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
          <h2 className="text-base font-bold text-white tracking-tight">Adaptive Questionnaire Screening History</h2>
          <p className="text-xs text-slate-400">
            Patient-reported responses collected through structured clinical branching logic.
          </p>
        </div>
        <span className="text-xs text-slate-500 font-mono">
          {sessions.length} completed sessions
        </span>
      </div>

      {sessions.length === 0 ? (
        <div className="p-8 text-center bg-slate-950/60 border border-slate-800 rounded-2xl text-xs text-slate-500">
          No completed questionnaire sessions found for this patient.
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((sess, idx) => (
            <div
              key={sess.session_id}
              className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl"
            >
              {/* Session Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800/80 gap-2">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-teal-950 border border-teal-800 flex items-center justify-center text-teal-400">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">
                      Screening Session #{sessions.length - idx}
                    </h3>
                    <p className="text-[11px] text-slate-400">
                      Completed:{' '}
                      {sess.completed_at
                        ? new Date(sess.completed_at).toLocaleString()
                        : 'Completed'}
                    </p>
                  </div>
                </div>

                <span className="text-[11px] font-mono text-teal-400 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                  {sess.total_questions_answered} questions answered
                </span>
              </div>

              {/* Answers Grid */}
              <div className="space-y-3">
                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Structured Patient Responses
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {sess.answers.map((a) => (
                    <div
                      key={a.question_code}
                      className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1 text-xs"
                    >
                      <span className="text-[10px] font-mono text-teal-400/80 uppercase">
                        {a.question_code}
                      </span>
                      <p className="text-slate-200 font-medium">{a.question_text}</p>
                      <p className="text-teal-300 font-semibold pt-0.5">
                        Answer:{' '}
                        {typeof a.answer === 'boolean'
                          ? a.answer
                            ? 'Yes'
                            : 'No'
                          : Array.isArray(a.answer)
                          ? a.answer.join(', ')
                          : String(a.answer)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Non-diagnostic notice */}
              <div className="p-3 bg-slate-900/40 border border-slate-800 rounded-xl text-[11px] text-slate-400 flex items-start gap-2">
                <HelpCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                <span>
                  Responses represent patient self-reporting and provide triage decision support. VertiCare AI does not assert confirmed clinical diagnoses based solely on questionnaire responses.
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

