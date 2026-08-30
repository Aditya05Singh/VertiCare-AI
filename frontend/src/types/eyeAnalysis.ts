export interface QualitySummary {
  total_frames: number;
  valid_frames: number;
  valid_ratio: number;
  face_detected_ratio: number;
  is_sufficient: boolean;
}

export interface EyeMovementFeaturesSubmit {
  features: Record<string, number>;
  quality_summary: QualitySummary;
}

export interface EyeFeatureItem {
  id: string;
  feature_name: string;
  feature_value: number;
  created_at: string;
}

export interface EyeScreeningInterpretation {
  status: 'AVAILABLE' | 'UNAVAILABLE';
  label: string;
  confidence?: number | null;
  model_name: string;
  model_version: string;
  explanation: string;
  contributing_factors: string[];
  disclaimer: string;
  domain_shift_notice: string;
}

export interface EyeAnalysisSession {
  id: string;
  patient_id: string;
  started_at: string;
  ended_at?: string | null;
  analysis_status: string;
  quality_summary: QualitySummary;
  features: EyeFeatureItem[] | Record<string, number>;
  screening?: EyeScreeningInterpretation | null;
  created_at: string;
  notice?: string;
}
