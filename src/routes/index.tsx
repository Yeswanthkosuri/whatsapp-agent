import { createFileRoute } from "@tanstack/react-router";
import { Dashboard } from "@/pages/Dashboard";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — WhatsApp AI Orchestrator" },
      { name: "description", content: "Multi-tenant WhatsApp AI support & sales overview." },
    ],
  }),
  component: Dashboard,
});
