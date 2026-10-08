import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { familyService } from "@/services/family-service";

export const familyKeys = {
  all: ["family"] as const,
  profile: () => [...familyKeys.all, "profile"] as const,
  contacts: () => [...familyKeys.all, "contacts"] as const,
};

export function useFamily() {
  const profileQuery = useQuery({
    queryKey: familyKeys.profile(),
    queryFn: () => familyService.getElderProfile(),
    staleTime: 30_000,
  });

  const contactsQuery = useQuery({
    queryKey: familyKeys.contacts(),
    queryFn: () => familyService.getEmergencyContacts(),
    staleTime: 60_000,
  });

  return {
    profile: profileQuery.data,
    contacts: contactsQuery.data,
    isLoading: profileQuery.isLoading || contactsQuery.isLoading,
    isError: profileQuery.isError || contactsQuery.isError,
    error: profileQuery.error || contactsQuery.error,
    refetch: () => {
      profileQuery.refetch();
      contactsQuery.refetch();
    },
  };
}

export function useResolveFamilyAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => familyService.resolveFamilyAlert(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: familyKeys.all });
    },
  });
}
