import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  UserCheck,
  ClipboardList,
  Eye,
  FileText,
  AlertTriangle,
  Shield,
  PhoneCall,
  Users,
  Stethoscope,
  ShieldAlert,
  UserPlus,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';

export const Sidebar: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const isDoctor = user?.role === 'DOCTOR';
  const isPatient = user?.role === 'PATIENT';

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950/50 p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-6">
        {/* Core Navigation */}
        <div>
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500 mb-2">
            {isDoctor ? 'Clinician Navigation' : 'Patient Navigation'}
          </p>
          <nav className="space-y-1">
            <NavLink
              to="/"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                )
              }
            >
              <LayoutDashboard className="w-4 h-4" />
              Platform Overview
            </NavLink>

            {isDoctor ? (
              <>
                {/* Doctor Dashboard */}
                <NavLink
                  to="/doctor/dashboard"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <Stethoscope className="w-4 h-4 text-teal-400" />
                  Doctor Dashboard
                </NavLink>

                {/* Assigned Patients Directory */}
                <NavLink
                  to="/doctor/patients"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <Users className="w-4 h-4 text-teal-400" />
                  Assigned Patients
                </NavLink>

                {/* Emergency Alerts & Triage */}
                <NavLink
                  to="/doctor/emergencies"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-rose-600/10 text-rose-400 border border-rose-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  Emergency Alerts
                </NavLink>
              </>
            ) : (
              <>
                {/* Patient Dashboard */}
                <NavLink
                  to="/patient/dashboard"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <UserCheck className="w-4 h-4 text-teal-400" />
                  Patient Dashboard
                </NavLink>

                {/* Assigned Doctor */}
                <NavLink
                  to="/patient/assigned-doctor"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <Stethoscope className="w-4 h-4 text-teal-400" />
                  Assigned Doctor
                </NavLink>

                {/* Daily Health Check */}
                <NavLink
                  to="/patient/health-check"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <Activity className="w-4 h-4 text-teal-400" />
                  Daily Health Check
                </NavLink>

                {/* Adaptive Questionnaire */}
                <NavLink
                  to="/patient/questionnaire"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <ClipboardList className="w-4 h-4 text-teal-400" />
                  Adaptive Questionnaire
                </NavLink>

                {/* Eye Movement Screening */}
                <NavLink
                  to="/patient/eye-analysis"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-teal-600/10 text-teal-400 border border-teal-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <Eye className="w-4 h-4 text-teal-400" />
                  Eye Movement Screening
                </NavLink>

                {/* Emergency Support */}
                <NavLink
                  to="/patient/emergency"
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-rose-600/10 text-rose-400 border border-rose-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    )
                  }
                >
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  Emergency Support
                </NavLink>
              </>
            )}
          </nav>
        </div>

        {/* Active Session Info */}
        {isAuthenticated && user && (
          <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs space-y-1.5">
            <div className="flex items-center gap-1.5 text-slate-300 font-medium">
              <Shield className="w-3.5 h-3.5 text-teal-400" />
              <span>Role Permissions</span>
            </div>
            <p className="text-[11px] text-slate-400">
              Authenticated as <strong className="text-white">{user.role}</strong>
            </p>
          </div>
        )}
      </div>

      <div className="p-3 rounded-lg border border-slate-800/80 bg-slate-900/30 text-[11px] text-slate-500">
        <div className="flex items-center gap-1.5 text-slate-400 font-medium mb-1">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          <span>Academic Prototype</span>
        </div>
        VertiCare AI Clinical Portal
      </div>
    </aside>
  );
};
