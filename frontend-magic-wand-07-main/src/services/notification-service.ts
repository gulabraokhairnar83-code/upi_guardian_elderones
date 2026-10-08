/**
 * UPI Guardian - Notification Service
 * Telemetry and dispatch records for Twilio SMS / Voice alerts and caregiver acknowledgements.
 */

import { apiClient, isMockEnabled } from "./api-client";

export interface NotificationRecord {
  notification_id: string;
  user_id: string;
  elder_user_id?: string;
  caregiver_id: string;
  caregiver_user_id?: string;
  transaction_id?: string;
  risk_event_id?: string;
  channel: "SMS" | "VOICE";
  notification_type: "RISK_ALERT" | "EMERGENCY_ESCALATION";
  risk_level: "HIGH" | "CRITICAL";
  status: "PENDING" | "SENDING" | "SENT" | "DELIVERED" | "FAILED" | "CANCELLED";
  provider_message_id?: string;
  message_preview?: string;
  is_acknowledged: boolean;
  acknowledged_at?: string;
  acknowledged_by?: string;
  error_code?: string;
  created_at: string;
  sent_at?: string;
}

let mockNotificationsState: NotificationRecord[] = [
  {
    notification_id: "notif_sms_demo01",
    user_id: "usr_sunita_68",
    caregiver_id: "cg_rohit_01",
    transaction_id: "TXN-UG-902",
    risk_event_id: "evt_demo_902",
    channel: "SMS",
    notification_type: "EMERGENCY_ESCALATION",
    risk_level: "CRITICAL",
    status: "SENT",
    provider_message_id: "SM_MOCK_8891238912",
    message_preview: "UPI Guardian Alert: Critical-risk activity detected for Sunita Devi. Risk Score: 92/100...",
    is_acknowledged: false,
    created_at: "2026-03-12T11:42:00Z",
    sent_at: "2026-03-12T11:42:05Z",
  },
  {
    notification_id: "notif_voice_demo02",
    user_id: "usr_sunita_68",
    caregiver_id: "cg_rohit_01",
    transaction_id: "TXN-UG-902",
    risk_event_id: "evt_demo_902",
    channel: "VOICE",
    notification_type: "EMERGENCY_ESCALATION",
    risk_level: "CRITICAL",
    status: "SENT",
    provider_message_id: "CA_MOCK_7712399120",
    message_preview: "Automated voice alert dispatched to +91 98765 43210",
    is_acknowledged: false,
    created_at: "2026-03-12T11:43:00Z",
    sent_at: "2026-03-12T11:43:03Z",
  },
];

export const notificationService = {
  async getNotifications(limit = 50): Promise<NotificationRecord[]> {
    if (isMockEnabled()) {
      return [...mockNotificationsState];
    }
    try {
      const res = await apiClient.get<NotificationRecord[] | { notifications: NotificationRecord[] }>(
        "/notifications",
        { params: { limit } }
      );
      if (Array.isArray(res)) return res;
      if (res && Array.isArray((res as { notifications: NotificationRecord[] }).notifications)) {
        return (res as { notifications: NotificationRecord[] }).notifications;
      }
      return [];
    } catch {
      return [...mockNotificationsState];
    }
  },

  async acknowledgeNotification(notificationId: string): Promise<NotificationRecord> {
    if (isMockEnabled()) {
      mockNotificationsState = mockNotificationsState.map((n) => {
        if (n.notification_id === notificationId) {
          return {
            ...n,
            is_acknowledged: true,
            acknowledged_at: new Date().toISOString(),
            acknowledged_by: "Current Caregiver",
          };
        }
        return n;
      });
      const found = mockNotificationsState.find((n) => n.notification_id === notificationId);
      if (!found) throw new Error("Notification not found");
      return found;
    }

    return await apiClient.post<NotificationRecord>(
      `/notifications/${encodeURIComponent(notificationId)}/acknowledge`
    );
  },

  async triggerEscalation(payload: unknown): Promise<{ triggered: boolean; message?: string }> {
    if (isMockEnabled()) {
      return { triggered: true, message: "Mock escalation dispatched." };
    }
    return await apiClient.post<{ triggered: boolean; message?: string }>("/notifications/escalate", payload);
  },
};
