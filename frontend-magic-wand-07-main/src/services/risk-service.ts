/**
 * UPI Guardian - Risk Fusion Service
 * Connects frontend to the Phase 6 Risk Fusion Engine and Risk Events audit log.
 */

import { apiClient, isMockEnabled } from "./api-client";
import type { RiskLevel } from "@/data/mock/transactions";

export interface RiskAnalysisRequestPayload {
  transaction_id?: string;
  user_id?: string;
  payee?: string;
  amount?: number;
  upiId?: string;
  is_new_payee?: boolean;
  velocity?: number;
  timestamp?: string;
}

export interface RiskFusionAnalysis {
  transaction_id: string;
  user_id: string;
  transaction_anomaly_score: number;
  communication_risk_score: number;
  behavioral_deviation_score: number;
  new_payee_score: number;
  velocity_score: number;
  temporal_correlation_score: number;
  correlation_boost: number;
  final_risk_score: number;
  risk_level: string; // "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  top_contributing_factors: string[];
  explanation: string;
  recommended_action: string;
  communication_id?: string | null;
  alert_created?: boolean;
}

export interface RiskEvent {
  id: string;
  event_id: string;
  user_id: string;
  transaction_id: string;
  final_risk_score: number;
  risk_level: string;
  top_contributing_factors?: string[];
  explanation?: string;
  recommended_action?: string;
  created_at: string;
  timestamp?: string;
}

// Fallback synthetic mock response for offline demonstration
const mockFusionSample: RiskFusionAnalysis = {
  transaction_id: "TXN-UG-928405",
  user_id: "usr_sunita_68",
  transaction_anomaly_score: 84.5,
  communication_risk_score: 95.0,
  behavioral_deviation_score: 78.0,
  new_payee_score: 100.0,
  velocity_score: 70.0,
  temporal_correlation_score: 85.0,
  correlation_boost: 10.0,
  final_risk_score: 92.4,
  risk_level: "CRITICAL",
  top_contributing_factors: [
    "New or unfamiliar payee",
    "Suspicious communication detected",
    "Transaction occurred shortly after suspicious communication",
    "Unusual transaction amount",
  ],
  explanation:
    "High-risk activity detected because an unusual transaction occurred shortly after a suspicious communication. The transaction involves significant deviations from your normal pattern.",
  recommended_action:
    "Do not proceed. Contact a trusted caregiver or official bank/UPI support using a verified contact method.",
  communication_id: "msg_scam_01",
  alert_created: true,
};

const mockEventsSample: RiskEvent[] = [
  {
    id: "re_demo_01",
    event_id: "re_demo_01",
    user_id: "usr_sunita_68",
    transaction_id: "TXN-UG-928405",
    final_risk_score: 92.4,
    risk_level: "CRITICAL",
    top_contributing_factors: [
      "New or unfamiliar payee",
      "Suspicious communication detected",
    ],
    explanation: "High-risk activity detected shortly after suspicious SMS.",
    recommended_action: "Do not proceed. Contact trusted caregiver.",
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "re_demo_02",
    event_id: "re_demo_02",
    user_id: "usr_sunita_68",
    transaction_id: "TXN-UG-928401",
    final_risk_score: 64.2,
    risk_level: "HIGH",
    top_contributing_factors: ["Unusual transaction amount"],
    explanation: "Suspicious activity detected due to unusual payment amount.",
    recommended_action: "Pause the transaction and verify the recipient.",
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
];

export const riskService = {
  /**
   * POST /api/risk/analyze
   * Computes multi-signal composite risk score using Phase 6 Risk Fusion Engine.
   */
  async analyzeRisk(payload: RiskAnalysisRequestPayload): Promise<RiskFusionAnalysis> {
    if (isMockEnabled()) {
      return {
        ...mockFusionSample,
        transaction_id: payload.transaction_id || `TXN-DEMO-${Date.now()}`,
        final_risk_score: payload.amount && payload.amount > 20000 ? 92.4 : 24.0,
        risk_level: payload.amount && payload.amount > 20000 ? "CRITICAL" : "LOW",
      };
    }

    const normalizedPayload = {
      ...payload,
      upiId:
        payload.upiId ||
        (payload.payee
          ? `${payload.payee.toLowerCase().replace(/[^a-z0-9]/g, "")}@okaxis`
          : "payment@okaxis"),
    };

    const res = await apiClient.post<{ success: boolean; analysis: RiskFusionAnalysis }>(
      "/risk/analyze",
      normalizedPayload
    );
    return res.analysis;
  },

  /**
   * GET /api/risk/events
   * Retrieves historical audit events from risk_events collection.
   */
  async getRiskEvents(userId = "usr_sunita_68", limit = 20): Promise<RiskEvent[]> {
    if (isMockEnabled()) {
      return mockEventsSample;
    }

    const res = await apiClient.get<{ success: boolean; events: RiskEvent[]; count: number }>(
      "/risk/events",
      {
        params: {
          user_id: userId,
          limit,
        },
      }
    );
    return res.events;
  },
};
