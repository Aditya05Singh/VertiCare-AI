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

  async uploadVideo(file: File, sessionId?: string): Promise<EyeAnalysisSession> {
    const formData = new FormData();
    formData.append('file', file);
    const endpoint = sessionId
      ? `/eye-analysis/sessions/${sessionId}/video`
      : `/eye-analysis/video-screening`;
    const response = await apiClient.post<EyeAnalysisSession>(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async processSampleVideo(pattern: 'normal' | 'horizontal_nystagmus' | 'vertical_nystagmus'): Promise<EyeAnalysisSession> {
    const response = await apiClient.post<EyeAnalysisSession>(
      `/eye-analysis/sample-video-screening?pattern=${pattern}`
    );
    return response.data;
  },
};



