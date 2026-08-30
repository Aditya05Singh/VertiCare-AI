import { DailyHealthCheck, DailyHealthTrendPoint } from './healthCheck';
import { SessionSummary } from './questionnaire';
import { EyeAnalysisSession } from './eyeAnalysis';
import { RiskAssessment } from './risk';

export type NoteType = 'ROUTINE_REVIEW' | 'EMERGENCY_FOLLOW_UP' | 'DIAGNOSTIC_HYPOTHESIS' | 'DISCHARGE';

export interface DoctorRecentActivityItem {
  patient_id: string;
  patient_name: string;
  activity_type: 'HEALTH_CHECK' | 'QUESTIONNAIRE' | 'EYE_ANALYSIS' | 'RISK_ASSESSMENT';
  timestamp: string;
  description: string;
  risk_level?: string | null;
}

export interface DoctorDashboardSummary {
  total_assigned_patients: number;
  risk_distribution: {
    HIGH: number;
    MEDIUM: number;
    LOW: number;
    UNASSESSED: number;
  };
  recent_activity: DoctorRecentActivityItem[];
}

export interface AssignedPatientCard {
  patient_id: string;
  full_name: string;
  email: string;
  date_of_birth: string;
  gender: string;
  assigned_at: string;
  latest_risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | null;
  latest_risk_score?: number | null;
  latest_assessment_date?: string | null;
  latest_health_check_date?: string | null;
  latest_health_check_dizziness?: number | null;
  total_health_checks: number;
}

export interface DoctorPatientList {
  items: AssignedPatientCard[];
  total: number;
}

export interface DoctorPatientDossier {
  patient_id: string;
  full_name: string;
  email: string;
  date_of_birth: string;
  gender: string;
  medical_history?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  latest_health_check?: DailyHealthCheck | null;
  latest_questionnaire?: SessionSummary | null;
  latest_eye_analysis?: EyeAnalysisSession | null;
  latest_risk_assessment?: RiskAssessment | null;
  recent_notes_count: number;
}

export interface DoctorNote {
  id: string;
  patient_id: string;
  doctor_id: string;
  doctor_name: string;
  doctor_specialization: string;
  risk_assessment_id?: string | null;
  note_type: NoteType;
  content: string;
  is_shared_with_patient: boolean;
  created_at: string;
  updated_at: string;
}

export interface DoctorPatientReport {
  patient_id: string;
  patient_name: string;
  generated_at: string;
  health_summary: {
    total_records_14d: number;
    average_dizziness: number;
    average_imbalance: number;
    average_sleep: number;
    average_stress: number;
  };
  questionnaire_summary?: {
    session_id: string;
    completed_at?: string | null;
    answers: Array<{
      question_code: string;
      question_text: string;
      answer: any;
    }>;
  } | null;
  eye_analysis_summary?: {
    session_id: string;
    created_at: string;
    quality: any;
    features: Record<string, number>;
  } | null;
  latest_risk?: RiskAssessment | null;
  clinical_notes: DoctorNote[];
  disclaimer: string;
}

