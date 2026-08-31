export const APP_NAME = "VertiCare AI";

export const MEDICAL_DISCLAIMER =
  "Academic Healthcare Prototype: VertiCare AI is intended solely for vertigo screening, continuous monitoring, and clinical decision support. It is NOT a diagnostic medical device and does NOT replace evaluation by a qualified ENT specialist, neurologist, or healthcare provider.";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV
    ? "/api/v1"
    : "https://backend-five-lime-21.vercel.app/api/v1");

