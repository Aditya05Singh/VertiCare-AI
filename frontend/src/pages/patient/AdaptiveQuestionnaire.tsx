import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { questionnaireApi } from '@/api/questionnaireApi';
import { QuestionnaireSession, SessionSummary } from '@/types';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import {
  ClipboardList,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  RotateCcw,
  ShieldAlert,
  FileCheck,
  Activity,
} from 'lucide-react';

export const AdaptiveQuestionnaire: React.FC = () => {
  const [session, setSession] = useState<QuestionnaireSession | null>(null);
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Check for active session on load
  useEffect(() => {
    async function loadActiveSession() {
      try {
        const active = await questionnaireApi.checkActive();
        if (active) {
          setSession(active);
          if (active.status === 'COMPLETED') {
            const sum = await questionnaireApi.getSummary(active.session_id);
            setSummary(sum);
          }
        }
      } catch (err) {
        console.error('Error fetching active session:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadActiveSession();
  }, []);

  const handleStartOrResume = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const sess = await questionnaireApi.startOrResume();
      setSession(sess);
      setSelectedAnswer(null);
      if (sess.status === 'COMPLETED') {
        const sum = await questionnaireApi.getSummary(sess.session_id);
        setSummary(sum);
      }
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Failed to start questionnaire.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerSubmit = async () => {
    if (!session || !session.current_question) return;

    if (selectedAnswer === null || selectedAnswer === undefined || (Array.isArray(selectedAnswer) && selectedAnswer.length === 0)) {
      setErrorMessage('Please select or enter an answer to continue.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const updatedSession = await questionnaireApi.submitAnswer(
        session.session_id,
        session.current_question.question_code,
        selectedAnswer
      );
      setSession(updatedSession);
      setSelectedAnswer(null);

      if (updatedSession.status === 'COMPLETED') {
        const sum = await questionnaireApi.getSummary(updatedSession.session_id);
        setSummary(sum);
      }
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Failed to record answer.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleMultiChoice = (val: string) => {
    const current = Array.isArray(selectedAnswer) ? [...selectedAnswer] : [];
    if (current.includes(val)) {
      setSelectedAnswer(current.filter((item) => item !== val));
    } else {
      setSelectedAnswer([...current, val]);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" label="Loading adaptive questionnaire..." />
      </div>
    );
  }

  // 1. Completion State View
  if (session?.status === 'COMPLETED' && summary) {
    return (
      <div className="max-w-3xl mx-auto space-y-6 pb-12">
        <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-2xl space-y-4 shadow-xl text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-950 border border-emerald-700 text-emerald-400 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Screening Assessment Completed
          </h1>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            Your structured symptom responses have been recorded. Total questions answered: <strong className="text-white">{summary.total_questions_answered}</strong>.
          </p>

          <div className="p-3 bg-teal-950/30 border border-teal-800/60 rounded-xl text-xs text-teal-300 text-left flex items-start gap-2.5">
            <HelpCircle className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <span>{summary.notice}</span>
          </div>
        </div>

        {/* Structured Answers Summary */}
        <div className="p-6 bg-slate-950/50 border border-slate-800 rounded-2xl space-y-4">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-teal-400" />
            Recorded Response Summary
          </h2>

          <div className="divide-y divide-slate-800/80">
            {summary.answers.map((item, idx) => (
              <div key={idx} className="py-3 space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300">{item.question_text}</span>
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                    {item.category}
                  </span>
                </div>
                <p className="text-xs text-teal-300 font-medium">
                  {typeof item.answer === 'boolean'
                    ? item.answer ? 'Yes' : 'No'
                    : Array.isArray(item.answer)
                    ? item.answer.join(', ')
                    : String(item.answer)}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center gap-4">
          <Link to="/patient/dashboard">
            <Button variant="primary">Return to Patient Dashboard</Button>
          </Link>
        </div>
      </div>
    );
  }

  // 2. Active In-Progress Question View
  if (session?.status === 'IN_PROGRESS' && session.current_question) {
    const q = session.current_question;

    return (
      <div className="max-w-2xl mx-auto space-y-6 pb-12">
        {/* Header & Adaptive Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-teal-400 font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <ClipboardList className="w-4 h-4" />
              Adaptive Questionnaire • Step {session.progress.current_step}
            </span>
            <span className="text-[11px] font-mono text-slate-400 uppercase bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              Category: {q.category}
            </span>
          </div>

          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-teal-500 h-full transition-all duration-300"
              style={{
                width: `${Math.min(100, (session.progress.answered_count / session.progress.estimated_total) * 100)}%`,
              }}
            />
          </div>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Question Card */}
        <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-2xl space-y-6 shadow-xl">
          <h2 className="text-lg sm:text-xl font-bold text-white leading-snug">
            {q.question_text}
          </h2>

          {/* Render Controls by Question Type */}
          {q.question_type === 'BOOLEAN' && (
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setSelectedAnswer(true)}
                className={`p-4 rounded-xl border text-sm font-semibold transition-all ${
                  selectedAnswer === true
                    ? 'bg-teal-600/20 border-teal-500 text-teal-300 shadow-md ring-1 ring-teal-500'
                    : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                Yes
              </button>
              <button
                type="button"
                onClick={() => setSelectedAnswer(false)}
                className={`p-4 rounded-xl border text-sm font-semibold transition-all ${
                  selectedAnswer === false
                    ? 'bg-teal-600/20 border-teal-500 text-teal-300 shadow-md ring-1 ring-teal-500'
                    : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                No
              </button>
            </div>
          )}

          {q.question_type === 'SINGLE_CHOICE' && (
            <div className="space-y-2.5">
              {q.options.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setSelectedAnswer(opt.value)}
                  className={`w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm transition-all ${
                    selectedAnswer === opt.value
                      ? 'bg-teal-600/20 border-teal-500 text-teal-200 font-medium ring-1 ring-teal-500'
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}

          {q.question_type === 'MULTI_CHOICE' && (
            <div className="space-y-2.5">
              <p className="text-[11px] text-slate-400">Select all options that apply to your symptoms:</p>
              {q.options.map((opt) => {
                const isSelected = Array.isArray(selectedAnswer) && selectedAnswer.includes(opt.value);
                return (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => toggleMultiChoice(opt.value)}
                    className={`w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm transition-all ${
                      isSelected
                        ? 'bg-teal-600/20 border-teal-500 text-teal-200 font-medium ring-1 ring-teal-500'
                        : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          )}

          {q.question_type === 'NUMBER' && (
            <div className="space-y-2">
              <input
                type="number"
                value={selectedAnswer ?? ''}
                onChange={(e) => setSelectedAnswer(e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="Enter value..."
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-teal-500"
              />
            </div>
          )}

          {q.question_type === 'TEXT' && (
            <div className="space-y-2">
              <textarea
                rows={3}
                value={selectedAnswer ?? ''}
                onChange={(e) => setSelectedAnswer(e.target.value)}
                placeholder="Describe your symptoms..."
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-teal-500"
              />
            </div>
          )}

          {/* Navigation Action */}
          <div className="pt-2">
            <Button
              type="button"
              className="w-full gap-2 justify-center"
              onClick={handleAnswerSubmit}
              isLoading={isSubmitting}
            >
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // 3. Intro / Start State View
  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
          <ClipboardList className="w-4 h-4" />
          <span>Screening Workflow</span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Adaptive Vestibular Questionnaire</h1>
        <p className="text-xs text-slate-400">
          An intelligent screening module that adapts follow-up questions dynamically based on your reported symptoms.
        </p>
      </div>

      {errorMessage && (
        <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Safety & Protocol Card */}
      <div className="p-6 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-4 shadow-xl">
        <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-teal-400" />
          About This Assessment
        </h2>
        <ul className="text-xs text-slate-300 space-y-2 list-disc list-inside">
          <li><strong>Adaptive Branching:</strong> Questions adapt depending on whether dizziness is spinning, positional, brief, or prolonged.</li>
          <li><strong>Deterministic Rules:</strong> All questions and branches follow verified clinical screening logic without generative AI unpredictability.</li>
          <li><strong>Save & Resume:</strong> You can exit and resume your assessment at any time without losing completed answers.</li>
        </ul>

        <div className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl text-[11px] text-slate-400 leading-relaxed">
          <strong className="text-slate-300">Important:</strong> VertiCare AI is an academic healthcare prototype. This questionnaire collects structured screening context for qualified ENT and neurology clinician reviews and does not diagnose disease or replace professional examination.
        </div>

        <Button
          onClick={handleStartOrResume}
          className="w-full sm:w-auto gap-2"
          size="lg"
        >
          <span>{session ? 'Resume Assessment' : 'Start Assessment'}</span>
          <ArrowRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};

