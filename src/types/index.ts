/** Shared types for the WhatsApp AI Orchestrator frontend. */

export type Tenant = { id: string; name: string; plan: "Starter" | "Growth" | "Scale" };

export type DashboardStats = {
  activeConversations: number;
  messagesToday: number;
  documentsSent: number;
  imagesSent: number;
  humanHandover: number;
};

export type MessageType = "text" | "image" | "pdf";
export type Message = {
  id: string;
  from: "user" | "ai" | "agent";
  type: MessageType;
  content: string;
  meta?: { url?: string; filename?: string; size?: string };
  timestamp: string;
};

export type Conversation = {
  id: string;
  phone: string;
  name: string;
  tenantId: string;
  lastActivity: string;
  status: "active" | "waiting" | "handover" | "closed";
  unread: number;
  isTyping?: boolean;
  messages: Message[];
};

export type Campaign = {
  id: string;
  name: string;
  tenantId: string;
  audience: string;
  template: string;
  status: "draft" | "scheduled" | "sent";
  recipients: number;
  sentAt?: string;
};

export type MediaAsset = {
  id: string;
  type: "image" | "document";
  name: string;
  url: string;
  size: string;
  uploadedAt: string;
  tenantId?: string;
};

export type TenantSettings = {
  tenantName: string;
  systemPrompt: string;
  mediaRules: string;
};
