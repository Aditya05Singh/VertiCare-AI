import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { FormFieldWrapper } from '@/components/forms/FormFieldWrapper';
import { Stethoscope, AlertCircle, CheckCircle2 } from 'lucide-react';

const doctorRegisterSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  specialization: z.string().min(2, 'Specialization is required'),
  license_identifier: z.string().min(3, 'Medical license identifier is required'),
});

type DoctorRegisterFormData = z.infer<typeof doctorRegisterSchema>;

export const DoctorRegister: React.FC = () => {
  const { registerDoctor, login } = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<DoctorRegisterFormData>({
    resolver: zodResolver(doctorRegisterSchema),
    defaultValues: {
      specialization: 'Otolaryngology / Neurotology',
    },
  });

  const onSubmit = async (data: DoctorRegisterFormData) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      await registerDoctor(data);
      setIsSuccess(true);
      // Auto login after registration
      await login({ email: data.email, password: data.password });
      setTimeout(() => {
        navigate('/doctor/dashboard');
      }, 1000);
    } catch (error: any) {
      let message = 'Registration failed. Please check your professional details.';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          message = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          message = detail
            .map((item: any) => item.msg || item.message || JSON.stringify(item))
            .join(', ');
        }
      }
      setFormError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto my-6 space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-xl bg-cyan-600/20 border border-cyan-500/30 text-cyan-400 flex items-center justify-center mx-auto">
          <Stethoscope className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Clinician Account Registration</h1>
        <p className="text-xs text-slate-400">
          Create your verified doctor profile for patient triage and clinical decision support reviews.
        </p>
      </div>

      {formError && (
        <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-lg text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{formError}</span>
        </div>
      )}

      {isSuccess && (
        <div className="p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-lg text-xs text-emerald-300 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Doctor profile registered! Redirecting to clinician portal...</span>
        </div>
      )}

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="p-6 bg-slate-950/60 border border-slate-800 rounded-xl space-y-4 shadow-xl"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FormFieldWrapper label="First Name" error={errors.first_name?.message} required>
            <input
              type="text"
              placeholder="Marcus"
              {...register('first_name')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
          </FormFieldWrapper>

          <FormFieldWrapper label="Last Name" error={errors.last_name?.message} required>
            <input
              type="text"
              placeholder="Welby"
              {...register('last_name')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
          </FormFieldWrapper>
        </div>

        <FormFieldWrapper label="Professional Email" error={errors.email?.message} required>
          <input
            type="email"
            placeholder="dr.welby@clinic.org"
            {...register('email')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          />
        </FormFieldWrapper>

        <FormFieldWrapper label="Password" error={errors.password?.message} helperText="Minimum 8 characters" required>
          <input
            type="password"
            placeholder="••••••••"
            {...register('password')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          />
        </FormFieldWrapper>

        <FormFieldWrapper label="Clinical Specialization" error={errors.specialization?.message} required>
          <input
            type="text"
            placeholder="e.g. Otolaryngology, Neurotology, Vestibular Neurology"
            {...register('specialization')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          />
        </FormFieldWrapper>

        <FormFieldWrapper label="Medical License / Identifier" error={errors.license_identifier?.message} required>
          <input
            type="text"
            placeholder="e.g. MED-LIC-2026-883"
            {...register('license_identifier')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          />
        </FormFieldWrapper>

        <Button type="submit" className="w-full bg-cyan-600 hover:bg-cyan-700 focus:ring-cyan-500" isLoading={isSubmitting}>
          Create Doctor Account
        </Button>
      </form>

      <p className="text-center text-xs text-slate-400">
        Already registered?{' '}
        <Link to="/login" className="text-cyan-400 font-medium hover:underline">
          Sign in here
        </Link>
      </p>
    </div>
  );
};

