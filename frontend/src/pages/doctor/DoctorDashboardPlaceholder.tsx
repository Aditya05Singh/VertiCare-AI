import React from 'react';
import { EmptyState } from '@/components/common/EmptyState';
import { Stethoscope } from 'lucide-react';

export const DoctorDashboardPlaceholder: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Doctor Decision Support Portal</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Patient triage queue, longitudinal symptom trends, and clinical decision support reviews.
        </p>
      </div>

      <EmptyState
        icon={<Stethoscope className="w-10 h-10 text-cyan-400" />}
        title="Doctor Portal Scaffolding Ready"
        description="Patient risk triage queue, longitudinal charts, clinical note authoring, and emergency escalation workflows will be implemented in subsequent phases."
      />
    </div>
  );
};

