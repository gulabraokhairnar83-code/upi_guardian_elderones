/**
 * UPI Guardian - Transaction Service
 * Handles transaction monitoring and ML anomaly analysis.
 */

import { apiClient, isMockEnabled } from "./api-client";
import { mockProvider, type TransactionAnalysisResult } from "./mock-provider";
import type { Transaction, RiskLevel } from "@/data/mock/transactions";

export type { Transaction, RiskLevel, TransactionAnalysisResult };

export interface AnalyzeTransactionPayload {
  payee: string;
  amount: number;
  upiId: string;
  location?: string;
  device?: string;
  time?: string;
  user_id?: string;
  transaction_id?: string;
}

function normalizeTransaction(t: any): Transaction {
  const statusStr = String(t.status || t.risk_level || "safe").toLowerCase();
  const status: RiskLevel =
    statusStr === "critical"
      ? "critical"
      : statusStr === "high"
      ? "high"
      : statusStr === "review"
      ? "review"
      : "safe";

  const rawRisk =
    t.risk !== undefined
      ? t.risk
      : t.final_risk_score !== undefined
      ? t.final_risk_score
      : t.anomaly_score !== undefined
      ? Math.round(t.anomaly_score * 100)
      : 10;

  let date = t.date;
  let time = t.time;
  if ((!date || !time) && t.timestamp) {
    try {
      const dt = new Date(t.timestamp);
      if (!isNaN(dt.getTime())) {
        date = date || dt.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
        time = time || dt.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
      }
    } catch {
      // ignore
    }
  }

  return {
    ...t,
    id: String(t.id || t.transaction_id || ""),
    date: date || "Today",
    time: time || "Recent",
    payee: t.payee || "Unknown Payee",
    amount: Number(t.amount || 0),
    location: t.location || "Pune",
    risk: typeof rawRisk === "number" ? rawRisk : 10,
    status,
    newPayee: t.newPayee !== undefined ? Boolean(t.newPayee) : Boolean(t.is_new_payee),
    upiId: t.upiId || (t.payee ? `${String(t.payee).toLowerCase().replace(/[^a-z0-9]/g, "")}@okaxis` : "upi@user"),
    device: t.device || "Android Device",
  };
}

export const transactionService = {
  /**
   * GET /api/transactions
   * Retrieves transactions with optional filtering
   */
  async getTransactions(filter?: { status?: string; query?: string }): Promise<Transaction[]> {
    if (isMockEnabled()) {
      return mockProvider.getTransactions(filter);
    }

    const data = await apiClient.get<any[]>("/transactions", {
      params: {
        status: filter?.status && filter.status !== "all" ? filter.status : undefined,
        q: filter?.query || undefined,
      },
    });

    return Array.isArray(data) ? data.map(normalizeTransaction) : [];
  },

  /**
   * GET /api/transactions/:id
   * Retrieves single transaction details by ID
   */
  async getTransactionById(id: string): Promise<Transaction | null> {
    if (isMockEnabled()) {
      return mockProvider.getTransactionById(id);
    }

    const data = await apiClient.get<any>(`/transactions/${encodeURIComponent(id)}`);
    return data ? normalizeTransaction(data) : null;
  },

  /**
   * POST /api/analyze-transaction
   * Analyzes a proposed or active transaction using backend ML models
   */
  async analyzeTransaction(payload: AnalyzeTransactionPayload): Promise<TransactionAnalysisResult> {
    if (isMockEnabled()) {
      return mockProvider.analyzeTransaction(payload);
    }

    const raw = await apiClient.post<any>("/analyze-transaction", payload);
    const riskScore =
      raw.risk !== undefined
        ? raw.risk
        : typeof raw.anomaly_score === "number"
        ? Math.round(raw.anomaly_score <= 1.0 ? raw.anomaly_score * 100 : raw.anomaly_score)
        : 50;

    const statusMap: Record<string, RiskLevel> = {
      LOW: "safe",
      MEDIUM: "review",
      HIGH: "high",
      CRITICAL: "critical",
      safe: "safe",
      review: "review",
      high: "high",
      critical: "critical",
    };
    const riskLevel = statusMap[raw.risk_level] || statusMap[raw.status] || "safe";
    const contributingFactors = Array.isArray(raw.contributing_factors)
      ? raw.contributing_factors.map((f: any) =>
          typeof f === "string" ? { name: f, score: riskScore } : f
        )
      : [];
    let recAction: "allow" | "review" | "block" = "allow";
    if (riskLevel === "critical") recAction = "block";
    else if (riskLevel === "high" || riskLevel === "review") recAction = "review";

    return {
      transactionId: raw.transaction_id || raw.transactionId || payload.transaction_id || "TXN-ANL",
      payee: payload.payee,
      amount: payload.amount,
      riskScore,
      riskLevel,
      contributingFactors,
      explanation: raw.explanation || "Behavioral anomaly evaluation complete.",
      recommendedAction: recAction,
      isDemo: false,
    };
  },
};
