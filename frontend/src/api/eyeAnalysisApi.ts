import { apiClient } from '@/api/client';
import { EyeAnalysisSession, EyeMovementFeaturesSubmit } from '@/types';

export const eyeAnalysisApi = {
  async createSession(): Promise<EyeAnalysisSession> {
    const response = await apiClient.post<EyeAnalysisSession>('/eye-analysis/sessions');
    return response.data;
  },

  async saveFeatures(
    sessionId: string,
    payload: EyeMovementFeaturesSubmit
  ): Promise<EyeAnalysisSession> {
    const response = await apiClient.post<EyeAnalysisSession>(
      `/eye-analysis/sessions/${sessionId}/features`,
      payload
    );
    return response.data;
  },

  async getSession(sessionId: string): Promise<EyeAnalysisSession> {
    const response = await apiClient.get<EyeAnalysisSession>(
      `/eye-analysis/sessions/${sessionId}`
    );
    return response.data;
  },
};

