import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

type Props = {
  label: string;
  value: string | number;
  delta?: string;
  icon: LucideIcon;
  tone?: "primary" | "accent" | "warning" | "success";
};

const toneMap: Record<NonNullable<Props["tone"]>, string> = {
  primary: "bg-primary/10 text-primary",
  accent: "bg-accent text-accent-foreground",
  warning: "bg-warning/15 text-warning-foreground",
  success: "bg-success/15 text-success",
};

export function StatCard({ label, value, delta, icon: Icon, tone = "primary" }: Props) {
  return (
    <div className="glass-card rounded-2xl p-5 animate-fade-in">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</div>
          <div className="mt-2 text-3xl font-bold tracking-tight">{value}</div>
          {delta && <div className="mt-1 text-xs text-success font-medium">{delta}</div>}
        </div>
        <div className={cn("h-11 w-11 grid place-items-center rounded-xl shrink-0", toneMap[tone])}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
