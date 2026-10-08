import { useQuery } from "@tanstack/react-query";
import { healthService, type HealthStatus } from "@/services/health-service";

export const healthKeys = {
  all: ["health"] as const,
  status: () => [...healthKeys.all, "status"] as const,
};

export function useHealthCheck() {
  return useQuery<HealthStatus>({
    queryKey: healthKeys.status(),
    queryFn: () => healthService.checkHealth(),
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
}
