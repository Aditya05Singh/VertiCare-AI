import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { UserRole } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { ShieldAlert } from 'lucide-react';

interface RoleProtectedRouteProps {
  allowedRole: UserRole;
  children: React.ReactNode;
}

export const RoleProtectedRoute: React.FC<RoleProtectedRouteProps> = ({
  allowedRole,
  children,
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" label="Checking role permissions..." />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (user.role !== allowedRole) {
    return (
      <div className="max-w-md mx-auto my-12">
        <EmptyState
          icon={<ShieldAlert className="w-10 h-10 text-rose-400" />}
          title="Access Restricted"
          description={`This area is restricted to ${allowedRole} accounts. Your account is registered as ${user.role}.`}
        />
      </div>
    );
  }

  return <>{children}</>;
};

