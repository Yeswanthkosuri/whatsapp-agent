/**
 * Chat and conversation API service.
 */
import type { Conversation } from "@/types";
import { apiEndpoints, request } from "./api";
import { conversations as mockConversations } from "@/lib/mock-data";

export const chatService = {
  list: (tenantId: string) =>
    request<Conversation[]>(
      `/conversations?tenant=${encodeURIComponent(tenantId)}`,
      undefined,
      mockConversations.filter((c) => c.tenantId === tenantId),
    ),

  get: (id: string) =>
    request<Conversation | undefined>(
      `/conversations/${id}`,
      undefined,
      mockConversations.find((c) => c.id === id),
    ),

  stats: apiEndpoints.dashboardStats,
};
