import { apiClient } from '@/api/client';
import { HealthStatus } from '@/types';

export const healthService = {
  async checkHealth(): Promise<HealthStatus> {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },
};

