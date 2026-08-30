import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, LogOut, User, ShieldCheck, Stethoscope, UserCheck } from 'lucide-react';
import { useHealth } from '@/hooks/useHealth';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';

export const AppHeader: React.FC = () => {
  const { data: health, isLoading: isHealthLoading } = useHealth();
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg text-white">
          <div className="w-8 h-8 rounded-lg bg-teal-600/20 border border-teal-500/30 flex items-center justify-center text-teal-400">
            <Activity className="w-5 h-5" />
          </div>
          <span>VertiCare <span className="text-teal-400 font-semibold">AI</span></span>
        </Link>
        <span className="text-[11px] font-medium bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
          Academic Prototype
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs">
        {/* Backend health status pill */}
        <div className="hidden md:flex items-center gap-1.5 text-slate-400">
          <span
            className={`w-2 h-2 rounded-full ${
              isHealthLoading
                ? 'bg-amber-400 animate-pulse'
                : health?.status === 'ok'
                ? 'bg-emerald-400'
                : 'bg-rose-400'
            }`}
          />
          <span>
            API: {isHealthLoading ? 'Connecting...' : health?.status === 'ok' ? 'Online' : 'Offline'}
          </span>
        </div>

        {isAuthenticated && user ? (
          <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-slate-300">
                {user.role === 'DOCTOR' ? (
                  <Stethoscope className="w-4 h-4 text-cyan-400" />
                ) : (
                  <UserCheck className="w-4 h-4 text-teal-400" />
                )}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-semibold text-slate-200 leading-tight">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  {user.role}
                </p>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-slate-400 hover:text-rose-400 gap-1.5 px-2"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Sign Out</span>
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link to="/login">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link to="/register/patient">
              <Button variant="primary" size="sm">
                Register
              </Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
