import { apiClient } from '@/api/client';
import { RiskAssessment, RiskAssessmentList } from '@/types';

export const riskApi = {
  async calculateRisk(data?: {
    health_check_id?: string;
    questionnaire_session_id?: string;
    eye_analysis_session_id?: string;
  }): Promise<RiskAssessment> {
    const response = await apiClient.post<RiskAssessment>('/risk-assessment', data || {});
    return response.data;
  },

  async getLatestAssessment(): Promise<RiskAssessment | null> {
    const response = await apiClient.get<RiskAssessmentList>('/risk-assessment/history?limit=1');
    if (response.data.items && response.data.items.length > 0) {
      return response.data.items[0];
    }
    return null;
  },

  async getAssessment(id: string): Promise<RiskAssessment> {
    const response = await apiClient.get<RiskAssessment>(`/risk-assessment/${id}`);
    return response.data;
  },

  async getHistory(limit: number = 10, offset: number = 0): Promise<RiskAssessmentList> {
    const response = await apiClient.get<RiskAssessmentList>(
      `/risk-assessment/history?limit=${limit}&offset=${offset}`
    );
    return response.data;
  },
};

