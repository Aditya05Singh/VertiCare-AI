import React from 'react';
import { cn } from '@/lib/utils';

interface FormFieldWrapperProps {
  label: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}

export const FormFieldWrapper: React.FC<FormFieldWrapperProps> = ({
  label,
  error,
  helperText,
  required,
  children,
  className,
}) => {
  return (
    <div className={cn('space-y-1.5', className)}>
      <label className="block text-xs font-medium text-slate-300">
        {label} {required && <span className="text-rose-400">*</span>}
      </label>
      {children}
      {error ? (
        <p className="text-xs text-rose-400">{error}</p>
      ) : helperText ? (
        <p className="text-xs text-slate-500">{helperText}</p>
      ) : null}
    </div>
  );
};

