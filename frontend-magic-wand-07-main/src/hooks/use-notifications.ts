/**
 * UPI Guardian - Notifications Query & Mutation Hooks
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  notificationService,
  type NotificationRecord,
} from "@/services/notification-service";

export const NOTIFICATIONS_QUERY_KEY = ["notifications"] as const;

export function useNotifications(limit = 50) {
  return useQuery({
    queryKey: [...NOTIFICATIONS_QUERY_KEY, limit],
    queryFn: () => notificationService.getNotifications(limit),
    staleTime: 1000 * 15, // 15s
  });
}

export function useAcknowledgeNotification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (notificationId: string) =>
      notificationService.acknowledgeNotification(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_QUERY_KEY });
    },
  });
}
