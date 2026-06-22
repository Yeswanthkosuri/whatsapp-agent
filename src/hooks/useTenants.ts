import { useQuery } from "@tanstack/react-query";
import { tenantService } from "@/services/tenantService";

export function useTenants() {
  const query = useQuery({
    queryKey: ["tenants"],
    queryFn: () => tenantService.list(),
    staleTime: 60_000,
  });

  return {
    tenants: query.data ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

export function useTenantSettings(tenantId: string) {
  return useQuery({
    queryKey: ["settings", tenantId],
    queryFn: () => tenantService.settings(tenantId),
    enabled: Boolean(tenantId),
  });
}
