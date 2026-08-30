import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { healthCheckApi } from '@/api/healthCheckApi';
import { DailyHealthCheckInput } from '@/types';

export function useHealthCheckHistory(limit = 30, offset = 0) {
  return useQuery({
    queryKey: ['health-checks', 'history', limit, offset],
    queryFn: () => healthCheckApi.getHistory(limit, offset),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useHealthTrends(days = 30) {
  return useQuery({
    queryKey: ['health-checks', 'trends', days],
    queryFn: () => healthCheckApi.getTrends(days),
    staleTime: 1000 * 60 * 2,
  });
}

export function useSubmitHealthCheck() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DailyHealthCheckInput) => healthCheckApi.createOrUpdateHealthCheck(data),
    onSuccess: () => {
      // Invalidate relevant queries so dashboard and history reload automatically
      queryClient.invalidateQueries({ queryKey: ['health-checks'] });
    },
  });
}

