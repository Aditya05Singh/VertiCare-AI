import React from 'react';
import { EmptyState } from '@/components/common/EmptyState';
import { UserCheck } from 'lucide-react';

export const PatientDashboardPlaceholder: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Patient Monitoring Portal</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Daily symptom check-in, adaptive questionnaire, and eye movement screening workflows.
        </p>
      </div>

      <EmptyState
        icon={<UserCheck className="w-10 h-10 text-teal-400" />}
        title="Patient Portal Scaffolding Ready"
        description="Daily symptom logger, adaptive questionnaire wizard, webcam eye-tracking, and risk visualization modules will be implemented in subsequent phases."
      />
    </div>
  );
};

