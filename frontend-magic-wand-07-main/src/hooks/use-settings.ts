import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { settingsService, type UserSettings } from "@/services/settings-service";

export const settingsKeys = {
  all: ["settings"] as const,
};

export function useSettings() {
  return useQuery({
    queryKey: settingsKeys.all,
    queryFn: () => settingsService.getSettings(),
    staleTime: 60_000,
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (newSettings: Partial<UserSettings>) =>
      settingsService.updateSettings(newSettings),
    onSuccess: (data) => {
      queryClient.setQueryData(settingsKeys.all, data);
    },
  });
}
