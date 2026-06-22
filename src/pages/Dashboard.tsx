import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/stat-card";
import { useTenant } from "@/lib/tenant-store";
import { useChats } from "@/hooks/useChats";
import { MessagesSquare, Send, FileText, ImageIcon, UserCog } from "lucide-react";

export function Dashboard() {
  const { current } = useTenant();
  const { stats } = useChats(current.id);

  return (
    <AppShell>
      <div className="p-4 lg:p-8 max-w-7xl mx-auto space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold tracking-tight">Overview</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Real-time activity for <span className="font-medium text-foreground">{current.name}</span>
            </p>
          </div>
          <div className="text-xs text-muted-foreground">Live sync enabled</div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard label="Active Conversations" value={stats?.activeConversations ?? "—"} delta="+8% today" icon={MessagesSquare} tone="primary" />
          <StatCard label="Messages Today" value={stats?.messagesToday?.toLocaleString() ?? "—"} delta="+12%" icon={Send} tone="success" />
          <StatCard label="Documents Sent" value={stats?.documentsSent ?? "—"} icon={FileText} tone="accent" />
          <StatCard label="Images Sent" value={stats?.imagesSent ?? "—"} icon={ImageIcon} tone="accent" />
          <StatCard label="Human Handover" value={stats?.humanHandover ?? "—"} delta="-3 vs yesterday" icon={UserCog} tone="warning" />
        </div>

        <div className="grid lg:grid-cols-3 gap-4">
          <div className="glass-card rounded-2xl p-6 lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">Channel performance</h2>
              <span className="text-xs text-muted-foreground">Last 24h</span>
            </div>
            <div className="grid sm:grid-cols-3 gap-4">
              {[
                { label: "AI resolution rate", value: "82%" },
                { label: "Avg. response time", value: "1.4s" },
                { label: "CSAT score", value: "4.7 / 5" },
              ].map((item) => (
                <div key={item.label} className="rounded-xl border border-border bg-card/50 p-4">
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="text-2xl font-bold mt-1">{item.value}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="glass-card rounded-2xl p-6">
            <h2 className="font-semibold mb-4">Tenant snapshot</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Tenant ID</span><span className="font-mono text-xs">{current.id}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Plan</span><span className="font-semibold">{current.plan}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Channel</span><span className="font-semibold">WhatsApp Cloud</span></div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
