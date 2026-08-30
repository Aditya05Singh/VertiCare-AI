export type EmergencySeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type EmergencyStatus = 'PENDING' | 'CONTACT_INITIATED' | 'ACKNOWLEDGED' | 'RESOLVED' | 'CANCELLED';

export interface EmergencyEvent {
  id: string;
  patient_id: string;
  patient_name?: string | null;
  patient_dob?: string | null;
  patient_gender?: string | null;
  risk_assessment_id?: string | null;
  risk_level?: string | null;
  risk_score?: number | null;
  severity: EmergencySeverity;
  status: EmergencyStatus;
  contacted_doctor: boolean;
  contacted_emergency_contact: boolean;
  contacted_at?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  assigned_doctor_name?: string | null;
  assigned_doctor_specialization?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  notice: string;
}

export interface EmergencyEventList {
  items: EmergencyEvent[];
  total: number;
  limit: number;
  offset: number;
}

export interface EmergencyContext {
  has_emergency_contact: boolean;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  has_assigned_doctor: boolean;
  assigned_doctor_name?: string | null;
  assigned_doctor_specialization?: string | null;
  latest_risk_level?: string | null;
  latest_risk_score?: number | null;
  latest_risk_assessment_id?: string | null;
  active_event?: EmergencyEvent | null;
}

export interface EmergencyGuidanceItem {
  title: string;
  description: string;
  category: string;
}

export interface EmergencyGuidance {
  guidance: EmergencyGuidanceItem[];
  disclaimer: string;
}

