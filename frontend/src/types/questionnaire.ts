export type QuestionType = 'BOOLEAN' | 'SINGLE_CHOICE' | 'MULTI_CHOICE' | 'NUMBER' | 'TEXT';
export type SessionStatus = 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';

export interface QuestionOption {
  value: string;
  label: string;
}

export interface QuestionnaireQuestion {
  id: string;
  question_code: string;
  version: string;
  category: string;
  question_type: QuestionType;
  question_text: string;
  options: QuestionOption[];
  display_order: number;
}

export interface SessionProgress {
  answered_count: number;
  estimated_total: number;
  current_step: number;
}

export interface QuestionnaireSession {
  session_id: string;
  status: SessionStatus;
  started_at: string;
  completed_at?: string | null;
  current_question?: QuestionnaireQuestion | null;
  progress: SessionProgress;
  message?: string | null;
}

export interface AnswerSummaryItem {
  question_code: string;
  question_text: string;
  category: string;
  question_type: QuestionType;
  answer: any;
  answered_at: string;
}

export interface SessionSummary {
  session_id: string;
  patient_id: string;
  status: SessionStatus;
  started_at: string;
  completed_at?: string | null;
  total_questions_answered: number;
  answers: AnswerSummaryItem[];
  notice: string;
}

