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
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

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

      {authError && (
        <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-lg text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{authError}</span>
        </div>
      )}

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

