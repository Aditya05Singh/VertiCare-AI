import { apiClient } from '@/api/client';
import {
  AssignmentCreateInput,
  DoctorPatientAssignment,
  AssignedDoctor,
  AssignedDoctorPublicProfile,
  DoctorPatientList,
} from '@/types';

export const assignmentApi = {
  async createAssignment(data: AssignmentCreateInput): Promise<DoctorPatientAssignment> {
    const response = await apiClient.post<DoctorPatientAssignment>('/assignments', data);
    return response.data;
  },

  async getAssignedDoctor(): Promise<AssignedDoctor> {
    const response = await apiClient.get<AssignedDoctor>('/patient/assigned-doctor');
    return response.data;
  },

  async getDoctorProfile(doctorId: string): Promise<AssignedDoctorPublicProfile> {
    const response = await apiClient.get<AssignedDoctorPublicProfile>(`/patient/doctor-profile/${doctorId}`);
    return response.data;
  },

  async getAssignedPatients(): Promise<DoctorPatientList> {
    const response = await apiClient.get<DoctorPatientList>('/doctor/assigned-patients');
    return response.data;
  },

  async deleteAssignment(assignmentId: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/assignments/${assignmentId}`);
    return response.data;
  },
};

