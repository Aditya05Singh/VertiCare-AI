import { apiClient } from '@/api/client';
import {
  EmergencyEvent,
  EmergencyEventList,
  EmergencyContext,
  EmergencyGuidance,
  EmergencySeverity,
} from '@/types';

export const emergencyApi = {
  async getGuidance(): Promise<EmergencyGuidance> {
    const response = await apiClient.get<EmergencyGuidance>('/emergency-events/guidance');
    return response.data;
  },

  async getContext(): Promise<EmergencyContext> {
    const response = await apiClient.get<EmergencyContext>('/emergency-events/context');
    return response.data;
  },

  async createEvent(data: {
    severity?: EmergencySeverity;
    risk_assessment_id?: string | null;
    notes?: string;
    initiate_doctor_contact?: boolean;
    initiate_emergency_contact?: boolean;
  }): Promise<EmergencyEvent> {
    const response = await apiClient.post<EmergencyEvent>('/emergency-events', data);
    return response.data;
  },

  async listEvents(params?: {
    limit?: number;
    offset?: number;
    status?: string;
  }): Promise<EmergencyEventList> {
    const response = await apiClient.get<EmergencyEventList>('/emergency-events', { params });
    return response.data;
  },

  async getEvent(eventId: string): Promise<EmergencyEvent> {
    const response = await apiClient.get<EmergencyEvent>(`/emergency-events/${eventId}`);
    return response.data;
  },

  async executePatientAction(
    eventId: string,
    action: 'CONTACT_DOCTOR' | 'CONTACT_EMERGENCY_CONTACT' | 'CANCEL',
    notes?: string
  ): Promise<EmergencyEvent> {
    const response = await apiClient.post<EmergencyEvent>(
      `/emergency-events/${eventId}/patient-action`,
      { action, notes }
    );
    return response.data;
  },

  async executeDoctorAction(
    eventId: string,
    action: 'ACKNOWLEDGE' | 'RESOLVE',
    notes?: string
  ): Promise<EmergencyEvent> {
    const response = await apiClient.post<EmergencyEvent>(
      `/emergency-events/${eventId}/doctor-action`,
      { action, notes }
    );
    return response.data;
  },
};

