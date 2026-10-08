import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { alertService } from "@/services/alert-service";

export const alertKeys = {
  all: ["alerts"] as const,
  list: (level?: string) => [...alertKeys.all, "list", level ?? "all"] as const,
};

export function useAlerts(level?: string) {
  return useQuery({
    queryKey: alertKeys.list(level),
    queryFn: () => alertService.getAlerts(level),
    staleTime: 30_000,
  });
}

export function useResolveAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => alertService.resolveAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.all });
    },
  });
}
