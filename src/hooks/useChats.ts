import { useQuery } from "@tanstack/react-query";
import { chatService } from "@/services/chatService";

export function useChats(tenantId: string) {
  const listQuery = useQuery({
    queryKey: ["conversations", tenantId],
    queryFn: () => chatService.list(tenantId),
    enabled: Boolean(tenantId),
    refetchInterval: 5000,
  });

  const statsQuery = useQuery({
    queryKey: ["stats", tenantId],
    queryFn: () => chatService.stats(tenantId),
    enabled: Boolean(tenantId),
    refetchInterval: 10000,
  });

  return {
    conversations: listQuery.data ?? [],
    stats: statsQuery.data,
    isLoading: listQuery.isLoading,
    isError: listQuery.isError,
    refetch: listQuery.refetch,
  };
}

export function useChat(sessionId: string | null) {
  return useQuery({
    queryKey: ["conversation", sessionId],
    queryFn: () => (sessionId ? chatService.get(sessionId) : undefined),
    enabled: Boolean(sessionId),
    refetchInterval: 3000,
  });
}
