import React from 'react';
import { AlertCircle } from 'lucide-react';
import { MEDICAL_DISCLAIMER } from '@/constants';

export const DisclaimerBanner: React.FC = () => {
  return (
    <div className="bg-amber-950/40 border-b border-amber-800/50 px-4 py-2 text-xs text-amber-200/90 flex items-center justify-center gap-2">
      <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
      <span className="text-center font-medium tracking-wide">
        {MEDICAL_DISCLAIMER}
      </span>
    </div>
  );
};

