import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { emergencyApi } from '@/api/emergencyApi';
import {
  EmergencyContext,
  EmergencyEvent,
  EmergencyGuidance,
} from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import {
  AlertTriangle,
  PhoneCall,
  UserCheck,
  ShieldAlert,
  HelpCircle,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Shield,
  Info,
} from 'lucide-react';

export const PatientEmergency: React.FC = () => {
  const [context, setContext] = useState<EmergencyContext | null>(null);
  const [guidance, setGuidance] = useState<EmergencyGuidance | null>(null);
  const [events, setEvents] = useState<EmergencyEvent[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modal / Confirmation States
  const [showDoctorModal, setShowDoctorModal] = useState<boolean>(false);
  const [showContactModal, setShowContactModal] = useState<boolean>(false);
  const [showCancelModal, setShowCancelModal] = useState<boolean>(false);
  const [doctorNotes, setDoctorNotes] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setIsLoading(true);
    setError(null);
    try {
      const [ctxRes, gRes, evList] = await Promise.all([
        emergencyApi.getContext(),
        emergencyApi.getGuidance(),
        emergencyApi.listEvents({ limit: 10 }),
      ]);
      setContext(ctxRes);
      setGuidance(gRes);
      setEvents(evList.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load emergency support context.');
    } finally {
      setIsLoading(false);
    }
  }

  const activeEvent = context?.active_event;

  // Handle Contact Doctor
  const handleConfirmContactDoctor = async () => {
    setIsProcessing(true);
    setActionSuccessMsg(null);
    try {
      if (activeEvent) {
        await emergencyApi.executePatientAction(activeEvent.id, 'CONTACT_DOCTOR', doctorNotes || undefined);
      } else {
        await emergencyApi.createEvent({
          severity: 'HIGH',
          risk_assessment_id: context?.latest_risk_assessment_id,
          notes: doctorNotes || 'Patient initiated doctor contact request.',
          initiate_doctor_contact: true,
        });
      }
      setShowDoctorModal(false);
      setDoctorNotes('');
      setActionSuccessMsg(
        'Your request has been recorded. Please use the available contact method or clinical appointment to reach your doctor.'
      );
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to initiate doctor contact.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle Contact Personal Emergency Contact
  const handleConfirmEmergencyContact = async () => {
    setIsProcessing(true);
    setActionSuccessMsg(null);
    try {
      if (activeEvent) {
        await emergencyApi.executePatientAction(activeEvent.id, 'CONTACT_EMERGENCY_CONTACT');
      } else {
        await emergencyApi.createEvent({
          severity: 'HIGH',
          risk_assessment_id: context?.latest_risk_assessment_id,
          notes: 'Patient initiated emergency contact notification.',
          initiate_emergency_contact: true,
        });
      }
      setShowContactModal(false);
      setActionSuccessMsg(
        'Emergency contact action recorded. Please use your phone or messaging app to speak directly with your emergency contact.'
      );
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to record emergency contact action.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle Cancel Active Event
  const handleCancelActiveEvent = async () => {
    if (!activeEvent) return;
    setIsProcessing(true);
    try {
      await emergencyApi.executePatientAction(activeEvent.id, 'CANCEL', 'Cancelled by patient.');
      setShowCancelModal(false);
      setActionSuccessMsg('Active emergency support event marked as cancelled.');
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel event.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading emergency support options..." />
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
    <div className="space-y-8 max-w-4xl mx-auto pb-12">
      {/* Primary Emergency Banner */}
      <div className="p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-rose-950/40 via-slate-900 to-slate-900 border border-rose-900/50 shadow-2xl space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-rose-400">
          <ShieldAlert className="w-5 h-5 text-rose-400" />
          <span>Emergency Support & Escalation</span>
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Urgent Clinical & Safety Support
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            If you are experiencing severe, sudden, or rapidly worsening symptoms (such as inability to walk, slurred speech, chest pain, or visual loss), seek appropriate emergency medical care immediately.
          </p>
        </div>

        {/* Action Success Alert */}
        {actionSuccessMsg && (
          <div className="p-4 bg-teal-950/60 border border-teal-700/60 rounded-xl text-xs text-teal-200 flex items-start gap-2.5 shadow-lg">
            <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <span>{actionSuccessMsg}</span>
          </div>
        )}

        {/* Active Support Event Tracker */}
        {activeEvent && (
          <div className="p-4 bg-slate-950/90 border border-amber-800/60 rounded-xl space-y-2 shadow-inner">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Active Emergency Event ({activeEvent.status.replace(/_/g, ' ')})
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                Created: {new Date(activeEvent.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>

            <div className="text-xs text-slate-300 grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 border-t border-slate-800/80">
              <p>
                Doctor Contact:{' '}
                <strong className={activeEvent.contacted_doctor ? 'text-teal-400' : 'text-slate-500'}>
                  {activeEvent.contacted_doctor ? 'Initiated' : 'Not Requested'}
                </strong>
              </p>
              <p>
                Emergency Contact:{' '}
                <strong className={activeEvent.contacted_emergency_contact ? 'text-teal-400' : 'text-slate-500'}>
                  {activeEvent.contacted_emergency_contact ? 'Initiated' : 'Not Requested'}
                </strong>
              </p>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setShowCancelModal(true)}
                className="text-xs text-slate-400 hover:text-rose-400 transition underline font-medium"
              >
                Cancel active event (symptoms resolved or false alarm)
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Support Action Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Action 1: Contact Doctor */}
        <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-400">
              <UserCheck className="w-4 h-4" />
              <span>Clinician Contact</span>
            </div>
            <h2 className="text-lg font-bold text-white">Contact Assigned Doctor</h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              Record a support request for your assigned doctor and initiate clinical review.
            </p>

            {context?.has_assigned_doctor ? (
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-1">
                <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                  Assigned Clinician
                </span>
                <p className="font-bold text-white">{context.assigned_doctor_name}</p>
                <p className="text-slate-400 text-[11px]">{context.assigned_doctor_specialization}</p>
              </div>
            ) : (
              <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800 text-xs text-slate-500">
                No doctor is currently assigned to your patient account.
              </div>
            )}
          </div>

          <Button
            size="sm"
            variant="primary"
            onClick={() => setShowDoctorModal(true)}
            className="w-full text-xs gap-1.5 justify-center py-2.5"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Contact Doctor</span>
          </Button>
        </div>

        {/* Action 2: Contact Personal Emergency Contact */}
        <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400">
              <PhoneCall className="w-4 h-4" />
              <span>Personal Emergency Contact</span>
            </div>
            <h2 className="text-lg font-bold text-white">Contact Emergency Contact</h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              Reach your designated emergency contact registered in your patient profile.
            </p>

            {context?.has_emergency_contact ? (
              <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-1">
                <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                  Configured Contact
                </span>
                <p className="font-bold text-white">{context.emergency_contact_name}</p>
                <p className="text-teal-300 font-mono text-xs">{context.emergency_contact_phone}</p>
              </div>
            ) : (
              <div className="p-3 bg-rose-950/30 rounded-xl border border-rose-900/50 text-xs text-rose-300 space-y-2">
                <p>No emergency contact is configured in your profile.</p>
              </div>
            )}
          </div>

          {context?.has_emergency_contact ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowContactModal(true)}
              className="w-full text-xs gap-1.5 justify-center py-2.5 text-cyan-300 border-cyan-800/60 hover:bg-cyan-950/40"
            >
              <PhoneCall className="w-3.5 h-3.5" />
              <span>Contact Emergency Contact</span>
            </Button>
          ) : (
            <Link to="/patient/dashboard" className="block w-full">
              <Button size="sm" variant="outline" className="w-full text-xs gap-1.5 justify-center py-2.5">
                <span>Update Contact in Profile</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Emergency Guidance Section */}
      <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
          <HelpCircle className="w-4 h-4 text-teal-400" />
          <span>General Emergency Safety Guidance</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {guidance?.guidance.map((g, idx) => (
            <div
              key={idx}
              className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5 text-xs"
            >
              <h3 className="font-bold text-white flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                {g.title}
              </h3>
              <p className="text-slate-300 leading-relaxed">{g.description}</p>
            </div>
          ))}
        </div>

        <div className="p-3 bg-teal-950/20 border border-teal-800/40 rounded-xl text-[11px] text-teal-300 flex items-start gap-2">
          <Info className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
          <span>{guidance?.disclaimer}</span>
        </div>
      </div>

      {/* Emergency History Log */}
      <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
            <Clock className="w-4 h-4 text-teal-400" />
            <span>Emergency Support History</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">{events.length} recorded</span>
        </div>

        {events.length === 0 ? (
          <p className="text-xs text-slate-500 text-center py-4 bg-slate-900/40 rounded-xl border border-slate-800">
            No emergency support events recorded.
          </p>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {events.map((ev) => (
              <div key={ev.id} className="py-3 flex items-center justify-between text-xs">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                        ev.status === 'RESOLVED'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : ev.status === 'CANCELLED'
                          ? 'bg-slate-800 text-slate-400'
                          : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}
                    >
                      {ev.status}
                    </span>
                    <span className="text-white font-semibold">Severity: {ev.severity}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">{ev.notes || 'Emergency support requested.'}</p>
                </div>

                <div className="text-right text-[11px] text-slate-500 font-mono">
                  <span>{new Date(ev.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Confirmation Modal: Contact Doctor */}
      {showDoctorModal && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <div className="max-w-md w-full p-6 bg-slate-950 border border-teal-800 rounded-2xl space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Contact Your Assigned Doctor?</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              This will record an emergency support event and flag it for your clinician's review.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Optional Message / Symptoms
              </label>
              <textarea
                rows={3}
                value={doctorNotes}
                onChange={(e) => setDoctorNotes(e.target.value)}
                placeholder="Describe current dizziness severity, nausea, or triggering circumstances..."
                className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowDoctorModal(false)}
                className="text-xs"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                variant="primary"
                onClick={handleConfirmContactDoctor}
                isLoading={isProcessing}
                className="text-xs"
              >
                Confirm Request
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal: Contact Emergency Contact */}
      {showContactModal && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <div className="max-w-md w-full p-6 bg-slate-950 border border-cyan-800 rounded-2xl space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Contact Personal Emergency Contact?</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              You can call your emergency contact directly using the link below.
            </p>

            {context?.emergency_contact_phone && (
              <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 text-center space-y-1">
                <span className="text-[11px] text-slate-400 block">{context.emergency_contact_name}</span>
                <a
                  href={`tel:${context.emergency_contact_phone}`}
                  className="text-lg font-bold font-mono text-teal-400 hover:underline block"
                >
                  {context.emergency_contact_phone}
                </a>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowContactModal(false)}
                className="text-xs"
              >
                Close
              </Button>
              <Button
                size="sm"
                variant="primary"
                onClick={handleConfirmEmergencyContact}
                isLoading={isProcessing}
                className="text-xs"
              >
                Record Contact Action
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal: Cancel Active Event */}
      {showCancelModal && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <div className="max-w-md w-full p-6 bg-slate-950 border border-slate-800 rounded-2xl space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Cancel Active Support Event?</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Confirm cancellation if symptoms have subsided or the support request was initiated in error.
            </p>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowCancelModal(false)}
                className="text-xs"
              >
                Keep Active
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleCancelActiveEvent}
                isLoading={isProcessing}
                className="text-xs text-rose-300 hover:bg-rose-950/40"
              >
                Confirm Cancellation
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
