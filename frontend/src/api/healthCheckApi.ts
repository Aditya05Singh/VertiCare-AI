import { apiClient } from '@/api/client';
import {
  DailyHealthCheck,
  DailyHealthCheckInput,
  DailyHealthCheckListResponse,
  DailyHealthTrendResponse,
} from '@/types';

export const healthCheckApi = {
  async createOrUpdateHealthCheck(data: DailyHealthCheckInput): Promise<DailyHealthCheck> {
    const response = await apiClient.post<DailyHealthCheck>('/health-checks', data);
    return response.data;
  },

  async getHistory(limit = 30, offset = 0): Promise<DailyHealthCheckListResponse> {
    const response = await apiClient.get<DailyHealthCheckListResponse>('/health-checks', {
      params: { limit, offset },
    });
    return response.data;
  },

  async getTrends(days = 30): Promise<DailyHealthTrendResponse> {
    const response = await apiClient.get<DailyHealthTrendResponse>('/health-checks/trends', {
      params: { days },
    });
    return response.data;
  },

  async getHealthCheckById(id: string): Promise<DailyHealthCheck> {
    const response = await apiClient.get<DailyHealthCheck>(`/health-checks/${id}`);
    return response.data;
  },
};

