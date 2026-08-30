import React, { useEffect, useState } from 'react';
import { NavLink, Outlet, useParams, Link } from 'react-router-dom';
import { doctorApi } from '@/api/doctorApi';
import { DoctorPatientDossier } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { cn } from '@/lib/utils';
import {
  User,
  Activity,
  ClipboardList,
  Eye,
  Sparkles,
  FileEdit,
  FileText,
  ArrowLeft,
  AlertCircle,
} from 'lucide-react';

export const DoctorPatientLayout: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [dossier, setDossier] = useState<DoctorPatientDossier | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);

  useEffect(() => {
    if (!id) return;
    async function loadPatient() {
      setIsLoading(true);
      setError(null);
      setErrorStatus(null);
      try {
        const data = await doctorApi.getPatientDossier(id!);
        setDossier(data);
      } catch (err: any) {
        setErrorStatus(err.response?.status || 500);
        let msg = 'Patient record not found or not assigned to your clinician account.';
        if (err.response?.data?.detail) {
          const detail = err.response.data.detail;
          if (typeof detail === 'string') msg = detail;
          else if (Array.isArray(detail)) msg = detail.map((d: any) => d.msg).join(', ');
        } else if (err.message) {
          msg = err.message;
        }
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    }
    loadPatient();
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading patient monitoring dossier..." />
      </div>
    );
  }

  if (error || !dossier) {
    const isForbiddenOrNotFound = errorStatus === 404 || errorStatus === 403;
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-rose-950/60 border border-rose-800/60 text-rose-400 flex items-center justify-center mx-auto">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">
          {isForbiddenOrNotFound ? 'Access Denied or Patient Not Found' : 'Error Loading Patient Dossier'}
        </h2>
        <p className="text-xs text-slate-400">
          {error || 'You are not authorized to view this patient record.'}
        </p>
        <Link
          to="/doctor/patients"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 text-slate-200 text-xs font-semibold hover:bg-slate-700 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Assigned Patient List</span>
        </Link>
      </div>
    );
  }

  const latestRisk = dossier.latest_risk_assessment;

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Back button & Patient Header */}
      <div className="space-y-3">
        <Link
          to="/doctor/patients"
          className="inline-flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-teal-400 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Assigned Patients</span>
        </Link>

        <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-teal-950/30 border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-teal-950/80 border border-teal-700/60 flex items-center justify-center text-teal-400 font-bold text-lg">
              {dossier.full_name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                  {dossier.full_name}
                </h1>
                {latestRisk ? (
                  <span
                    className={cn(
                      'px-2.5 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider',
                      latestRisk.risk_level === 'HIGH'
                        ? 'bg-rose-950 text-rose-300 border border-rose-700'
                        : latestRisk.risk_level === 'MEDIUM'
                        ? 'bg-amber-950 text-amber-300 border border-amber-700'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    )}
                  >
                    {latestRisk.risk_level} Risk ({latestRisk.risk_score.toFixed(2)})
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-slate-800 text-slate-400">
                    Not Assessed
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400">
                {dossier.email} • DOB: {dossier.date_of_birth} • Gender: {dossier.gender}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="font-mono bg-slate-950/80 px-2.5 py-1 rounded-lg border border-slate-800">
              ID: {dossier.patient_id.slice(0, 8)}...
            </span>
          </div>
        </div>
      </div>

      {/* Clinician Sub-Navigation Tabs */}
      <div className="border-b border-slate-800 overflow-x-auto">
        <nav className="flex space-x-2 shrink-0">
          <NavLink
            to={`/doctor/patients/${id}`}
            end
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-semibold transition-colors whitespace-nowrap',
                isActive
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              )
            }
          >
            <User className="w-3.5 h-3.5" />
            <span>Overview</span>
          </NavLink>

          <NavLink
            to={`/doctor/patients/${id}/health`}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-semibold transition-colors whitespace-nowrap',
                isActive
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              )
            }
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Health History</span>
          </NavLink>

          <NavLink
            to={`/doctor/patients/${id}/questionnaire`}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-semibold transition-colors whitespace-nowrap',
                isActive
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              )
            }
          >
            <ClipboardList className="w-3.5 h-3.5" />
            <span>Questionnaire</span>
          </NavLink>

          <NavLink
            to={`/doctor/patients/${id}/eye-analysis`}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-semibold transition-colors whitespace-nowrap',
                isActive
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              )
            }
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Eye Analysis</span>
          </NavLink>

          <NavLink
            to={`/doctor/patients/${id}/risk`}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-semibold transition-colors whitespace-nowrap',
                isActive
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              )
            }
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Risk History</span>
          </NavLink>

          <NavLink
            to={`/doctor/patients/${id}/notes`}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-semibold transition-colors whitespace-nowrap',
                isActive
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              )
            }
          >
            <FileEdit className="w-3.5 h-3.5" />
            <span>Clinical Notes</span>
          </NavLink>

          <NavLink
            to={`/doctor/patients/${id}/reports`}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-semibold transition-colors whitespace-nowrap',
                isActive
                  ? 'border-teal-500 text-teal-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              )
            }
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Report Summary</span>
          </NavLink>
        </nav>
      </div>

      {/* Active Tab Page Content */}
      <Outlet context={{ dossier, reloadDossier: () => {} }} />
    </div>
  );
};

