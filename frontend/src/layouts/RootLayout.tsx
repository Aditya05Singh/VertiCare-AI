import React from 'react';
import { Outlet } from 'react-router-dom';
import { AppHeader } from '@/components/layout/AppHeader';
import { Sidebar } from '@/components/layout/Sidebar';
import { DisclaimerBanner } from '@/components/layout/DisclaimerBanner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export const RootLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100">
      <DisclaimerBanner />
      <AppHeader />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
};

