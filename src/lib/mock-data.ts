// Mock data fallback when VITE_API_BASE_URL is not set.
import type {
  Tenant,
  DashboardStats,
  Conversation,
  Campaign,
  MediaAsset,
} from "@/types";

export const tenants: Tenant[] = [
  { id: "tenantA", name: "Luxury Furniture", plan: "Growth" },
  { id: "tenantB", name: "Automotive Care", plan: "Scale" },
];

export const stats: DashboardStats = {
  activeConversations: 124,
  messagesToday: 3820,
  documentsSent: 312,
  imagesSent: 845,
  humanHandover: 18,
};

const now = Date.now();
const t = (m: number) => new Date(now - m * 60_000).toISOString();

export const conversations: Conversation[] = [
  {
    id: "c1",
    phone: "+1 415 555 0142",
    name: "Sarah Chen",
    tenantId: "tenantA",
    lastActivity: t(2),
    status: "active",
    unread: 2,
    isTyping: true,
    messages: [
      { id: "m1", from: "user", type: "text", content: "Hi, do you have the new linen sofas in stock?", timestamp: t(8) },
      { id: "m2", from: "ai", type: "text", content: "Hello Sarah! Yes, our luxury sofa collection just arrived. Would you like sizes or colors?", timestamp: t(7) },
      { id: "m3", from: "user", type: "text", content: "Show me the sofa please", timestamp: t(5) },
      { id: "m4", from: "ai", type: "image", content: "Luxury sofa", meta: { url: "https://picsum.photos/400" }, timestamp: t(4) },
      { id: "m5", from: "ai", type: "pdf", content: "Product catalog", meta: { filename: "catalog.pdf", size: "412 KB" }, timestamp: t(3) },
    ],
  },
  {
    id: "c2",
    phone: "+44 20 7946 0991",
    name: "James Whitaker",
    tenantId: "tenantB",
    lastActivity: t(11),
    status: "waiting",
    unread: 0,
    messages: [
      { id: "m1", from: "user", type: "text", content: "Can I get my service invoice?", timestamp: t(14) },
      { id: "m2", from: "ai", type: "text", content: "Of course. I'll send your invoice right away.", timestamp: t(13) },
    ],
  },
  {
    id: "c3",
    phone: "+34 91 555 0177",
    name: "María García",
    tenantId: "tenantB",
    lastActivity: t(34),
    status: "handover",
    unread: 5,
    messages: [
      { id: "m1", from: "user", type: "text", content: "There's a noise from the brakes after service.", timestamp: t(40) },
      { id: "m2", from: "ai", type: "text", content: "I'm escalating this to a human agent right away.", timestamp: t(39) },
      { id: "m3", from: "agent", type: "text", content: "Hi María, this is Diego from service. Can you describe the noise?", timestamp: t(35) },
    ],
  },
];

export const campaigns: Campaign[] = [
  { id: "cm1", name: "Spring Collection Launch", tenantId: "tenantA", audience: "All customers", template: "spring_sale_v2", status: "sent", recipients: 1240, sentAt: t(60 * 24) },
  { id: "cm2", name: "Service Reminder", tenantId: "tenantB", audience: "Upcoming this week", template: "service_followup", status: "scheduled", recipients: 312 },
];

export const mediaAssets: MediaAsset[] = [
  { id: "a1", type: "image", name: "sofa", url: "https://picsum.photos/400", size: "182 KB", uploadedAt: t(60 * 5), tenantId: "tenantA" },
  { id: "a2", type: "document", name: "catalog", url: "https://example.com/catalog.pdf", size: "412 KB", uploadedAt: t(60 * 12), tenantId: "tenantA" },
  { id: "a3", type: "image", name: "repair", url: "https://picsum.photos/500", size: "240 KB", uploadedAt: t(60 * 8), tenantId: "tenantB" },
  { id: "a4", type: "document", name: "invoice", url: "https://example.com/invoice.pdf", size: "98 KB", uploadedAt: t(60 * 30), tenantId: "tenantB" },
];
