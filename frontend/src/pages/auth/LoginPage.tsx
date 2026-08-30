import React from 'react';
import { Link } from 'react-router-dom';
import { EmptyState } from '@/components/common/EmptyState';
import { Lock } from 'lucide-react';

export const LoginPage: React.FC = () => {
  return (
    <div className="max-w-md mx-auto my-12">
      <EmptyState
        icon={<Lock className="w-8 h-8 text-teal-400" />}
        title="Authentication Portal Placeholder"
        description="JWT authentication, login forms, and credential verification will be activated in Step 3."
      />
      <div className="text-center mt-4">
        <Link to="/" className="text-xs text-teal-400 hover:underline">
          &larr; Return to Overview
        </Link>
      </div>
    </div>
  );
};

