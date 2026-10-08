/**
 * UPI Guardian - Dashboard Service
 * Fetches dashboard KPIs, live security status, and recent activity.
 */

import { apiClient, isMockEnabled } from "./api-client";
import { mockProvider, type DashboardSummary } from "./mock-provider";

export type { DashboardSummary };

export const dashboardService = {
  /**
   * Fetches the dashboard overview.
   * Real endpoint: GET /api/dashboard/summary
   */
  async getSummary(): Promise<DashboardSummary> {
    if (isMockEnabled()) {
      return mockProvider.getDashboardSummary();
    }

    return await apiClient.get<DashboardSummary>("/dashboard/summary");
  },
};
