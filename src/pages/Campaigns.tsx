import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { apiEndpoints } from "@/services/api";
import { campaigns as mockCampaigns } from "@/lib/mock-data";
import { useTenant } from "@/lib/tenant-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Megaphone, Send } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { request } from "@/services/api";
import type { Campaign } from "@/types";

const audiences = ["All customers", "Active last 7 days", "VIP segment", "Cart abandoners"];
const templates = ["spring_sale_v2", "appt_reminder", "service_followup", "new_arrival"];

export function Campaigns() {
  const { current, all } = useTenant();
  const qc = useQueryClient();
  const { data: list = [] } = useQuery({
    queryKey: ["campaigns", current.id],
    queryFn: () =>
      request<Campaign[]>(
        `/campaigns?tenant=${encodeURIComponent(current.id)}`,
        undefined,
        mockCampaigns.filter((c) => c.tenantId === current.id),
      ),
  });

  const [form, setForm] = useState({
    name: "",
    tenantId: current.id,
    audience: audiences[0],
    template: templates[0],
  });

  const create = useMutation({
    mutationFn: () => apiEndpoints.createCampaign(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["campaigns", current.id] });
      toast.success("Campaign scheduled");
      setForm({ ...form, name: "" });
    },
  });

  return (
    <AppShell>
      <div className="p-4 lg:p-8 max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight">Broadcast Campaigns</h1>
          <p className="text-sm text-muted-foreground mt-1">Reach the right audience with approved WhatsApp templates.</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2">
              <Megaphone className="h-5 w-5 text-primary" />
              <h2 className="font-semibold">New campaign</h2>
            </div>
            <Field label="Campaign name">
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Spring promo" className="input" />
            </Field>
            <Field label="Tenant">
              <select value={form.tenantId} onChange={(e) => setForm({ ...form, tenantId: e.target.value })} className="input">
                {all.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </Field>
            <Field label="Audience">
              <select value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })} className="input">
                {audiences.map((a) => <option key={a}>{a}</option>)}
              </select>
            </Field>
            <Field label="Message template">
              <select value={form.template} onChange={(e) => setForm({ ...form, template: e.target.value })} className="input">
                {templates.map((t) => <option key={t}>{t}</option>)}
              </select>
            </Field>
            <Button onClick={() => create.mutate()} disabled={!form.name || create.isPending} className="w-full gap-2 rounded-xl">
              <Send className="h-4 w-4" />
              {create.isPending ? "Scheduling…" : "Send broadcast"}
            </Button>
            <style>{`.input { width: 100%; height: 2.5rem; padding: 0 0.75rem; border-radius: 0.625rem; border: 1px solid var(--border); background: var(--background); font-size: 0.875rem; outline: none; }
            .input:focus { border-color: var(--primary); }`}</style>
          </div>

          <div className="glass-card rounded-2xl p-6">
            <h2 className="font-semibold mb-4">Recent campaigns</h2>
            <div className="space-y-3">
              {list.map((c) => (
                <div key={c.id} className="flex items-center gap-3 p-3 rounded-xl border border-border bg-card/50">
                  <div className="h-10 w-10 grid place-items-center rounded-lg bg-primary/10 text-primary shrink-0">
                    <Megaphone className="h-5 w-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="font-medium text-sm truncate">{c.name}</div>
                    <div className="text-xs text-muted-foreground">{c.audience} · {c.template}</div>
                  </div>
                  <div className="text-right">
                    <Badge variant="secondary" className={cn(c.status === "sent" && "bg-success/15 text-success", c.status === "scheduled" && "bg-warning/20 text-warning-foreground", c.status === "draft" && "bg-muted")}>
                      {c.status}
                    </Badge>
                    <div className="text-[11px] text-muted-foreground mt-1">{c.recipients.toLocaleString()} recipients</div>
                  </div>
                </div>
              ))}
              {list.length === 0 && <div className="text-sm text-muted-foreground text-center py-8">No campaigns yet.</div>}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}
