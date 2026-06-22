import { createFileRoute } from "@tanstack/react-router";
import { MediaLibrary } from "@/pages/MediaLibrary";

export const Route = createFileRoute("/media")({
  head: () => ({
    meta: [
      { title: "Media Library — WhatsApp AI Orchestrator" },
      { name: "description", content: "Manage images and documents your AI agent can share." },
    ],
  }),
  component: MediaLibrary,
});
