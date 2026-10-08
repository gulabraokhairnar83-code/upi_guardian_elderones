import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  transactionService,
  type AnalyzeTransactionPayload,
  type Transaction,
} from "@/services/transaction-service";

export const transactionKeys = {
  all: ["transactions"] as const,
  lists: () => [...transactionKeys.all, "list"] as const,
  list: (filter?: { status?: string; query?: string }) =>
    [...transactionKeys.lists(), filter] as const,
  details: () => [...transactionKeys.all, "detail"] as const,
  detail: (id: string) => [...transactionKeys.details(), id] as const,
};

export function useTransactions(filter?: { status?: string; query?: string }) {
  return useQuery({
    queryKey: transactionKeys.list(filter),
    queryFn: () => transactionService.getTransactions(filter),
    staleTime: 60_000,
  });
}

export function useTransaction(id: string | null) {
  return useQuery({
    queryKey: id ? transactionKeys.detail(id) : ["transactions", "detail", "empty"],
    queryFn: () => (id ? transactionService.getTransactionById(id) : Promise.resolve(null)),
    enabled: Boolean(id),
    staleTime: 60_000,
  });
}

export function useAnalyzeTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: AnalyzeTransactionPayload) =>
      transactionService.analyzeTransaction(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: transactionKeys.all });
    },
  });
}
