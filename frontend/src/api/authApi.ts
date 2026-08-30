import { apiClient } from '@/api/client';
import {
  AuthResponse,
  LoginInput,
  PatientRegisterInput,
  DoctorRegisterInput,
  User,
} from '@/types';

export const authApi = {
  async login(data: LoginInput): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  async registerPatient(data: PatientRegisterInput): Promise<User> {
    const response = await apiClient.post<User>('/auth/register/patient', data);
    return response.data;
  },

  async registerDoctor(data: DoctorRegisterInput): Promise<User> {
    const response = await apiClient.post<User>('/auth/register/doctor', data);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },
};

