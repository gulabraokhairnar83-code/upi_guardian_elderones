/**
 * UPI Guardian - Alert Service
 * Handles fetching, filtering, and resolving fraud alerts.
 */

import { apiClient, isMockEnabled } from "./api-client";
import { mockProvider } from "./mock-provider";
import type { Alert } from "@/data/mock/alerts";

export type { Alert };

export const alertService = {
  /**
   * GET /api/alerts
   * Retrieves alerts with optional risk level filter
   */
  async getAlerts(level?: string): Promise<Alert[]> {
    if (isMockEnabled()) {
      return mockProvider.getAlerts(level);
    }

    return await apiClient.get<Alert[]>("/alerts", {
      params: {
        level: level && level !== "all" ? level : undefined,
      },
    });
  },

  /**
   * POST /api/alerts/:id/resolve
   * Resolves a flagged fraud alert
   */
  async resolveAlert(id: number | string): Promise<{ success: boolean; id: number | string }> {
    if (isMockEnabled()) {
      const numId = typeof id === "number" ? id : parseInt(String(id), 10) || 1;
      return mockProvider.resolveAlert(numId);
    }

    return await apiClient.post<{ success: boolean; id: number | string }>(`/alerts/${id}/resolve`);
  },
};
