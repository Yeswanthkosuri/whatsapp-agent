import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { useTenant } from "@/lib/tenant-store";
import { useTenantSettings } from "@/hooks/useTenants";
import { tenantService } from "@/services/tenantService";
import { Button } from "@/components/ui/button";
import { Settings as SettingsIcon } from "lucide-react";
import { toast } from "sonner";

export function Settings() {
  const { current } = useTenant();
  const { data } = useTenantSettings(current.id);
  const [form, setForm] = useState({ tenantName: "", systemPrompt: "", mediaRules: "" });

  useEffect(() => {
    if (data) setForm(data);
  }, [data]);

  const save = useMutation({
    mutationFn: () => tenantService.updateSettings(current.id, form),
    onSuccess: () => toast.success("Settings saved"),
  });

  return (
    <AppShell>
      <div className="p-4 lg:p-8 max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Tenant configuration for <span className="font-medium text-foreground">{current.name}</span>.
          </p>
        </div>

        <div className="glass-card rounded-2xl p-6 space-y-5">
          <div className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5 text-primary" />
            <h2 className="font-semibold">Tenant configuration</h2>
          </div>

          <Field label="Tenant name" hint="Visible to your team only.">
            <input
              value={form.tenantName}
              onChange={(e) => setForm({ ...form, tenantName: e.target.value })}
              className="w-full h-10 px-3 rounded-lg border border-border bg-background text-sm outline-none focus:border-primary"
            />
          </Field>

          <Field label="System prompt" hint="Instructions that define how the AI agent behaves.">
            <textarea
              rows={6}
              value={form.systemPrompt}
              onChange={(e) => setForm({ ...form, systemPrompt: e.target.value })}
              className="w-full p-3 rounded-lg border border-border bg-background text-sm outline-none focus:border-primary font-mono"
            />
          </Field>

          <Field label="Media rules" hint="Restrictions on what files the AI can send.">
            <textarea
              rows={4}
              value={form.mediaRules}
              onChange={(e) => setForm({ ...form, mediaRules: e.target.value })}
              className="w-full p-3 rounded-lg border border-border bg-background text-sm outline-none focus:border-primary"
            />
          </Field>

          <div className="flex justify-end gap-2 pt-2 border-t border-border">
            <Button variant="outline" onClick={() => data && setForm(data)}>Reset</Button>
            <Button onClick={() => save.mutate()} disabled={save.isPending}>
              {save.isPending ? "Saving…" : "Save changes"}
            </Button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <div className="flex items-baseline justify-between">
        <span className="text-sm font-semibold">{label}</span>
        {hint && <span className="text-xs text-muted-foreground">{hint}</span>}
      </div>
      <div className="mt-2">{children}</div>
    </label>
  );
}
