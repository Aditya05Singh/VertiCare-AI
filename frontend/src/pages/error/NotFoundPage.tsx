import React from 'react';
import { Link } from 'react-router-dom';
import { EmptyState } from '@/components/common/EmptyState';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="max-w-md mx-auto my-12">
      <EmptyState
        icon={<AlertCircle className="w-10 h-10 text-amber-400" />}
        title="404 — Page Not Found"
        description="The requested page route does not exist in the VertiCare AI application."
      />
      <div className="text-center mt-4">
        <Link to="/">
          <Button variant="outline" size="sm">
            Return to Overview
          </Button>
        </Link>
      </div>
    </div>
  );
};

