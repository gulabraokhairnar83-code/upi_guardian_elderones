/**
 * UPI Guardian - Settings Service
 * Handles user preferences, security switches, and accessibility toggles.
 */

import { apiClient, isMockEnabled } from "./api-client";
import { mockProvider, type UserSettings } from "./mock-provider";

export type { UserSettings };

export const settingsService = {
  /**
   * GET /api/settings
   * Retrieves saved user settings
   */
  async getSettings(): Promise<UserSettings> {
    if (isMockEnabled()) {
      return mockProvider.getSettings();
    }

    return await apiClient.get<UserSettings>("/settings");
  },

  /**
   * PATCH /api/settings
   * Updates user settings
   */
  async updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    if (isMockEnabled()) {
      return mockProvider.updateSettings(settings);
    }

    return await apiClient.patch<UserSettings>("/settings", settings);
  },
};
