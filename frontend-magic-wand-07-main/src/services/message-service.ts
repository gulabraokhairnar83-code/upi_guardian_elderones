/**
 * UPI Guardian - Message / Communication Analysis Service
 * Handles SMS and Call transcript scam detection.
 * Future Flask endpoint: POST /api/analyze-message
 */

import { apiClient, isMockEnabled } from "./api-client";
import { mockProvider } from "./mock-provider";
import type { MessageAnalysisResult } from "@/data/mock/sample-messages";

export type { MessageAnalysisResult };

export interface AnalyzeMessagePayload {
  text: string;
  type: "sms" | "call";
  user_id?: string;
}

interface BackendNlpResponse {
  success: boolean;
  analysis: {
    classification: string;
    scam_probability: number;
    risk_level: string;
    message_type: string;
    categories: string[];
    suspicious_phrases: string[];
    explanation: string;
    recommended_action: string;
    model_version?: string;
  };
}

export const messageService = {
  /**
   * POST /api/analyze-message
   * Analyzes an SMS text or call transcript for fraud, phishing, and coercion patterns.
   */
  async analyzeMessage(payload: AnalyzeMessagePayload): Promise<MessageAnalysisResult> {
    if (isMockEnabled()) {
      return mockProvider.analyzeMessage(payload);
    }

    const backendPayload = {
      text: payload.text,
      message_type: payload.type === "call" ? "call_transcript" : "sms",
      user_id: payload.user_id || "usr_sunita_68",
    };

    const res = await apiClient.post<BackendNlpResponse>("/analyze-message", backendPayload);
    const anl = res.analysis;

    const prob = Math.round(anl.scam_probability);
    let level: "safe" | "review" | "high" | "critical" = "safe";
    let title = "MESSAGE VERIFIED SAFE";

    const normalizedLevel = (anl.risk_level || "").toUpperCase();
    if (normalizedLevel === "CRITICAL" || prob >= 85) {
      level = "critical";
      title = "CRITICAL SCAM THREAT DETECTED";
    } else if (normalizedLevel === "HIGH" || prob >= 60) {
      level = "high";
      title = "POTENTIAL SCAM DETECTED";
    } else if (normalizedLevel === "MEDIUM" || prob >= 30) {
      level = "review";
      title = "SUSPICIOUS ACTIVITY DETECTED";
    }

    const patterns =
      anl.categories && anl.categories.length > 0
        ? anl.categories.map((c) =>
            c
              .split("_")
              .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
              .join(" ")
          )
        : ["No common scam categories detected"];

    return {
      isSuspicious: level !== "safe",
      riskScore: prob,
      level,
      title,
      detectedPatterns: patterns,
      explanation: anl.explanation,
      recommendations: [anl.recommended_action],
      isDemo: false,
      suspiciousPhrases: anl.suspicious_phrases || [],
      classification: anl.classification,
      recommendedAction: anl.recommended_action,
    };
  },

  /**
   * Retrieves sample prompt message for demo prefill.
   */
  async getSampleMessage(type: "sms" | "call"): Promise<string> {
    return mockProvider.getSampleMessage(type);
  },
};
