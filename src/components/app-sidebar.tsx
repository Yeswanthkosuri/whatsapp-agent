import { Link, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, MessagesSquare, Megaphone, Images, Settings, Bot } from "lucide-react";
import { cn } from "@/lib/utils";

const nav: Array<{ to: string; label: string; icon: typeof LayoutDashboard; exact?: boolean }> = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/conversations", label: "Conversations", icon: MessagesSquare },
  { to: "/broadcast", label: "Broadcast Campaigns", icon: Megaphone },
  { to: "/media", label: "Media Library", icon: Images },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function AppSidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <aside className="hidden lg:flex flex-col w-64 shrink-0 border-r border-sidebar-border bg-sidebar/80 backdrop-blur-xl">
      <div className="h-16 flex items-center gap-2 px-6 border-b border-sidebar-border">
        <div className="grid place-items-center h-9 w-9 rounded-xl bg-primary text-primary-foreground shadow-sm">
          <Bot className="h-5 w-5" />
        </div>
        <div className="leading-tight min-w-0">
          <div className="font-semibold text-sm truncate">WhatsApp AI Orchestrator</div>
          <div className="text-[11px] text-muted-foreground truncate">Multi-Tenant SaaS</div>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {nav.map((item) => {
          const active = item.exact ? pathname === item.to : pathname.startsWith(item.to);
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground",
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span className="truncate">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 m-3 rounded-xl glass-card text-xs">
        <div className="font-semibold mb-1">Production ready</div>
        <div className="text-muted-foreground">FastAPI · LangGraph · MongoDB Atlas · WhatsApp Cloud API</div>
      </div>
    </aside>
  );
}
