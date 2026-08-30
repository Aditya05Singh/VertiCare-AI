export interface DailyHealthCheck {
  id: string;
  patient_id: string;
  check_date: string;
  dizziness_severity: number;
  episode_duration: string;
  imbalance_severity: number;
  nausea: boolean;
  headache: boolean;
  sleep_hours: number;
  hydration_level: string;
  stress_level: number;
  medication_adherence: string;
  triggers: string[];
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DailyHealthCheckInput {
  check_date?: string;
  dizziness_severity: number;
  episode_duration: string;
  imbalance_severity: number;
  nausea: boolean;
  headache: boolean;
  sleep_hours: number;
  hydration_level: string;
  stress_level: number;
  medication_adherence: string;
  triggers: string[];
  notes?: string;
}

export interface DailyHealthCheckListResponse {
  items: DailyHealthCheck[];
  total: number;
  limit: number;
  offset: number;
}

export interface DailyHealthTrendPoint {
  date: string;
  dizziness_severity: number;
  imbalance_severity: number;
  sleep_hours: number;
  stress_level: number;
  hydration_level: string;
  nausea: boolean;
  headache: boolean;
  episode_duration: string;
}

export interface DailyHealthTrendResponse {
  patient_id: string;
  days_range: number;
  total_records: number;
  average_dizziness: number;
  average_imbalance: number;
  average_sleep: number;
  average_stress: number;
  data_points: DailyHealthTrendPoint[];
}

