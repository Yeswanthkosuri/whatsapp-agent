import { createFileRoute } from "@tanstack/react-router";
import { Campaigns } from "@/pages/Campaigns";

export const Route = createFileRoute("/broadcast")({
  head: () => ({
    meta: [
      { title: "Broadcast Campaigns — WhatsApp AI Orchestrator" },
      { name: "description", content: "Compose and send WhatsApp broadcast campaigns to your audience." },
    ],
  }),
  component: Campaigns,
});
