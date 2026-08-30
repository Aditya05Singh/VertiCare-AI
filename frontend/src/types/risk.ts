export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export interface RiskAssessment {
  id: string;
  patient_id: string;
  health_check_id?: string | null;
  questionnaire_session_id?: string | null;
  eye_analysis_session_id?: string | null;
  risk_score: number;
  risk_level: RiskLevel;
  model_name: string;
  model_version: string;
  contributing_factors: string[];
  created_at: string;
  notice: string;
}

export interface RiskAssessmentList {
  items: RiskAssessment[];
  total: number;
  limit: number;
  offset: number;
}

