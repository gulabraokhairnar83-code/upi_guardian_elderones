import { useMutation, useQuery } from "@tanstack/react-query";
import {
  messageService,
  type AnalyzeMessagePayload,
} from "@/services/message-service";

export function useAnalyzeMessage() {
  return useMutation({
    mutationFn: (payload: AnalyzeMessagePayload) =>
      messageService.analyzeMessage(payload),
  });
}

export function useSampleMessage(type: "sms" | "call") {
  return useQuery({
    queryKey: ["sample-message", type],
    queryFn: () => messageService.getSampleMessage(type),
    staleTime: Infinity,
  });
}
