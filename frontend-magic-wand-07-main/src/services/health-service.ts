/**
 * UPI Guardian - Health Check Service
 * Checks backend API connectivity safely without exposing internal secrets.
 */

import { apiClient, isMockEnabled } from "./api-client";

export interface HealthStatus {
  status: "healthy" | "degraded" | "offline";
  service: string;
  version: string;
  timestamp?: string | undefined;
  isMock: boolean;
}

export const healthService = {
  /**
   * GET /api/health
   * Connectivity check to verify Flask backend status.
   */
  async checkHealth(): Promise<HealthStatus> {
    if (isMockEnabled()) {
      return {
        status: "healthy",
        service: "UPI Guardian Mock Provider",
        version: "demo-1.0.0",
        timestamp: new Date().toISOString(),
        isMock: true,
      };
    }

    try {
      const data = await apiClient.get<{
        status: string;
        service: string;
        version: string;
        timestamp?: string;
      }>("/health", { timeoutMs: 4000 });

      return {
        status: data.status === "healthy" ? "healthy" : "degraded",
        service: data.service || "UPI Guardian Flask API",
        version: data.version || "1.0.0",
        timestamp: data.timestamp || new Date().toISOString(),
        isMock: false,
      };
    } catch {
      return {
        status: "offline",
        service: "UPI Guardian Flask API",
        version: "unknown",
        timestamp: new Date().toISOString(),
        isMock: false,
      };
    }
  },
};
