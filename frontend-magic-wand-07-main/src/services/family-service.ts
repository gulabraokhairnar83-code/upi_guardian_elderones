/**
 * UPI Guardian - Family & Caregiver Service
 * Handles elder safety monitoring, family notifications, and emergency contacts.
 */

import { apiClient, isMockEnabled } from "./api-client";
import { mockProvider } from "./mock-provider";
import type { ElderProfile } from "@/data/mock/elder-profile";
import type { EmergencyContact } from "@/data/mock/emergency-contacts";

export type { ElderProfile, EmergencyContact };

export const familyService = {
  /**
   * GET /api/family/profile
   * Retrieves protected elder profile details and safety status
   */
  async getElderProfile(): Promise<ElderProfile> {
    if (isMockEnabled()) {
      return mockProvider.getElderProfile();
    }

    return await apiClient.get<ElderProfile>("/family/profile");
  },

  /**
   * Retrieves emergency contacts roster.
   * NOTE: Full caregiver invitation & roster management is scheduled for Phase 8.
   */
  async getEmergencyContacts(): Promise<EmergencyContact[]> {
    return mockProvider.getEmergencyContacts();
  },

  /**
   * POST /api/family/alerts/resolve
   * Resolves the urgent family alert
   */
  async resolveFamilyAlert(): Promise<{ success: boolean }> {
    if (isMockEnabled()) {
      return mockProvider.resolveFamilyAlert();
    }

    return await apiClient.post<{ success: boolean }>("/family/alerts/resolve");
  },
};
