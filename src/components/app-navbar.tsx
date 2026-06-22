import { Bell, ChevronDown, Search } from "lucide-react";
import { useTenant } from "@/lib/tenant-store";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function AppNavbar() {
  const { current, all, setCurrent } = useTenant();
  return (
    <header className="h-16 shrink-0 border-b border-border bg-background/70 backdrop-blur-xl sticky top-0 z-30">
      <div className="h-full px-4 lg:px-6 flex items-center gap-3">
        <div className="lg:hidden font-semibold text-sm truncate max-w-[160px]">
          WhatsApp AI Orchestrator
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="gap-2 rounded-full">
              <span className="h-2 w-2 rounded-full bg-primary" />
              <span className="truncate max-w-[140px]">{current.name}</span>
              <Badge variant="secondary" className="hidden sm:inline-flex">{current.plan}</Badge>
              <ChevronDown className="h-4 w-4 opacity-60" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-64">
            <DropdownMenuLabel>Switch tenant</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {all.map((t) => (
              <DropdownMenuItem key={t.id} onClick={() => setCurrent(t)}>
                <div className="flex-1">
                  <div className="font-medium">{t.name}</div>
                  <div className="text-xs text-muted-foreground">{t.plan}</div>
                </div>
                {t.id === current.id && <span className="text-xs text-primary">Active</span>}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <div className="relative hidden md:flex flex-1 max-w-md ml-2">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            placeholder="Search conversations, contacts, campaigns…"
            className="w-full h-10 pl-9 pr-3 rounded-full bg-muted/60 border border-transparent focus:bg-background focus:border-border outline-none text-sm transition-colors"
          />
        </div>

        <div className="flex-1 md:hidden" />

        <Button variant="ghost" size="icon" className="relative rounded-full">
          <Bell className="h-5 w-5" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-destructive" />
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 pl-1 pr-2 py-1 rounded-full hover:bg-muted transition-colors">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary text-primary-foreground text-xs">AB</AvatarFallback>
              </Avatar>
              <div className="hidden sm:block text-left leading-tight">
                <div className="text-xs font-semibold">Alex Brooks</div>
                <div className="text-[10px] text-muted-foreground">Admin</div>
              </div>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>My account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Billing</DropdownMenuItem>
            <DropdownMenuItem>Sign out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
