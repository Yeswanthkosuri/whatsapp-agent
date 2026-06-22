import { createFileRoute } from "@tanstack/react-router";
import { Conversations } from "@/pages/Conversations";

export const Route = createFileRoute("/conversations")({
  head: () => ({
    meta: [
      { title: "Conversations — WhatsApp AI Orchestrator" },
      { name: "description", content: "Browse live WhatsApp conversations handled by your AI." },
    ],
  }),
  component: Conversations,
});
