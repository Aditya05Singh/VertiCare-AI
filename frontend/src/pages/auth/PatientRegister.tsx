import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { FormFieldWrapper } from '@/components/forms/FormFieldWrapper';
import { UserCheck, AlertCircle, CheckCircle2 } from 'lucide-react';

const patientRegisterSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum(['MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY']),
  emergency_contact_name: z.string().optional(),
  emergency_contact_phone: z.string().optional(),
  medical_history: z.string().optional(),
});

type PatientRegisterFormData = z.infer<typeof patientRegisterSchema>;

export const PatientRegister: React.FC = () => {
  const { registerPatient, login } = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PatientRegisterFormData>({
    resolver: zodResolver(patientRegisterSchema),
    defaultValues: {
      gender: 'PREFER_NOT_TO_SAY',
    },
  });

  const onSubmit = async (data: PatientRegisterFormData) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      await registerPatient(data);
      setIsSuccess(true);
      // Auto login after registration
      await login({ email: data.email, password: data.password });
      setTimeout(() => {
        navigate('/patient/dashboard');
      }, 1000);
    } catch (error: any) {
      let message = 'Registration failed. Please check your information.';
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
        <div className="w-12 h-12 rounded-xl bg-teal-600/20 border border-teal-500/30 text-teal-400 flex items-center justify-center mx-auto">
          <UserCheck className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Patient Account Registration</h1>
        <p className="text-xs text-slate-400">
          Create your patient profile for vertigo symptom tracking and screening.
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
          <span>Registration successful! Redirecting to your dashboard...</span>
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
              placeholder="Jane"
              {...register('first_name')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </FormFieldWrapper>

          <FormFieldWrapper label="Last Name" error={errors.last_name?.message} required>
            <input
              type="text"
              placeholder="Doe"
              {...register('last_name')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </FormFieldWrapper>
        </div>

        <FormFieldWrapper label="Email Address" error={errors.email?.message} required>
          <input
            type="email"
            placeholder="jane.doe@example.com"
            {...register('email')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
          />
        </FormFieldWrapper>

        <FormFieldWrapper label="Password" error={errors.password?.message} helperText="Minimum 8 characters" required>
          <input
            type="password"
            placeholder="••••••••"
            {...register('password')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
          />
        </FormFieldWrapper>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FormFieldWrapper label="Date of Birth" error={errors.date_of_birth?.message} required>
            <input
              type="date"
              {...register('date_of_birth')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </FormFieldWrapper>

          <FormFieldWrapper label="Gender" error={errors.gender?.message} required>
            <select
              {...register('gender')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            >
              <option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
              <option value="FEMALE">Female</option>
              <option value="MALE">Male</option>
              <option value="OTHER">Other</option>
            </select>
          </FormFieldWrapper>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FormFieldWrapper label="Emergency Contact Name" error={errors.emergency_contact_name?.message}>
            <input
              type="text"
              placeholder="Contact Person"
              {...register('emergency_contact_name')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </FormFieldWrapper>

          <FormFieldWrapper label="Emergency Contact Phone" error={errors.emergency_contact_phone?.message}>
            <input
              type="tel"
              placeholder="+1-555-0100"
              {...register('emergency_contact_phone')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </FormFieldWrapper>
        </div>

        <FormFieldWrapper label="Relevant Medical History (Optional)" error={errors.medical_history?.message}>
          <textarea
            rows={2}
            placeholder="e.g. Previous vestibular episodes, migraine history, ear surgeries..."
            {...register('medical_history')}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
          />
        </FormFieldWrapper>

        <Button type="submit" className="w-full" isLoading={isSubmitting}>
          Create Patient Account
        </Button>
      </form>

      <p className="text-center text-xs text-slate-400">
        Already have an account?{' '}
        <Link to="/login" className="text-teal-400 font-medium hover:underline">
          Sign in here
        </Link>
      </p>
    </div>
  );
};

