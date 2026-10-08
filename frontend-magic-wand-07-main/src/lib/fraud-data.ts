export type {
  RiskLevel,
  Transaction,
  ActivityPoint,
  ReportPoint,
} from "@/data/mock/transactions";
export {
  transactions,
  activityData,
  reportData,
  riskFactors,
} from "@/data/mock/transactions";
export type { Alert } from "@/data/mock/alerts";
export { alerts } from "@/data/mock/alerts";

export const api = {
  baseUrl: (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? "/api",
  endpoints: {
    transactions: "/transactions",
    alerts: "/alerts",
    analyzeTransaction: "/analyze-transaction",
    analyzeSms: "/analyze-sms",
    analyzeCall: "/analyze-call",
    riskScore: "/risk-score",
    family: "/family",
    reports: "/reports",
  },
};