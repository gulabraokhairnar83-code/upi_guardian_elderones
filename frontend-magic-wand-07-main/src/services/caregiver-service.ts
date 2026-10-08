/**
 * UPI Guardian - Caregiver Service
 * Manages trusted caregivers, verification status, and notification preferences.
 */

import { apiClient, isMockEnabled } from "./api-client";

export interface NotificationPreferences {
  sms_enabled: boolean;
  voice_enabled: boolean;
  high_risk_enabled: boolean;
  critical_risk_enabled: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  max_notifications_per_hour: number;
}

export interface Caregiver {
  caregiver_id: string;
  elder_user_id: string;
  caregiver_user_id?: string | undefined;
  name: string;
  phone: string;
  email: string;
  relationship: "SON" | "DAUGHTER" | "SPOUSE" | "RELATIVE" | "FRIEND" | "OTHER";
  status: "PENDING" | "VERIFIED" | "DISABLED";
  is_verified: boolean;
  is_active: boolean;
  isTrusted?: boolean | undefined;
  notification_preferences: NotificationPreferences;
  created_at: string;
  updated_at?: string | undefined;
}

export interface CreateCaregiverInput {
  name: string;
  phone: string;
  email: string;
  relationship: string;
  notification_preferences?: Partial<NotificationPreferences> | undefined;
}

export interface UpdateCaregiverInput {
  name?: string | undefined;
  phone?: string | undefined;
  email?: string | undefined;
  relationship?: "SON" | "DAUGHTER" | "SPOUSE" | "RELATIVE" | "FRIEND" | "OTHER" | undefined;
  notification_preferences?: Partial<NotificationPreferences> | undefined;
}

let mockCaregiversState: Caregiver[] = [
  {
    caregiver_id: "cg_rohit_01",
    elder_user_id: "usr_sunita_68",
    name: "Rohit Sharma",
    phone: "+91 98765 43210",
    email: "rohit.sharma@example.com",
    relationship: "SON",
    status: "VERIFIED",
    is_verified: true,
    is_active: true,
    isTrusted: true,
    notification_preferences: {
      sms_enabled: true,
      voice_enabled: true,
      high_risk_enabled: true,
      critical_risk_enabled: true,
      quiet_hours_enabled: false,
      quiet_hours_start: "22:00",
      quiet_hours_end: "07:00",
      max_notifications_per_hour: 5,
    },
    created_at: "2026-03-01T10:00:00Z",
  },
  {
    caregiver_id: "cg_priya_02",
    elder_user_id: "usr_sunita_68",
    name: "Priya Sharma",
    phone: "+91 98765 11223",
    email: "priya.sharma@example.com",
    relationship: "DAUGHTER",
    status: "VERIFIED",
    is_verified: true,
    is_active: true,
    isTrusted: true,
    notification_preferences: {
      sms_enabled: true,
      voice_enabled: false,
      high_risk_enabled: true,
      critical_risk_enabled: true,
      quiet_hours_enabled: true,
      quiet_hours_start: "22:00",
      quiet_hours_end: "07:00",
      max_notifications_per_hour: 3,
    },
    created_at: "2026-03-10T14:30:00Z",
  },
];

export const caregiverService = {
  async getCaregivers(): Promise<Caregiver[]> {
    if (isMockEnabled()) {
      return [...mockCaregiversState.filter((c) => c.is_active)];
    }
    try {
      const res = await apiClient.get<Caregiver[] | { caregivers: Caregiver[] }>("/caregivers");
      if (Array.isArray(res)) return res;
      if (res && Array.isArray((res as { caregivers: Caregiver[] }).caregivers)) {
        return (res as { caregivers: Caregiver[] }).caregivers;
      }
      return [];
    } catch {
      return [...mockCaregiversState.filter((c) => c.is_active)];
    }
  },

  async createCaregiver(input: CreateCaregiverInput): Promise<Caregiver> {
    if (isMockEnabled()) {
      const newCg: Caregiver = {
        caregiver_id: `cg_mock_${Date.now()}`,
        elder_user_id: "usr_sunita_68",
        name: input.name,
        phone: input.phone,
        email: input.email,
        relationship: (["SON", "DAUGHTER", "SPOUSE", "RELATIVE", "FRIEND", "OTHER"].includes(input.relationship.toUpperCase())
          ? (input.relationship.toUpperCase() as Caregiver["relationship"])
          : "OTHER"),
        status: "PENDING",
        is_verified: false,
        is_active: true,
        notification_preferences: {
          sms_enabled: true,
          voice_enabled: false,
          high_risk_enabled: true,
          critical_risk_enabled: true,
          quiet_hours_enabled: false,
          quiet_hours_start: "22:00",
          quiet_hours_end: "07:00",
          max_notifications_per_hour: 5,
          ...input.notification_preferences,
        },
        created_at: new Date().toISOString(),
      };
      mockCaregiversState = [newCg, ...mockCaregiversState];
      return newCg;
    }

    return await apiClient.post<Caregiver>("/caregivers", input);
  },

  async updateCaregiver(caregiverId: string, updates: UpdateCaregiverInput): Promise<Caregiver> {
    if (isMockEnabled()) {
      mockCaregiversState = mockCaregiversState.map((cg) => {
        if (cg.caregiver_id === caregiverId) {
          const updated: Caregiver = {
            ...cg,
            ...(updates.name ? { name: updates.name } : {}),
            ...(updates.phone ? { phone: updates.phone } : {}),
            ...(updates.email ? { email: updates.email } : {}),
            ...(updates.relationship ? { relationship: updates.relationship } : {}),
            notification_preferences: {
              ...cg.notification_preferences,
              ...(updates.notification_preferences || {}),
            },
            updated_at: new Date().toISOString(),
          };
          return updated;
        }
        return cg;
      });
      const found = mockCaregiversState.find((c) => c.caregiver_id === caregiverId);
      if (!found) throw new Error("Caregiver not found");
      return found;
    }

    return await apiClient.patch<Caregiver>(`/caregivers/${encodeURIComponent(caregiverId)}`, updates);
  },

  async deleteCaregiver(caregiverId: string): Promise<void> {
    if (isMockEnabled()) {
      mockCaregiversState = mockCaregiversState.filter((c) => c.caregiver_id !== caregiverId);
      return;
    }

    await apiClient.delete(`/caregivers/${encodeURIComponent(caregiverId)}`);
  },

  async verifyCaregiver(caregiverId: string, token?: string): Promise<Caregiver> {
    if (isMockEnabled()) {
      mockCaregiversState = mockCaregiversState.map((cg) => {
        if (cg.caregiver_id === caregiverId) {
          return {
            ...cg,
            status: "VERIFIED",
            is_verified: true,
            isTrusted: true,
            updated_at: new Date().toISOString(),
          };
        }
        return cg;
      });
      const found = mockCaregiversState.find((c) => c.caregiver_id === caregiverId);
      if (!found) throw new Error("Caregiver not found");
      return found;
    }

    return await apiClient.post<Caregiver>(`/caregivers/${encodeURIComponent(caregiverId)}/verify`, {
      token,
    });
  },
};
