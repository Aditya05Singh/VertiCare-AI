import { apiClient } from '@/api/client';
import {
  DoctorDashboardSummary,
  DoctorPatientList,
  DoctorPatientDossier,
  DoctorNote,
  DoctorPatientReport,
  NoteType,
  DailyHealthCheckListResponse,
  DailyHealthTrendResponse,
  SessionSummary,
  EyeAnalysisSession,
  RiskAssessmentList,
} from '@/types';

export const doctorApi = {
  async getDashboardSummary(): Promise<DoctorDashboardSummary> {
    const response = await apiClient.get<DoctorDashboardSummary>('/doctor/dashboard');
    return response.data;
  },

  async getAssignedPatients(params?: {
    search?: string;
    risk_filter?: string;
    sort_by?: string;
  }): Promise<DoctorPatientList> {
    const response = await apiClient.get<DoctorPatientList>('/doctor/patients', { params });
    return response.data;
  },

  async getPatientDossier(patientId: string): Promise<DoctorPatientDossier> {
    const response = await apiClient.get<DoctorPatientDossier>(`/doctor/patients/${patientId}`);
    return response.data;
  },

  async getPatientHealthHistory(
    patientId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<DailyHealthCheckListResponse> {
    const response = await apiClient.get<DailyHealthCheckListResponse>(
      `/doctor/patients/${patientId}/health?limit=${limit}&offset=${offset}`
    );
    return response.data;
  },

  async getPatientHealthTrends(patientId: string, days: number = 14): Promise<DailyHealthTrendResponse> {
    const response = await apiClient.get<DailyHealthTrendResponse>(
      `/doctor/patients/${patientId}/health/trends?days=${days}`
    );
    return response.data;
  },

  async getPatientQuestionnaires(patientId: string): Promise<SessionSummary[]> {
    const response = await apiClient.get<SessionSummary[]>(
      `/doctor/patients/${patientId}/questionnaire`
    );
    return response.data;
  },

  async getPatientEyeAnalyses(patientId: string): Promise<EyeAnalysisSession[]> {
    const response = await apiClient.get<EyeAnalysisSession[]>(
      `/doctor/patients/${patientId}/eye-analysis`
    );
    return response.data;
  },

  async getPatientRiskHistory(
    patientId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<RiskAssessmentList> {
    const response = await apiClient.get<RiskAssessmentList>(
      `/doctor/patients/${patientId}/risk?limit=${limit}&offset=${offset}`
    );
    return response.data;
  },

  async getPatientNotes(patientId: string): Promise<DoctorNote[]> {
    const response = await apiClient.get<DoctorNote[]>(`/doctor/patients/${patientId}/notes`);
    return response.data;
  },

  async createPatientNote(
    patientId: string,
    data: {
      content: string;
      note_type?: NoteType;
      risk_assessment_id?: string | null;
      is_shared_with_patient?: boolean;
    }
  ): Promise<DoctorNote> {
    const response = await apiClient.post<DoctorNote>(`/doctor/patients/${patientId}/notes`, data);
    return response.data;
  },

  async updateDoctorNote(
    noteId: string,
    data: {
      content: string;
      note_type?: NoteType;
      is_shared_with_patient?: boolean;
    }
  ): Promise<DoctorNote> {
    const response = await apiClient.patch<DoctorNote>(`/doctor/notes/${noteId}`, data);
    return response.data;
  },

  async getPatientReport(patientId: string): Promise<DoctorPatientReport> {
    const response = await apiClient.get<DoctorPatientReport>(
      `/doctor/patients/${patientId}/reports`
    );
    return response.data;
  },
};

