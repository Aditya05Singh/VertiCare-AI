import React from 'react';
import { Link } from 'react-router-dom';
import { EmptyState } from '@/components/common/EmptyState';
import { UserPlus } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  return (
    <div className="max-w-md mx-auto my-12">
      <EmptyState
        icon={<UserPlus className="w-8 h-8 text-cyan-400" />}
        title="Registration Portal Placeholder"
        description="Patient and Clinician role account registration workflows will be activated in Step 3."
      />
      <div className="text-center mt-4">
        <Link to="/" className="text-xs text-teal-400 hover:underline">
          &larr; Return to Overview
        </Link>
      </div>
    </div>
  );
};

