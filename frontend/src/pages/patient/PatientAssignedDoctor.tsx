import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { assignmentApi } from '@/api/assignmentApi';
import { useAuth } from '@/hooks/useAuth';
import { AssignedDoctor } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import {
  Stethoscope,
  UserPlus,
  Copy,
  Check,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  PhoneCall,
  UserCheck,
  Trash2,
  Calendar,
  Award,
} from 'lucide-react';

export const PatientAssignedDoctor: React.FC = () => {
  const { user } = useAuth();
  const [doctorInfo, setDoctorInfo] = useState<AssignedDoctor | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Add Doctor Modal State
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [doctorIdInput, setDoctorIdInput] = useState<string>('');
  const [isAssigning, setIsAssigning] = useState<boolean>(false);
  const [assignError, setAssignError] = useState<string | null>(null);
  const [assignSuccess, setAssignSuccess] = useState<string | null>(null);

  // Unassign Modal State
  const [showUnassignModal, setShowUnassignModal] = useState<boolean>(false);
  const [isUnassigning, setIsUnassigning] = useState<boolean>(false);

  // Copy Feedback
  const [copiedPatientId, setCopiedPatientId] = useState<boolean>(false);

  const loadDoctor = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await assignmentApi.getAssignedDoctor();
      setDoctorInfo(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load assigned doctor details.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDoctor();
  }, []);

  const handleCopyPatientId = () => {
    const idToCopy = user?.patient_profile_id || user?.id || '';
    if (idToCopy) {
      navigator.clipboard.writeText(idToCopy);
      setCopiedPatientId(true);
      setTimeout(() => setCopiedPatientId(false), 2000);
    }
  };

  const handleAssignDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanId = doctorIdInput.trim();
    if (!cleanId) {
      setAssignError('Please enter a valid Doctor ID.');
      return;
    }

    setIsAssigning(true);
    setAssignError(null);
    setAssignSuccess(null);

    try {
      const res = await assignmentApi.createAssignment({ doctor_id: cleanId });
      setAssignSuccess(`Successfully assigned to ${res.doctor_name}.`);
      setDoctorIdInput('');
      setShowAddModal(false);
      await loadDoctor();
    } catch (err: any) {
      let msg = 'Failed to assign doctor. Please verify the Doctor ID.';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') msg = detail;
        else if (Array.isArray(detail)) msg = detail.map((d: any) => d.msg).join(', ');
      }
      setAssignError(msg);
    } finally {
      setIsAssigning(false);
    }
  };

  const handleUnassignDoctor = async () => {
    if (!doctorInfo?.assignment_id) return;
    setIsUnassigning(true);
    try {
      await assignmentApi.deleteAssignment(doctorInfo.assignment_id);
      setShowUnassignModal(false);
      setAssignSuccess('Doctor assignment removed.');
      await loadDoctor();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to remove doctor assignment.');
    } finally {
      setIsUnassigning(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      {/* Title & Copyable Patient ID Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
            <Stethoscope className="w-4 h-4" />
            <span>Clinical Care Team</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Assigned Doctor</h1>
          <p className="text-xs text-slate-400">
            Manage your dedicated clinician relationship for vestibular monitoring and decision support.
          </p>
        </div>

        {/* Copyable Patient ID */}
        <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl text-xs self-start sm:self-auto">
          <UserCheck className="w-3.5 h-3.5 text-teal-400" />
          <span className="text-slate-400 text-[11px]">Your Patient ID:</span>
          <span className="font-mono text-teal-300 font-bold text-[11px] max-w-[130px] truncate">
            {user?.patient_profile_id || user?.id}
          </span>
          <button
            onClick={handleCopyPatientId}
            title="Copy Patient ID for doctor to connect"
            className="text-slate-400 hover:text-white transition p-1"
          >
            {copiedPatientId ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Success Alert */}
      {assignSuccess && (
        <div className="p-3 bg-emerald-950/60 border border-emerald-800 rounded-xl text-xs text-emerald-200 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{assignSuccess}</span>
          </div>
          <button onClick={() => setAssignSuccess(null)} className="text-emerald-400 text-xs hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="py-16 text-center">
          <LoadingSpinner size="md" label="Loading clinical relationship..." />
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/30 border border-rose-800/50 rounded-xl text-xs text-rose-300">
          {error}
        </div>
      ) : doctorInfo?.has_assigned_doctor ? (
        /* Doctor Assigned View */
        <div className="space-y-6">
          <div className="p-6 sm:p-8 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-6 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-teal-950 border border-teal-700 flex items-center justify-center text-teal-400 font-bold text-lg">
                  <Stethoscope className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">{doctorInfo.doctor_name}</h2>
                  <p className="text-xs text-teal-400">{doctorInfo.specialization}</p>
                </div>
              </div>

              <span className="px-3 py-1 bg-emerald-950 text-emerald-300 border border-emerald-800 rounded-full text-xs font-bold self-start sm:self-auto flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Active Care Provider
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                  Doctor ID
                </span>
                <p className="font-mono text-white text-[11px] truncate">{doctorInfo.doctor_id}</p>
              </div>

              <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                  License Identifier
                </span>
                <p className="font-mono text-slate-200 text-xs">{doctorInfo.license_identifier || 'Verified Clinician'}</p>
              </div>

              <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[10px] uppercase font-semibold block">
                  Assignment Date
                </span>
                <p className="text-slate-200 text-xs">
                  {doctorInfo.assigned_at ? new Date(doctorInfo.assigned_at).toLocaleDateString() : 'Active'}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
              <Link to="/patient/emergency">
                <Button size="sm" variant="outline" className="text-xs gap-1.5 text-rose-300 border-rose-900/60 hover:bg-rose-950/40">
                  <PhoneCall className="w-3.5 h-3.5 text-rose-400" />
                  <span>Request Emergency Review</span>
                </Button>
              </Link>

              <button
                onClick={() => setShowUnassignModal(true)}
                className="text-xs text-slate-500 hover:text-rose-400 transition flex items-center gap-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Remove Doctor Assignment</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Empty State — No Doctor Assigned */
        <div className="p-12 text-center bg-slate-950/60 border border-slate-800 rounded-2xl space-y-4 shadow-xl">
          <Stethoscope className="w-12 h-12 text-slate-600 mx-auto" />
          <div className="space-y-1.5 max-w-md mx-auto">
            <h2 className="text-base font-bold text-white">No Doctor Assigned Yet</h2>
            <p className="text-xs text-slate-400">
              Connect with your vestibular specialist or neurotologist using their unique Doctor ID to share your symptom logs and screening tests.
            </p>
          </div>

          <Button
            size="sm"
            onClick={() => {
              setShowAddModal(true);
              setAssignError(null);
            }}
            className="gap-1.5 text-xs shadow-md"
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>+ Add Doctor</span>
          </Button>
        </div>
      )}

      {/* Add Doctor Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <form
            onSubmit={handleAssignDoctor}
            className="max-w-md w-full p-6 bg-slate-950 border border-teal-800 rounded-2xl space-y-4 shadow-2xl"
          >
            <div className="space-y-1">
              <h3 className="text-base font-bold text-white">Add Doctor</h3>
              <p className="text-xs text-slate-300">
                Enter the Doctor ID provided by your healthcare provider.
              </p>
            </div>

            {assignError && (
              <div className="p-3 bg-rose-950/60 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span>{assignError}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Doctor ID
              </label>
              <input
                type="text"
                value={doctorIdInput}
                onChange={(e) => setDoctorIdInput(e.target.value)}
                placeholder="e.g. 5efc4bfa-4f0d-4c8b-b123-d055b9fdba6e"
                className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-teal-500"
                required
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Your doctor can find their Doctor ID in their clinician portal header or directory.
              </p>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => {
                  setShowAddModal(false);
                  setAssignError(null);
                }}
                className="text-xs"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                size="sm"
                variant="primary"
                isLoading={isAssigning}
                className="text-xs"
              >
                Assign Doctor
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Unassign Confirmation Modal */}
      {showUnassignModal && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <div className="max-w-md w-full p-6 bg-slate-950 border border-slate-800 rounded-2xl space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Remove Doctor Assignment?</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Confirm removal of your assignment with {doctorInfo?.doctor_name}. You can reassign at any time using their Doctor ID.
            </p>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowUnassignModal(false)}
                className="text-xs"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleUnassignDoctor}
                isLoading={isUnassigning}
                className="text-xs text-rose-300 hover:bg-rose-950/40"
              >
                Confirm Removal
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

