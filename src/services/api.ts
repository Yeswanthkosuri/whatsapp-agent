/**
 * Base API client for the FastAPI backend.
 * Uses VITE_API_BASE_URL from environment variables.
 */
import type {
  Campaign,
  Conversation,
  DashboardStats,
  MediaAsset,
  Tenant,
  TenantSettings,
} from "@/types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const USE_MOCK = !BASE_URL;

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function request<T>(path: string, init?: RequestInit, fallback?: T): Promise<T> {
  if (USE_MOCK && fallback !== undefined) {
    await new Promise((r) => setTimeout(r, 120));
    return fallback;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!res.ok) {
    throw new ApiError(res.status, `API ${res.status}: ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export function isApiConfigured(): boolean {
  return Boolean(BASE_URL);
}

export const apiEndpoints = {
  health: () => request<{ status: string }>("/health"),
  tenants: () => request<Tenant[]>("/tenants"),
  dashboardStats: (tenantId: string) =>
    request<DashboardStats>(`/dashboard/stats?tenant=${encodeURIComponent(tenantId)}`),
  conversations: (tenantId: string) =>
    request<Conversation[]>(`/conversations?tenant=${encodeURIComponent(tenantId)}`),
  conversation: (id: string) => request<Conversation>(`/conversations/${id}`),
  campaigns: (tenantId: string) =>
    request<Campaign[]>(`/campaigns?tenant=${encodeURIComponent(tenantId)}`),
  createCampaign: (payload: Omit<Campaign, "id" | "status" | "recipients">) =>
    request<Campaign>("/campaigns", { method: "POST", body: JSON.stringify(payload) }),
  media: (tenantId?: string) =>
    request<MediaAsset[]>(
      tenantId ? `/media?tenant=${encodeURIComponent(tenantId)}` : "/media",
    ),
  settings: (tenantId: string) => request<TenantSettings>(`/settings/${tenantId}`),
  updateSettings: (tenantId: string, payload: TenantSettings) =>
    request<{ ok: true }>(`/settings/${tenantId}`, {
      method: "PUT",
      body: JSON.stringify({
        name: payload.tenantName,
        systemPrompt: payload.systemPrompt,
        mediaRules: payload.mediaRules,
      }),
    }),
};
