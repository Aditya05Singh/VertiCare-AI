import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { FormFieldWrapper } from '@/components/forms/FormFieldWrapper';
import { Lock, UserCheck, Stethoscope, AlertCircle } from 'lucide-react';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [authError, setAuthError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const fillCredentials = (email: string, pass: string) => {
    setValue('email', email, { shouldValidate: true });
    setValue('password', pass, { shouldValidate: true });
  };

  const onSubmit = async (data: LoginFormData) => {
    setAuthError(null);
    setIsSubmitting(true);
    try {
      const user = await login(data);
      // Redirect based on role or return location
      const from = (location.state as any)?.from?.pathname;
      if (from) {
        navigate(from, { replace: true });
      } else if (user.role === 'PATIENT') {
        navigate('/patient/dashboard');
      } else if (user.role === 'DOCTOR') {
        navigate('/doctor/dashboard');
      } else {
        navigate('/');
      }
    } catch (error: any) {
      const message =
        error.response?.data?.detail || 'Authentication failed. Please check your credentials.';
      setAuthError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-8 space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-xl bg-teal-600/20 border border-teal-500/30 text-teal-400 flex items-center justify-center mx-auto">
          <Lock className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Sign In to VertiCare AI</h1>
        <p className="text-xs text-slate-400">
          Access your clinical decision support portal or patient monitoring dashboard.
        </p>
      </div>

      {/* One-Click Demo Credentials */}
      <div className="p-4 bg-slate-950/70 border border-teal-800/40 rounded-xl space-y-2.5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold uppercase tracking-wider text-teal-400 flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5" />
            <span>One-Click Demo Accounts</span>
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Click to Auto-fill</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <button
            type="button"
            onClick={() => fillCredentials('doctor@verticare.org', 'Doctor123!')}
            className="p-3 text-left bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/60 rounded-lg transition-all group"
          >
            <div className="flex items-center gap-1.5 text-cyan-400 font-semibold text-xs">
              <Stethoscope className="w-3.5 h-3.5" />
              <span>Clinician / Doctor</span>
            </div>
            <p className="text-[11px] font-mono text-slate-300 mt-1">doctor@verticare.org</p>
            <p className="text-[10px] text-slate-500 font-mono">Doctor123!</p>
          </button>

          <button
            type="button"
            onClick={() => fillCredentials('demo@verticare.org', 'Password123!')}
            className="p-3 text-left bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-teal-500/60 rounded-lg transition-all group"
          >
            <div className="flex items-center gap-1.5 text-teal-400 font-semibold text-xs">
              <UserCheck className="w-3.5 h-3.5" />
              <span>Patient Portal</span>
            </div>
            <p className="text-[11px] font-mono text-slate-300 mt-1">demo@verticare.org</p>
            <p className="text-[10px] text-slate-500 font-mono">Password123!</p>
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="p-6 bg-slate-950/60 border border-slate-800 rounded-xl space-y-4 shadow-xl">
        <FormFieldWrapper label="Email Address" error={errors.email?.message} required>
          <input
            type="email"
            placeholder="name@example.com"
            {...register('email')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
          />
        </FormFieldWrapper>

        <FormFieldWrapper label="Password" error={errors.password?.message} required>
          <input
            type="password"
            placeholder="••••••••"
            {...register('password')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
          />
        </FormFieldWrapper>

        <Button type="submit" className="w-full" isLoading={isSubmitting}>
          Sign In
        </Button>
      </form>

      <div className="p-4 bg-slate-950/30 border border-slate-800 rounded-xl text-center space-y-3">
        <p className="text-xs text-slate-400">New to VertiCare AI? Select account type:</p>
        <div className="grid grid-cols-2 gap-3">
          <Link to="/register/patient">
            <Button variant="outline" size="sm" className="w-full gap-2">
              <UserCheck className="w-4 h-4 text-teal-400" />
              Patient Register
            </Button>
          </Link>
          <Link to="/register/doctor">
            <Button variant="outline" size="sm" className="w-full gap-2">
              <Stethoscope className="w-4 h-4 text-cyan-400" />
              Doctor Register
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

