import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { emergencyApi } from '@/api/emergencyApi';
import { EmergencyEvent, EmergencyStatus } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Clock,
  User,
  Filter,
  XCircle,
  Sparkles,
  ArrowRight,
  HelpCircle,
  MessageSquare,
} from 'lucide-react';

export const DoctorEmergencies: React.FC = () => {
  const [events, setEvents] = useState<EmergencyEvent[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Clinician Action State
  const [actionEventId, setActionEventId] = useState<string | null>(null);
  const [actionType, setActionType] = useState<'ACKNOWLEDGE' | 'RESOLVE' | null>(null);
  const [actionNotes, setActionNotes] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  useEffect(() => {
    loadEvents();
  }, [statusFilter]);

  async function loadEvents() {
    setIsLoading(true);
    setError(null);
    try {
      const res = await emergencyApi.listEvents({
        status: statusFilter === 'ALL' ? undefined : statusFilter,
        limit: 50,
      });
      setEvents(res.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load emergency support events.');
    } finally {
      setIsLoading(false);
    }
  }

  const handleExecuteDoctorAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionEventId || !actionType) return;
    setIsProcessing(true);
    try {
      await emergencyApi.executeDoctorAction(
        actionEventId,
        actionType,
        actionNotes.trim() || undefined
      );
      setActionEventId(null);
      setActionType(null);
      setActionNotes('');
      await loadEvents();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to execute status transition.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-rose-400">
            <ShieldAlert className="w-4 h-4" />
            <span>Assigned Patient Emergency Triage</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Emergency Support & Escalations
          </h1>
          <p className="text-xs text-slate-400">
            Real-time monitoring of urgent support requests and escalation events initiated by your assigned patients.
          </p>
        </div>

        <span className="text-xs text-slate-500 font-mono self-start sm:self-auto bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
          {events.length} events matching filter
        </span>
      </div>

      {/* Filter Tabs */}
      <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-2xl flex flex-wrap items-center gap-2 shadow-lg">
        <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1 mr-1">
          <Filter className="w-3 h-3" />
          Status Filter:
        </span>
        {(['ALL', 'PENDING', 'CONTACT_INITIATED', 'ACKNOWLEDGED', 'RESOLVED', 'CANCELLED'] as const).map(
          (st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                statusFilter === st
                  ? st === 'PENDING' || st === 'CONTACT_INITIATED'
                    ? 'bg-amber-950 text-amber-300 border border-amber-700'
                    : st === 'RESOLVED'
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    : st === 'CANCELLED'
                    ? 'bg-slate-800 text-slate-300'
                    : 'bg-teal-600 text-white shadow'
                  : 'bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {st.replace(/_/g, ' ')}
            </button>
          )
        )}
      </div>

      {/* Emergency Events List */}
      {isLoading ? (
        <div className="py-16 text-center">
          <LoadingSpinner size="md" label="Loading emergency support queue..." />
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/30 border border-rose-800/50 rounded-xl text-xs text-rose-300">
          {error}
        </div>
      ) : events.length === 0 ? (
        <div className="p-12 text-center bg-slate-950/60 border border-slate-800 rounded-2xl space-y-3">
          <CheckCircle2 className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-sm font-bold text-white">No emergency-support events</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            {statusFilter !== 'ALL'
              ? `No assigned patient events found with status ${statusFilter.replace(/_/g, ' ')}.`
              : 'There are currently no urgent escalation events recorded for your assigned cohort.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {events.map((ev) => (
            <div
              key={ev.id}
              className={`p-6 rounded-2xl space-y-4 shadow-xl border transition ${
                ev.status === 'PENDING' || ev.status === 'CONTACT_INITIATED'
                  ? 'bg-slate-950/90 border-amber-800/70'
                  : ev.status === 'RESOLVED'
                  ? 'bg-slate-950/60 border-slate-800 opacity-90'
                  : 'bg-slate-950/60 border-slate-800 opacity-75'
              }`}
            >
              {/* Event Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800/80 gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-teal-400 font-bold text-base shrink-0">
                    {ev.patient_name?.charAt(0) || 'P'}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <Link
                        to={`/doctor/patients/${ev.patient_id}`}
                        className="text-sm font-bold text-white hover:text-teal-400 transition"
                      >
                        {ev.patient_name}
                      </Link>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                          ev.severity === 'CRITICAL'
                            ? 'bg-rose-950 text-rose-300 border border-rose-700'
                            : ev.severity === 'HIGH'
                            ? 'bg-rose-950/80 text-rose-300 border border-rose-800'
                            : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}
                      >
                        {ev.severity} SEVERITY
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      DOB: {ev.patient_dob} • Gender: {ev.patient_gender}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wider ${
                      ev.status === 'PENDING'
                        ? 'bg-amber-950 text-amber-300 border border-amber-700 animate-pulse'
                        : ev.status === 'CONTACT_INITIATED'
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-700'
                        : ev.status === 'ACKNOWLEDGED'
                        ? 'bg-indigo-950 text-indigo-300 border border-indigo-700'
                        : ev.status === 'RESOLVED'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {ev.status.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                    {new Date(ev.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Event Content & Contact Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                    Contact Channels
                  </span>
                  <p>
                    Doctor Contact:{' '}
                    <strong className={ev.contacted_doctor ? 'text-teal-300' : 'text-slate-500'}>
                      {ev.contacted_doctor ? 'Requested' : 'No'}
                    </strong>
                  </p>
                  <p>
                    Emergency Contact:{' '}
                    <strong className={ev.contacted_emergency_contact ? 'text-cyan-300' : 'text-slate-500'}>
                      {ev.contacted_emergency_contact ? 'Initiated' : 'No'}
                    </strong>
                  </p>
                  {ev.emergency_contact_name && (
                    <p className="text-[11px] text-slate-400 truncate">
                      EC: {ev.emergency_contact_name} ({ev.emergency_contact_phone})
                    </p>
                  )}
                </div>

                <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                    Screening Context
                  </span>
                  <p>
                    AI Risk Level:{' '}
                    <strong className="text-white">
                      {ev.risk_level ? `${ev.risk_level} (${ev.risk_score?.toFixed(2)})` : 'Not linked'}
                    </strong>
                  </p>
                  <Link
                    to={`/doctor/patients/${ev.patient_id}`}
                    className="text-teal-400 hover:underline flex items-center gap-1 pt-1 text-[11px]"
                  >
                    <span>View Patient Record</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>

                <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1 md:col-span-1">
                  <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                    Event Notes & Log
                  </span>
                  <p className="text-slate-300 whitespace-pre-wrap line-clamp-3">
                    {ev.notes || 'No additional symptom notes recorded.'}
                  </p>
                </div>
              </div>

              {/* Action Controls for Assigned Clinician */}
              {ev.status !== 'RESOLVED' && ev.status !== 'CANCELLED' && (
                <div className="flex flex-wrap items-center justify-end gap-2 pt-2 border-t border-slate-800/80">
                  {ev.status !== 'ACKNOWLEDGED' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setActionEventId(ev.id);
                        setActionType('ACKNOWLEDGE');
                        setActionNotes('');
                      }}
                      className="text-xs gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
                      <span>Mark Acknowledged</span>
                    </Button>
                  )}

                  <Button
                    size="sm"
                    variant="primary"
                    onClick={() => {
                      setActionEventId(ev.id);
                      setActionType('RESOLVE');
                      setActionNotes('');
                    }}
                    className="text-xs gap-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Mark Resolved</span>
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Clinician Action Modal */}
      {actionEventId && actionType && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <form
            onSubmit={handleExecuteDoctorAction}
            className="max-w-md w-full p-6 bg-slate-950 border border-teal-800 rounded-2xl space-y-4 shadow-2xl"
          >
            <h3 className="text-base font-bold text-white">
              {actionType === 'ACKNOWLEDGE' ? 'Acknowledge Emergency Event' : 'Resolve Emergency Event'}
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              {actionType === 'ACKNOWLEDGE'
                ? 'Confirming that you have seen this escalation event and are following up with the patient.'
                : 'Confirming that clinical evaluation or follow-up has occurred and this emergency support event is resolved.'}
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Clinician Note / Action Record
              </label>
              <textarea
                rows={3}
                value={actionNotes}
                onChange={(e) => setActionNotes(e.target.value)}
                placeholder="Enter triage notes, phone consultation summary, or next appointment instructions..."
                className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => {
                  setActionEventId(null);
                  setActionType(null);
                }}
                className="text-xs"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                size="sm"
                variant="primary"
                isLoading={isProcessing}
                className="text-xs"
              >
                {actionType === 'ACKNOWLEDGE' ? 'Confirm Acknowledged' : 'Confirm Resolved'}
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

