import { useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { useTenant } from "@/lib/tenant-store";
import { useChats } from "@/hooks/useChats";
import type { Conversation, Message } from "@/types";
import { Search, FileText, Send, Paperclip, Smile } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusTone: Record<Conversation["status"], string> = {
  active: "bg-success/15 text-success",
  waiting: "bg-warning/20 text-warning-foreground",
  handover: "bg-destructive/15 text-destructive",
  closed: "bg-muted text-muted-foreground",
};

export function Conversations() {
  const { current } = useTenant();
  const { conversations: list } = useChats(current.id);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filtered = useMemo(
    () => list.filter((c) => (c.name + c.phone).toLowerCase().includes(search.toLowerCase())),
    [list, search],
  );
  const selected = filtered.find((c) => c.id === selectedId) ?? filtered[0];

  return (
    <AppShell>
      <div className="h-[calc(100vh-4rem)] flex">
        <div className={cn("w-full md:w-80 lg:w-96 shrink-0 border-r border-border bg-card/60 backdrop-blur-xl flex flex-col", selected && "hidden md:flex")}>
          <div className="p-4 border-b border-border">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by name or phone"
                className="w-full h-10 pl-9 pr-3 rounded-lg bg-muted/60 border border-transparent focus:bg-background focus:border-border outline-none text-sm"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {filtered.map((c) => {
              const last = c.messages[c.messages.length - 1];
              return (
                <button
                  key={c.id}
                  onClick={() => setSelectedId(c.id)}
                  className={cn(
                    "w-full text-left px-4 py-3 flex gap-3 border-b border-border/60 hover:bg-muted/50 transition-colors",
                    selected?.id === c.id && "bg-muted/70",
                  )}
                >
                  <Avatar className="h-10 w-10 shrink-0">
                    <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                      {c.name.split(" ").map((n) => n[0]).join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm truncate">{c.name}</span>
                      <span className="text-[10px] text-muted-foreground shrink-0">
                        {new Date(c.lastActivity).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-2 mt-0.5">
                      <span className="text-xs text-muted-foreground truncate">
                        {last?.type === "text" ? last.content : last?.type === "image" ? "📷 Image" : "📎 Document"}
                      </span>
                      {c.unread > 0 && (
                        <span className="h-5 min-w-5 px-1.5 grid place-items-center rounded-full bg-primary text-primary-foreground text-[10px] font-bold">
                          {c.unread}
                        </span>
                      )}
                    </div>
                    <Badge variant="secondary" className={cn("mt-1 text-[10px] font-medium", statusTone[c.status])}>
                      {c.status}
                    </Badge>
                  </div>
                </button>
              );
            })}
            {filtered.length === 0 && (
              <div className="p-6 text-sm text-muted-foreground text-center">No conversations yet.</div>
            )}
          </div>
        </div>

        <div className={cn("flex-1 flex flex-col min-w-0", !selected && "hidden md:flex")}>
          {selected ? (
            <ChatThread conversation={selected} onBack={() => setSelectedId(null)} />
          ) : (
            <div className="flex-1 grid place-items-center text-sm text-muted-foreground">Select a conversation</div>
          )}
        </div>

        {selected && (
          <aside className="hidden xl:flex w-80 shrink-0 border-l border-border bg-card/60 backdrop-blur-xl flex-col">
            <CustomerPanel conversation={selected} />
          </aside>
        )}
      </div>
    </AppShell>
  );
}

function ChatThread({ conversation, onBack }: { conversation: Conversation; onBack: () => void }) {
  return (
    <>
      <div className="h-16 border-b border-border px-4 flex items-center gap-3 bg-background/70 backdrop-blur-xl">
        <button onClick={onBack} className="md:hidden text-sm text-primary">← Back</button>
        <Avatar className="h-9 w-9">
          <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
            {conversation.name.split(" ").map((n) => n[0]).join("")}
          </AvatarFallback>
        </Avatar>
        <div className="min-w-0">
          <div className="font-semibold text-sm truncate">{conversation.name}</div>
          <div className="text-xs text-muted-foreground truncate">{conversation.phone}</div>
        </div>
        <Badge variant="secondary" className={cn("ml-auto", statusTone[conversation.status])}>
          {conversation.status}
        </Badge>
      </div>

      <div
        className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-3"
        style={{
          backgroundImage:
            "radial-gradient(circle at 20px 20px, color-mix(in oklab, var(--primary) 6%, transparent) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      >
        {conversation.messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {conversation.isTyping && <TypingIndicator />}
      </div>

      <div className="border-t border-border p-3 bg-background/80 backdrop-blur-xl">
        <div className="flex items-end gap-2">
          <button className="h-10 w-10 grid place-items-center rounded-full hover:bg-muted text-muted-foreground"><Paperclip className="h-5 w-5" /></button>
          <button className="h-10 w-10 grid place-items-center rounded-full hover:bg-muted text-muted-foreground"><Smile className="h-5 w-5" /></button>
          <textarea
            rows={1}
            placeholder="Type a message…"
            className="flex-1 resize-none rounded-2xl border border-border bg-background px-4 py-2.5 text-sm outline-none focus:border-primary"
          />
          <button className="h-10 w-10 grid place-items-center rounded-full bg-primary text-primary-foreground hover:opacity-90 shrink-0">
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.from === "user";
  return (
    <div className={cn("flex animate-fade-in", isUser ? "justify-start" : "justify-end")}>
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-3 py-2 text-sm shadow-sm",
          isUser
            ? "bg-card border border-border rounded-bl-sm"
            : message.from === "agent"
              ? "bg-accent text-accent-foreground rounded-br-sm"
              : "bg-primary text-primary-foreground rounded-br-sm",
        )}
      >
        {message.type === "text" && <p className="whitespace-pre-wrap">{message.content}</p>}
        {message.type === "image" && message.meta?.url && (
          <div className="space-y-1">
            <img src={message.meta.url} alt={message.content} className="rounded-lg max-w-xs" />
            <p className="text-xs opacity-80">{message.content}</p>
          </div>
        )}
        {message.type === "pdf" && (
          <div className="flex items-center gap-3 bg-background/20 rounded-lg px-3 py-2 min-w-[220px]">
            <div className="h-9 w-9 grid place-items-center rounded-md bg-background/30">
              <FileText className="h-5 w-5" />
            </div>
            <div className="text-xs">
              <div className="font-semibold">{message.meta?.filename}</div>
              <div className="opacity-80">{message.meta?.size}</div>
            </div>
          </div>
        )}
        <div className={cn("text-[10px] mt-1 opacity-70", isUser ? "text-muted-foreground" : "")}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-end">
      <div className="bg-primary/90 text-primary-foreground rounded-2xl rounded-br-sm px-4 py-2.5 flex items-center gap-1">
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-current" style={{ animationDelay: "0s" }} />
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-current" style={{ animationDelay: "0.15s" }} />
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-current" style={{ animationDelay: "0.3s" }} />
      </div>
    </div>
  );
}

function CustomerPanel({ conversation }: { conversation: Conversation }) {
  const { current } = useTenant();
  return (
    <div className="p-6 space-y-6 overflow-y-auto">
      <div className="text-center">
        <Avatar className="h-16 w-16 mx-auto">
          <AvatarFallback className="bg-primary/10 text-primary font-semibold">
            {conversation.name.split(" ").map((n) => n[0]).join("")}
          </AvatarFallback>
        </Avatar>
        <div className="mt-3 font-semibold">{conversation.name}</div>
        <div className="text-xs text-muted-foreground">{conversation.phone}</div>
      </div>

      <div className="glass-card rounded-xl p-4 space-y-3 text-sm">
        <Row label="Session status">
          <Badge variant="secondary" className={statusTone[conversation.status]}>{conversation.status}</Badge>
        </Row>
        <Row label="Tenant"><span className="font-medium">{current.name}</span></Row>
        <Row label="Typing">
          <span className={conversation.isTyping ? "text-success font-medium" : "text-muted-foreground"}>
            {conversation.isTyping ? "Active" : "Idle"}
          </span>
        </Row>
        <Row label="Last activity">
          <span className="text-muted-foreground">{new Date(conversation.lastActivity).toLocaleString()}</span>
        </Row>
        <Row label="Messages"><span>{conversation.messages.length}</span></Row>
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-2">
      <span className="text-xs text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}
