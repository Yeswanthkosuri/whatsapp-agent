import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { apiEndpoints } from "@/services/api";
import { mediaAssets as mockMedia } from "@/lib/mock-data";
import { useTenant } from "@/lib/tenant-store";
import { FileText, ImageIcon, Search, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function MediaLibrary() {
  const { current } = useTenant();
  const { data = [] } = useQuery({
    queryKey: ["media", current.id],
    queryFn: () => apiEndpoints.media(current.id).catch(() => mockMedia.filter((m) => m.tenantId === current.id)),
  });
  const [search, setSearch] = useState("");
  const [tab, setTab] = useState<"all" | "image" | "document">("all");

  const filtered = useMemo(
    () =>
      data.filter(
        (a) =>
          (tab === "all" || a.type === tab) &&
          a.name.toLowerCase().includes(search.toLowerCase()),
      ),
    [data, search, tab],
  );

  return (
    <AppShell>
      <div className="p-4 lg:p-8 max-w-7xl mx-auto space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold tracking-tight">Media Library</h1>
            <p className="text-sm text-muted-foreground mt-1">Images and documents available to your AI agent for {current.name}.</p>
          </div>
          <Button className="gap-2 rounded-xl"><Upload className="h-4 w-4" />Upload</Button>
        </div>

        <div className="glass-card rounded-2xl p-4 lg:p-6 space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search assets"
                className="w-full h-10 pl-9 pr-3 rounded-lg bg-muted/60 border border-transparent focus:bg-background focus:border-border outline-none text-sm"
              />
            </div>
            <div className="flex rounded-lg border border-border p-1 bg-background">
              {(["all", "image", "document"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium rounded-md capitalize transition-colors",
                    tab === t ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {t === "all" ? "All" : t + "s"}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filtered.map((a) => (
              <div key={a.id} className="group rounded-xl border border-border bg-card overflow-hidden hover:shadow-md transition-shadow">
                <div className="aspect-square bg-muted grid place-items-center overflow-hidden">
                  {a.type === "image" ? (
                    <img src={a.url} alt={a.name} className="h-full w-full object-cover group-hover:scale-105 transition-transform" />
                  ) : (
                    <FileText className="h-12 w-12 text-muted-foreground" />
                  )}
                </div>
                <div className="p-3">
                  <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground mb-1">
                    {a.type === "image" ? <ImageIcon className="h-3 w-3" /> : <FileText className="h-3 w-3" />}
                    <span className="uppercase tracking-wide">{a.type}</span>
                    <span>·</span>
                    <span>{a.size}</span>
                  </div>
                  <div className="text-sm font-medium truncate">{a.name}</div>
                </div>
              </div>
            ))}
          </div>
          {filtered.length === 0 && (
            <div className="text-sm text-muted-foreground text-center py-12">No assets match your filters.</div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
