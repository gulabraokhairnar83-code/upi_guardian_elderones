import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  riskService,
  type RiskAnalysisRequestPayload,
  type RiskFusionAnalysis,
  type RiskEvent,
} from "@/services/risk-service";

export const riskKeys = {
  all: ["risk"] as const,
  events: (userId?: string, limit?: number) =>
    [...riskKeys.all, "events", userId ?? "usr_sunita_68", limit ?? 20] as const,
};

export function useRiskAnalysis() {
  const queryClient = useQueryClient();
  return useMutation<RiskFusionAnalysis, Error, RiskAnalysisRequestPayload>({
    mutationFn: (payload: RiskAnalysisRequestPayload) => riskService.analyzeRisk(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: riskKeys.all });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}

export function useRiskEvents(userId = "usr_sunita_68", limit = 20) {
  return useQuery<RiskEvent[]>({
    queryKey: riskKeys.events(userId, limit),
    queryFn: () => riskService.getRiskEvents(userId, limit),
    staleTime: 30_000,
  });
}
