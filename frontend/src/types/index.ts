export * from './auth';
export * from './healthCheck';
export * from './questionnaire';
export * from './eyeAnalysis';
export * from './risk';
export * from './doctor';
export * from './emergency';
export * from './assignment';

export interface HealthStatus {
  status: string;
  service: string;
}
