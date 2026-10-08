/**
 * UPI Guardian - Mock Data Provider
 * Provides realistic synthetic data during prototype mode or when the Flask backend is offline.
 * NOTE: All analyzer results here are synthetic demo placeholders and explicitly flagged with `isDemo: true`.
 */

import {
  transactions,
  activityData,
  reportData,
  riskFactors,
  type Transaction,
  type RiskLevel,
  type ActivityPoint,
  type ReportPoint,
} from "@/data/mock/transactions";
import { alerts, type Alert } from "@/data/mock/alerts";
import { elderProfile, type ElderProfile } from "@/data/mock/elder-profile";
import { emergencyContacts, type EmergencyContact } from "@/data/mock/emergency-contacts";
import {
  sampleCallTranscript,
  sampleSmsText,
  mockCallAnalysisResult,
  mockSmsAnalysisResult,
  type MessageAnalysisResult,
} from "@/data/mock/sample-messages";

export interface DashboardSummary {
  systemStatus: "OPERATIONAL" | "DEGRADED" | "OFFLINE";
  accountStatus: "Protected" | "At Risk" | "Review Required";
  currentRiskScore: number;
  riskLevel: RiskLevel;
  riskSummary: string;
  overall_risk_score?: number | undefined;
  overall_risk_level?: RiskLevel | undefined;
  critical_alert_count?: number | undefined;
  communication_transaction_correlations?: number | undefined;
  top_risk_factors?: string[] | undefined;
  kpis: Array<{
    label: string;
    value: string;
    trend: string;
    tone: "info" | "safe" | "warning" | "danger";
  }>;
  activity: ActivityPoint[];
  recentAlerts: Alert[];
}

export interface TransactionAnalysisResult {
  transactionId: string;
  payee: string;
  amount: number;
  riskScore: number;
  riskLevel: RiskLevel;
  contributingFactors: Array<{ name: string; score: number }>;
  explanation: string;
  recommendedAction: "allow" | "review" | "block";
  isDemo: boolean;
}

export interface UserSettings {
  profile: {
    name: string;
    age: number;
    phone: string;
    email: string;
  };
  security: {
    twoFactor: boolean;
    loginActivityAlerts: boolean;
  };
  alertPreferences: {
    highRiskTransactions: boolean;
    scamCalls: boolean;
    scamSms: boolean;
    familyNotifications: boolean;
  };
  accessibility: {
    seniorMode: boolean;
    highContrast: boolean;
    reducedMotion: boolean;
    voiceAssistance: boolean;
  };
}

let mockAlertsState = [...alerts];
let mockTransactionsState = [...transactions];
let mockContactsState = [...emergencyContacts];
let mockElderProfileState = { ...elderProfile };

let mockSettingsState: UserSettings = {
  profile: {
    name: "Sunita Devi",
    age: 68,
    phone: "+91 ••••• ••410",
    email: "sunita.demo@example.com",
  },
  security: {
    twoFactor: true,
    loginActivityAlerts: true,
  },
  alertPreferences: {
    highRiskTransactions: true,
    scamCalls: true,
    scamSms: true,
    familyNotifications: true,
  },
  accessibility: {
    seniorMode: false,
    highContrast: false,
    reducedMotion: false,
    voiceAssistance: false,
  },
};

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockProvider = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    await delay(120);
    return {
      systemStatus: "OPERATIONAL",
      accountStatus: "Protected",
      currentRiskScore: 27,
      riskLevel: "safe",
      riskSummary: "Low risk. No immediate action needed.",
      kpis: [
        { label: "Transactions", value: "24", trend: "+12%", tone: "info" },
        { label: "Safe", value: "20", trend: "+8%", tone: "safe" },
        { label: "Suspicious", value: "3", trend: "-2%", tone: "warning" },
        { label: "High Risk Alerts", value: "1", trend: "+1", tone: "danger" },
        { label: "Current Risk Score", value: "27/100", trend: "Normal", tone: "safe" },
        { label: "Scams Detected", value: "2", trend: "+100%", tone: "danger" },
      ],
      activity: activityData,
      recentAlerts: mockAlertsState.slice(0, 3),
    };
  },

  async getTransactions(filter?: { status?: string; query?: string }): Promise<Transaction[]> {
    await delay(150);
    let result = [...mockTransactionsState];
    if (filter?.status && filter.status !== "all") {
      result = result.filter((t) => t.status === filter.status);
    }
    if (filter?.query && filter.query.trim()) {
      const q = filter.query.toLowerCase().trim();
      result = result.filter(
        (t) => t.payee.toLowerCase().includes(q) || t.id.toLowerCase().includes(q)
      );
    }
    return result;
  },

  async getTransactionById(id: string): Promise<Transaction | null> {
    await delay(100);
    return mockTransactionsState.find((t) => t.id === id) ?? null;
  },

  async analyzeTransaction(payload: {
    payee: string;
    amount: number;
    upiId: string;
  }): Promise<TransactionAnalysisResult> {
    await delay(250);
    const isHigh = payload.amount > 20000;
    return {
      transactionId: `TXN-UG-${Date.now()}`,
      payee: payload.payee,
      amount: payload.amount,
      riskScore: isHigh ? 89 : 24,
      riskLevel: isHigh ? "critical" : "safe",
      contributingFactors: riskFactors.map(([name, score]) => ({ name, score })),
      explanation: isHigh
        ? "Simulated demo risk: High amount anomaly and unverified payee pattern."
        : "Simulated demo risk: Normal transaction velocity and recognized spending bracket.",
      recommendedAction: isHigh ? "block" : "allow",
      isDemo: true,
    };
  },

  async getAlerts(level?: string): Promise<Alert[]> {
    await delay(120);
    if (level && level !== "all") {
      return mockAlertsState.filter((a) => a.level === level);
    }
    return [...mockAlertsState];
  },

  async resolveAlert(id: number): Promise<{ success: boolean; id: number }> {
    await delay(150);
    mockAlertsState = mockAlertsState.filter((a) => a.id !== id);
    return { success: true, id };
  },

  async analyzeMessage(payload: {
    text: string;
    type: "call" | "sms";
  }): Promise<MessageAnalysisResult> {
    await delay(300);
    if (payload.type === "sms") {
      return { ...mockSmsAnalysisResult, isDemo: true };
    }
    return { ...mockCallAnalysisResult, isDemo: true };
  },

  async getSampleMessage(type: "call" | "sms"): Promise<string> {
    return type === "sms" ? sampleSmsText : sampleCallTranscript;
  },

  async getElderProfile(): Promise<ElderProfile> {
    await delay(120);
    return { ...mockElderProfileState };
  },

  async getEmergencyContacts(): Promise<EmergencyContact[]> {
    await delay(100);
    return [...mockContactsState];
  },

  async resolveFamilyAlert(): Promise<{ success: boolean }> {
    await delay(150);
    mockElderProfileState = {
      ...mockElderProfileState,
      metrics: {
        ...mockElderProfileState.metrics,
        activeAlertsCount: 0,
      },
    };
    return { success: true };
  },

  async getReportsData(): Promise<{ reportData: ReportPoint[]; activityData: ActivityPoint[] }> {
    await delay(150);
    return { reportData, activityData };
  },

  async getSettings(): Promise<UserSettings> {
    await delay(100);
    return { ...mockSettingsState };
  },

  async updateSettings(newSettings: Partial<UserSettings>): Promise<UserSettings> {
    await delay(200);
    mockSettingsState = {
      ...mockSettingsState,
      ...newSettings,
      profile: { ...mockSettingsState.profile, ...newSettings.profile },
      security: { ...mockSettingsState.security, ...newSettings.security },
      alertPreferences: { ...mockSettingsState.alertPreferences, ...newSettings.alertPreferences },
      accessibility: { ...mockSettingsState.accessibility, ...newSettings.accessibility },
    };
    return { ...mockSettingsState };
  },
};
