export interface AssignmentCreateInput {
  doctor_id?: string;
  patient_id?: string;
}

export interface DoctorPatientAssignment {
  id: string;
  doctor_id: string;
  patient_id: string;
  doctor_user_id: string;
  patient_user_id: string;
  doctor_name: string;
  doctor_specialization: string;
  doctor_license: string;
  patient_name: string;
  patient_email: string;
  assigned_at: string;
  notice: string;
}

export interface AssignedDoctor {
  has_assigned_doctor: boolean;
  assignment_id?: string | null;
  doctor_id?: string | null;
  doctor_user_id?: string | null;
  doctor_name?: string | null;
  specialization?: string | null;
  license_identifier?: string | null;
  assigned_at?: string | null;
}

export interface AssignedDoctorPublicProfile {
  doctor_id: string;
  doctor_user_id: string;
  full_name: string;
  specialization: string;
  license_identifier: string;
  assigned_at?: string | null;
  notice: string;
}

