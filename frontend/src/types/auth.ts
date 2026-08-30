export type UserRole = "PATIENT" | "DOCTOR";

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  patient_profile_id?: string | null;
  doctor_profile_id?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PatientRegisterInput {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: "MALE" | "FEMALE" | "OTHER" | "PREFER_NOT_TO_SAY";
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  medical_history?: string;
}

export interface DoctorRegisterInput {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  specialization: string;
  license_identifier: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

