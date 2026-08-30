import { useQuery } from '@tanstack/react-query';
import { healthService } from '@/services/healthService';

export function useHealth() {
  return useQuery({
    queryKey: ['system-health'],
    queryFn: () => healthService.checkHealth(),
    retry: 1,
    staleTime: 30000,
  });
}

