import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { doctorApi } from '@/api/doctorApi';
import { assignmentApi } from '@/api/assignmentApi';
import { useAuth } from '@/hooks/useAuth';
import { AssignedPatientCard } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import {
  Users,
  Search,
  Filter,
  ArrowUpDown,
  ArrowRight,
  UserPlus,
  Copy,
  Check,
  CheckCircle2,
  AlertCircle,
  Stethoscope,
} from 'lucide-react';

export const DoctorPatientList: React.FC = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState<AssignedPatientCard[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<string>('recent');
  const [error, setError] = useState<string | null>(null);

  // Add Patient Modal State
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [patientIdInput, setPatientIdInput] = useState<string>('');
  const [isAssigning, setIsAssigning] = useState<boolean>(false);
  const [assignError, setAssignError] = useState<string | null>(null);
  const [assignSuccess, setAssignSuccess] = useState<string | null>(null);

  // Copy ID Feedback
  const [copiedId, setCopiedId] = useState<boolean>(false);

  const loadPatients = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await doctorApi.getAssignedPatients({
        search: searchQuery.trim() || undefined,
        risk_filter: riskFilter === 'ALL' ? undefined : riskFilter,
        sort_by: sortBy,
      });
      setPatients(res.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load assigned patient directory.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadPatients();
    }, 200);

    return () => clearTimeout(timer);
  }, [searchQuery, riskFilter, sortBy]);

  const handleCopyDoctorId = () => {
    const idToCopy = user?.doctor_profile_id || user?.id || '';
    if (idToCopy) {
      navigator.clipboard.writeText(idToCopy);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  const handleAssignPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanId = patientIdInput.trim();
    if (!cleanId) {
      setAssignError('Please enter a valid Patient ID.');
      return;
    }

    setIsAssigning(true);
    setAssignError(null);
    setAssignSuccess(null);

    try {
      const res = await assignmentApi.createAssignment({ patient_id: cleanId });
      setAssignSuccess(`Patient ${res.patient_name} successfully assigned.`);
      setPatientIdInput('');
      setShowAddModal(false);
      await loadPatients();
    } catch (err: any) {
      let msg = 'Failed to assign patient. Please verify the Patient ID.';
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

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Title & Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Assigned Patients</h1>
          <p className="text-xs text-slate-400">
            Authorized clinician directory for remote vestibular monitoring and clinical decision support.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Copyable Doctor ID Card */}
          <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
            <Stethoscope className="w-3.5 h-3.5 text-teal-400" />
            <span className="text-slate-400 text-[11px]">Your Doctor ID:</span>
            <span className="font-mono text-teal-300 font-bold text-[11px] max-w-[120px] truncate">
              {user?.doctor_profile_id || user?.id}
            </span>
            <button
              onClick={handleCopyDoctorId}
              title="Copy Doctor ID for patients to connect"
              className="text-slate-400 hover:text-white transition p-1"
            >
              {copiedId ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
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
            <span>+ Add New Patient</span>
          </Button>
        </div>
      </div>

      {/* Assignment Success Alert */}
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

      {/* Search & Filter Controls */}
      <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3 shadow-lg">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search Box */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search assigned patient by name or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 transition"
            />
          </div>

          {/* Sort Dropdown */}
          <div className="flex items-center gap-2 shrink-0">
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
            >
              <option value="recent">Sort by: Recent Assignment</option>
              <option value="risk_high_to_low">Sort by: Risk (High to Low)</option>
              <option value="name">Sort by: Patient Name (A-Z)</option>
            </select>
          </div>
        </div>

        {/* Risk Filter Buttons */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/60">
          <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1 mr-1">
            <Filter className="w-3 h-3" />
            Risk Filter:
          </span>
          {(['ALL', 'HIGH', 'MEDIUM', 'LOW', 'UNASSESSED'] as const).map((tier) => (
            <button
              key={tier}
              onClick={() => setRiskFilter(tier)}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                riskFilter === tier
                  ? tier === 'HIGH'
                    ? 'bg-rose-950 text-rose-300 border border-rose-700'
                    : tier === 'MEDIUM'
                    ? 'bg-amber-950 text-amber-300 border border-amber-700'
                    : tier === 'LOW'
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    : 'bg-teal-600 text-white shadow'
                  : 'bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Patient Directory List */}
      {isLoading ? (
        <div className="py-16 text-center">
          <LoadingSpinner size="md" label="Loading authorized patients..." />
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/30 border border-rose-800/50 rounded-xl text-xs text-rose-300">
          {error}
        </div>
      ) : patients.length === 0 ? (
        <div className="p-12 text-center bg-slate-950/60 border border-slate-800 rounded-2xl space-y-4">
          <Users className="w-10 h-10 text-slate-600 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white">No patients assigned yet</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Add patients to your clinical monitoring queue using their unique Patient ID.
            </p>
          </div>
          <Button
            size="sm"
            onClick={() => {
              setShowAddModal(true);
              setAssignError(null);
            }}
            className="gap-1.5 text-xs"
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>+ Add New Patient</span>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {patients.map((p) => (
            <div
              key={p.patient_id}
              className="p-5 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-4 hover:border-slate-700 transition flex flex-col justify-between shadow-lg"
            >
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-base font-bold text-white tracking-tight">{p.full_name}</h3>
                    <p className="text-xs text-slate-400">{p.email}</p>
                    <p className="text-[10px] font-mono text-slate-500 pt-0.5 truncate">ID: {p.patient_id}</p>
                  </div>
                  {p.latest_risk_level ? (
                    <span
                      className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider ${
                        p.latest_risk_level === 'HIGH'
                          ? 'bg-rose-950 text-rose-300 border border-rose-700'
                          : p.latest_risk_level === 'MEDIUM'
                          ? 'bg-amber-950 text-amber-300 border border-amber-700'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                      }`}
                    >
                      {p.latest_risk_level}
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-slate-900 text-slate-400 border border-slate-800">
                      Not Assessed
                    </span>
                  )}
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2 p-3 bg-slate-900/60 rounded-xl border border-slate-800/80 text-[11px]">
                  <div>
                    <span className="text-slate-500 block">Latest Dizziness</span>
                    <strong className="text-slate-200">
                      {p.latest_health_check_dizziness !== null && p.latest_health_check_dizziness !== undefined
                        ? `${p.latest_health_check_dizziness} / 10`
                        : 'No log'}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Risk Score</span>
                    <strong className="text-teal-300 font-mono">
                      {p.latest_risk_score !== null && p.latest_risk_score !== undefined
                        ? `${p.latest_risk_score.toFixed(2)}`
                        : '—'}
                    </strong>
                  </div>
                  <div className="col-span-2 pt-1 border-t border-slate-800/60 flex items-center justify-between text-slate-400 text-[10px]">
                    <span>Total Logs: {p.total_health_checks}</span>
                    <span>DOB: {p.date_of_birth}</span>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <Link to={`/doctor/patients/${p.patient_id}`} className="block pt-1">
                <Button size="sm" variant="outline" className="w-full text-xs gap-1.5 justify-center">
                  <span>Open Patient Record</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Add Patient Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
          <form
            onSubmit={handleAssignPatient}
            className="max-w-md w-full p-6 bg-slate-950 border border-teal-800 rounded-2xl space-y-4 shadow-2xl"
          >
            <div className="space-y-1">
              <h3 className="text-base font-bold text-white">Add Patient</h3>
              <p className="text-xs text-slate-300">
                Enter the Patient ID to create an assignment.
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
                Patient ID
              </label>
              <input
                type="text"
                value={patientIdInput}
                onChange={(e) => setPatientIdInput(e.target.value)}
                placeholder="e.g. 34916d35-5368-47dc-8953-ceb739e93acc"
                className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-teal-500"
                required
              />
              <p className="text-[11px] text-slate-500 mt-1">
                The Patient ID can be found on the patient's dashboard or profile.
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
                Assign Patient
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
