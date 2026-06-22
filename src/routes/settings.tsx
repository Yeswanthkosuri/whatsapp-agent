import { createFileRoute } from "@tanstack/react-router";
import { Settings } from "@/pages/Settings";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — WhatsApp AI Orchestrator" },
      { name: "description", content: "Configure tenant identity, AI system prompt, and media rules." },
    ],
  }),
  component: Settings,
});
