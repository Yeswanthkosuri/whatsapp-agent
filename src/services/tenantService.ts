/**
 * Tenant API service.
 */
import type { Tenant, TenantSettings } from "@/types";
import { apiEndpoints, request } from "./api";
import { tenants as mockTenants } from "@/lib/mock-data";

export const tenantService = {
  list: () => request<Tenant[]>("/tenants", undefined, mockTenants),

  settings: (tenantId: string) =>
    apiEndpoints.settings(tenantId).catch(() => ({
      tenantName: mockTenants.find((t) => t.id === tenantId)?.name ?? "",
      systemPrompt: "You are a helpful WhatsApp sales & support assistant.",
      mediaRules: "Only send images under 5MB. PDF attachments must be from the approved media library.",
    } satisfies TenantSettings)),

  updateSettings: (tenantId: string, payload: TenantSettings) =>
    apiEndpoints.updateSettings(tenantId, payload),
};
