/**
 * UPI Guardian - Caregivers Query & Mutation Hooks
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  caregiverService,
  type Caregiver,
  type CreateCaregiverInput,
  type UpdateCaregiverInput,
} from "@/services/caregiver-service";

export const CAREGIVERS_QUERY_KEY = ["caregivers"] as const;

export function useCaregivers() {
  return useQuery({
    queryKey: CAREGIVERS_QUERY_KEY,
    queryFn: () => caregiverService.getCaregivers(),
    staleTime: 1000 * 30, // 30s
  });
}

export function useCreateCaregiver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateCaregiverInput) => caregiverService.createCaregiver(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CAREGIVERS_QUERY_KEY });
    },
  });
}

export function useUpdateCaregiver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: UpdateCaregiverInput }) =>
      caregiverService.updateCaregiver(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CAREGIVERS_QUERY_KEY });
    },
  });
}

export function useDeleteCaregiver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => caregiverService.deleteCaregiver(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CAREGIVERS_QUERY_KEY });
    },
  });
}

export function useVerifyCaregiver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, token }: { id: string; token?: string }) =>
      caregiverService.verifyCaregiver(id, token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CAREGIVERS_QUERY_KEY });
    },
  });
}
