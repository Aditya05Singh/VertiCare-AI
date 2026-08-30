import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useSubmitHealthCheck, useHealthCheckHistory } from '@/hooks/useHealthCheck';
import { Button } from '@/components/ui/button';
import { FormFieldWrapper } from '@/components/forms/FormFieldWrapper';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import {
  Activity,
  CheckCircle2,
  AlertCircle,
  Calendar,
  Clock,
  Droplet,
  Moon,
  Zap,
  Pill,
  FileText,
  ShieldCheck,
} from 'lucide-react';

const COMMON_TRIGGERS = [
  'Sudden head movement',
  'Getting out of bed / lying down',
  'Bright lights / Screens',
  'Stress / Fatigue',
  'Skipping meals / Dehydration',
  'Caffeine / Alcohol',
  'Loud sounds / Noise',
  'Weather / Barometric change',
];

const healthCheckSchema = z.object({
  check_date: z.string().optional(),
  dizziness_severity: z.number().min(0).max(10),
  episode_duration: z.string().min(1, 'Please select duration'),
  imbalance_severity: z.number().min(0).max(10),
  nausea: z.boolean(),
  headache: z.boolean(),
  sleep_hours: z.number().min(0).max(24),
  hydration_level: z.string().min(1, 'Please select hydration'),
  stress_level: z.number().min(0).max(10),
  medication_adherence: z.string().min(1, 'Please select medication status'),
  triggers: z.array(z.string()),
  notes: z.string().max(1000).optional(),
});

type HealthCheckFormData = z.infer<typeof healthCheckSchema>;

export const DailyHealthCheck: React.FC = () => {
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const { data: historyData, isLoading: isHistoryLoading } = useHealthCheckHistory(10, 0);
  const submitMutation = useSubmitHealthCheck();

  const todayStr = new Date().toISOString().split('T')[0];

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors },
  } = useForm<HealthCheckFormData>({
    resolver: zodResolver(healthCheckSchema),
    defaultValues: {
      check_date: todayStr,
      dizziness_severity: 0,
      episode_duration: 'None / Subsided',
      imbalance_severity: 0,
      nausea: false,
      headache: false,
      sleep_hours: 7.5,
      hydration_level: 'Moderate (1-2L)',
      stress_level: 3,
      medication_adherence: 'Taken as prescribed',
      triggers: [],
      notes: '',
    },
  });

  const selectedTriggers = watch('triggers') || [];
  const dizzinessVal = watch('dizziness_severity');
  const imbalanceVal = watch('imbalance_severity');
  const stressVal = watch('stress_level');
  const sleepVal = watch('sleep_hours');

  const toggleTrigger = (trigger: string) => {
    if (selectedTriggers.includes(trigger)) {
      setValue('triggers', selectedTriggers.filter((t) => t !== trigger));
    } else {
      setValue('triggers', [...selectedTriggers, trigger]);
    }
  };

  const onSubmit = async (data: HealthCheckFormData) => {
    setApiError(null);
    setSuccessMessage(null);
    try {
      await submitMutation.mutateAsync(data);
      setSuccessMessage('Your daily health check has been recorded successfully.');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: any) {
      const msg =
        err.response?.data?.detail || 'Failed to submit health check. Please try again.';
      setApiError(msg);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
          <Activity className="w-4 h-4" />
          <span>Patient Monitoring</span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Daily Health Check</h1>
        <p className="text-xs text-slate-400">
          Log your daily vestibular symptoms, sleep, hydration, and triggers. Recording every day helps track recovery patterns.
        </p>
      </div>

      {/* Notifications */}
      {successMessage && (
        <div className="p-4 bg-emerald-950/40 border border-emerald-800/60 rounded-xl text-xs text-emerald-200 flex items-start gap-3 shadow-lg">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-emerald-300">Submission Saved</p>
            <p className="text-emerald-400/90 mt-0.5">{successMessage}</p>
          </div>
        </div>
      )}

      {apiError && (
        <div className="p-4 bg-rose-950/40 border border-rose-800/60 rounded-xl text-xs text-rose-200 flex items-start gap-3 shadow-lg">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-rose-300">Submission Error</p>
            <p className="text-rose-400/90 mt-0.5">{apiError}</p>
          </div>
        </div>
      )}

      {/* Main Check-in Form */}
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="p-6 bg-slate-950/60 border border-slate-800 rounded-xl space-y-6 shadow-xl"
      >
        {/* Section 1: Date & Episode Duration */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-4 border-b border-slate-800/80">
          <FormFieldWrapper label="Check-in Date" error={errors.check_date?.message} required>
            <div className="relative">
              <input
                type="date"
                {...register('check_date')}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              />
            </div>
          </FormFieldWrapper>

          <FormFieldWrapper label="Episode Duration" error={errors.episode_duration?.message} required>
            <select
              {...register('episode_duration')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            >
              <option value="None / Subsided">None / No dizziness today</option>
              <option value="< 1 minute">Brief (&lt; 1 minute, positional)</option>
              <option value="1-20 minutes">Short (1 – 20 minutes)</option>
              <option value="20 mins - 2 hours">Moderate (20 mins – 2 hours)</option>
              <option value="> 2 hours">Prolonged (&gt; 2 hours)</option>
              <option value="Constant / All day">Constant / All day feeling</option>
            </select>
          </FormFieldWrapper>
        </div>

        {/* Section 2: Severity Sliders */}
        <div className="space-y-6 pb-4 border-b border-slate-800/80">
          <h2 className="text-sm font-semibold text-slate-200">Symptom Severity Levels (0 – 10)</h2>

          {/* Dizziness Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <label className="font-medium text-slate-300">
                Dizziness / Spinning Severity:
              </label>
              <span className="px-2 py-0.5 rounded bg-teal-950 text-teal-300 font-bold border border-teal-800">
                {dizzinessVal} / 10
              </span>
            </div>
            <Controller
              name="dizziness_severity"
              control={control}
              render={({ field }) => (
                <input
                  type="range"
                  min={0}
                  max={10}
                  step={1}
                  value={field.value}
                  onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                  className="w-full accent-teal-500 h-2 bg-slate-800 rounded-lg cursor-pointer"
                />
              )}
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0 (None)</span>
              <span>5 (Moderate)</span>
              <span>10 (Severe / Bedbound)</span>
            </div>
          </div>

          {/* Imbalance Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <label className="font-medium text-slate-300">
                Unsteadiness / Imbalance Severity:
              </label>
              <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 font-bold border border-rose-800">
                {imbalanceVal} / 10
              </span>
            </div>
            <Controller
              name="imbalance_severity"
              control={control}
              render={({ field }) => (
                <input
                  type="range"
                  min={0}
                  max={10}
                  step={1}
                  value={field.value}
                  onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                  className="w-full accent-rose-500 h-2 bg-slate-800 rounded-lg cursor-pointer"
                />
              )}
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0 (Steady)</span>
              <span>5 (Need support / wall)</span>
              <span>10 (Cannot stand / walk)</span>
            </div>
          </div>

          {/* Associated Symptoms (Nausea & Headache) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <FormFieldWrapper label="Nausea or Stomach Upset">
              <Controller
                name="nausea"
                control={control}
                render={({ field }) => (
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => field.onChange(false)}
                      className={`px-3 py-2 text-xs font-medium rounded-lg border transition-colors ${
                        !field.value
                          ? 'bg-slate-800 text-white border-teal-500/50'
                          : 'bg-slate-900 text-slate-400 border-slate-700'
                      }`}
                    >
                      No Nausea
                    </button>
                    <button
                      type="button"
                      onClick={() => field.onChange(true)}
                      className={`px-3 py-2 text-xs font-medium rounded-lg border transition-colors ${
                        field.value
                          ? 'bg-amber-950/60 text-amber-300 border-amber-500/50'
                          : 'bg-slate-900 text-slate-400 border-slate-700'
                      }`}
                    >
                      Yes, Nauseous
                    </button>
                  </div>
                )}
              />
            </FormFieldWrapper>

            <FormFieldWrapper label="Headache or Migraine">
              <Controller
                name="headache"
                control={control}
                render={({ field }) => (
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => field.onChange(false)}
                      className={`px-3 py-2 text-xs font-medium rounded-lg border transition-colors ${
                        !field.value
                          ? 'bg-slate-800 text-white border-teal-500/50'
                          : 'bg-slate-900 text-slate-400 border-slate-700'
                      }`}
                    >
                      No Headache
                    </button>
                    <button
                      type="button"
                      onClick={() => field.onChange(true)}
                      className={`px-3 py-2 text-xs font-medium rounded-lg border transition-colors ${
                        field.value
                          ? 'bg-amber-950/60 text-amber-300 border-amber-500/50'
                          : 'bg-slate-900 text-slate-400 border-slate-700'
                      }`}
                    >
                      Yes, Headache
                    </button>
                  </div>
                )}
              />
            </FormFieldWrapper>
          </div>
        </div>

        {/* Section 3: Lifestyle & Adherence */}
        <div className="space-y-4 pb-4 border-b border-slate-800/80">
          <h2 className="text-sm font-semibold text-slate-200">Lifestyle & Wellness Factors</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Sleep Hours */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <label className="font-medium text-slate-300 flex items-center gap-1.5">
                  <Moon className="w-3.5 h-3.5 text-indigo-400" />
                  Sleep Duration:
                </label>
                <span className="text-slate-200 font-semibold">{sleepVal} Hours</span>
              </div>
              <Controller
                name="sleep_hours"
                control={control}
                render={({ field }) => (
                  <input
                    type="range"
                    min={0}
                    max={14}
                    step={0.5}
                    value={field.value}
                    onChange={(e) => field.onChange(parseFloat(e.target.value))}
                    className="w-full accent-indigo-500 h-2 bg-slate-800 rounded-lg cursor-pointer"
                  />
                )}
              />
            </div>

            {/* Stress Level */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <label className="font-medium text-slate-300 flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-amber-400" />
                  Stress Level:
                </label>
                <span className="text-slate-200 font-semibold">{stressVal} / 10</span>
              </div>
              <Controller
                name="stress_level"
                control={control}
                render={({ field }) => (
                  <input
                    type="range"
                    min={0}
                    max={10}
                    step={1}
                    value={field.value}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                    className="w-full accent-amber-500 h-2 bg-slate-800 rounded-lg cursor-pointer"
                  />
                )}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormFieldWrapper label="Hydration Intake" error={errors.hydration_level?.message} required>
              <select
                {...register('hydration_level')}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              >
                <option value="Low (<1L)">Low (&lt; 1 Liter / &lt; 4 glasses)</option>
                <option value="Moderate (1-2L)">Moderate (1 – 2 Liters / 4-8 glasses)</option>
                <option value="Good (2-3L)">Good (2 – 3 Liters / 8-12 glasses)</option>
                <option value="High (>3L)">High (&gt; 3 Liters)</option>
              </select>
            </FormFieldWrapper>

            <FormFieldWrapper label="Medication Adherence" error={errors.medication_adherence?.message} required>
              <select
                {...register('medication_adherence')}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              >
                <option value="Taken as prescribed">Taken as prescribed</option>
                <option value="Missed morning dose">Missed morning dose</option>
                <option value="Missed entire day">Missed entire day</option>
                <option value="No medications prescribed">No medications prescribed / N/A</option>
              </select>
            </FormFieldWrapper>
          </div>
        </div>

        {/* Section 4: Triggers & Notes */}
        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-200">
              Identified Situational Triggers (Select all that apply)
            </label>
            <div className="flex flex-wrap gap-2 pt-1">
              {COMMON_TRIGGERS.map((trigger) => {
                const isSelected = selectedTriggers.includes(trigger);
                return (
                  <button
                    key={trigger}
                    type="button"
                    onClick={() => toggleTrigger(trigger)}
                    className={`px-3 py-1.5 text-xs rounded-full border transition-colors ${
                      isSelected
                        ? 'bg-teal-900/60 border-teal-500 text-teal-200'
                        : 'bg-slate-900/80 border-slate-700 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    {trigger}
                  </button>
                );
              })}
            </div>
          </div>

          <FormFieldWrapper label="Notes & Observations (Optional)" error={errors.notes?.message}>
            <textarea
              rows={2}
              placeholder="e.g. Felt unsteady when turning head left in supermarket, rested for 10 mins..."
              {...register('notes')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </FormFieldWrapper>
        </div>

        {/* Submit */}
        <Button
          type="submit"
          className="w-full sm:w-auto"
          isLoading={submitMutation.isPending}
        >
          Save Daily Health Check
        </Button>
      </form>

      {/* History Log Table */}
      <div className="space-y-3">
        <h2 className="text-base font-bold text-white tracking-tight">Recent Check-in History</h2>

        {isHistoryLoading ? (
          <div className="p-8 text-center bg-slate-950/40 rounded-xl border border-slate-800">
            <LoadingSpinner size="md" label="Loading health check history..." />
          </div>
        ) : !historyData || historyData.items.length === 0 ? (
          <div className="p-6 bg-slate-950/40 rounded-xl border border-slate-800 text-center">
            <EmptyState
              title="No Health Checks Recorded Yet"
              description="Complete your first daily health check above to start tracking your longitudinal progress."
            />
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60 shadow-lg">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-semibold">Date</th>
                  <th className="px-4 py-3 font-semibold">Dizziness</th>
                  <th className="px-4 py-3 font-semibold">Imbalance</th>
                  <th className="px-4 py-3 font-semibold">Duration</th>
                  <th className="px-4 py-3 font-semibold">Sleep / Stress</th>
                  <th className="px-4 py-3 font-semibold">Hydration</th>
                  <th className="px-4 py-3 font-semibold">Triggers</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {historyData.items.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/30 transition-colors">
                    <td className="px-4 py-3 font-medium text-white whitespace-nowrap">
                      {item.check_date}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded font-bold ${
                          item.dizziness_severity > 6
                            ? 'bg-rose-950 text-rose-400 border border-rose-800'
                            : item.dizziness_severity > 3
                            ? 'bg-amber-950 text-amber-400 border border-amber-800'
                            : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        }`}
                      >
                        {item.dizziness_severity} / 10
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-semibold text-slate-200">
                        {item.imbalance_severity} / 10
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                      {item.episode_duration}
                    </td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">
                      {item.sleep_hours}h sleep • {item.stress_level}/10 stress
                    </td>
                    <td className="px-4 py-3 text-slate-400">
                      {item.hydration_level}
                    </td>
                    <td className="px-4 py-3 text-slate-400 max-w-xs truncate">
                      {item.triggers && item.triggers.length > 0
                        ? item.triggers.join(', ')
                        : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

