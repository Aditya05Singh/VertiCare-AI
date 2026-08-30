import { apiClient } from '@/api/client';
import { QuestionnaireSession, SessionSummary } from '@/types';

export const questionnaireApi = {
  async startOrResume(): Promise<QuestionnaireSession> {
    const response = await apiClient.get<QuestionnaireSession>('/questionnaire/start');
    return response.data;
  },

  async checkActive(): Promise<QuestionnaireSession | null> {
    const response = await apiClient.get<QuestionnaireSession | null>('/questionnaire/active');
    return response.data;
  },

  async getSession(sessionId: string): Promise<QuestionnaireSession> {
    const response = await apiClient.get<QuestionnaireSession>(`/questionnaire/session/${sessionId}`);
    return response.data;
  },

  async submitAnswer(sessionId: string, questionCode: string, answer: any): Promise<QuestionnaireSession> {
    const response = await apiClient.post<QuestionnaireSession>(
      `/questionnaire/session/${sessionId}/answer`,
      { question_code: questionCode, answer }
    );
    return response.data;
  },

  async completeSession(sessionId: string): Promise<QuestionnaireSession> {
    const response = await apiClient.post<QuestionnaireSession>(
      `/questionnaire/session/${sessionId}/complete`
    );
    return response.data;
  },

  async getSummary(sessionId: string): Promise<SessionSummary> {
    const response = await apiClient.get<SessionSummary>(
      `/questionnaire/session/${sessionId}/summary`
    );
    return response.data;
  },
};

