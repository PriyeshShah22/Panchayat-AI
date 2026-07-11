import { Box, Button, Paper, Stack, TextField, Typography, Avatar } from "@mui/material";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import SendIcon from "@mui/icons-material/Send";
import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";

interface ChatMsg {
  role: "user" | "assistant";
  content: string;
  intent?: string | null;
  data?: any;
}

const SUGGESTIONS = [
  "Show my pending maintenance",
  "What's my complaint history?",
  "When was my last payment?",
  "Who visited today?",
  "What notices were posted this week?",
];

export default function AI() {
  const [messages, setMessages] = useState<ChatMsg[]>([
    { role: "assistant", content: "Hi! Ask me about your bills, complaints, visitors, or notices." },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send(text: string) {
    if (!text.trim()) return;
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setBusy(true);
    try {
      const res = await api.post("/ai/chat", { message: text });
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.data.reply, intent: res.data.intent, data: res.data.data },
      ]);
    } catch (e: any) {
      setMessages((m) => [...m, { role: "assistant", content: e?.response?.data?.detail || "Sorry, I couldn't process that." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "calc(100vh - 120px)" }}>
      <Typography variant="h4">AI Assistant</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Permission-aware assistant. Try one of the prompts below.
      </Typography>

      <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: "wrap" }}>
        {SUGGESTIONS.map((s) => (
          <Button key={s} size="small" variant="outlined" onClick={() => send(s)}>{s}</Button>
        ))}
      </Stack>

      <Paper ref={scrollRef} sx={{ flex: 1, p: 2, overflow: "auto", borderRadius: 3 }}>
        <Stack spacing={2}>
          {messages.map((m, i) => (
            <Stack key={i} direction="row" spacing={2} alignItems="flex-start">
              <Avatar sx={{ bgcolor: m.role === "assistant" ? "primary.main" : "secondary.main" }}>
                {m.role === "assistant" ? <SmartToyIcon /> : <PersonIcon />}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {m.role === "assistant" ? "Assistant" : "You"}
                  {m.intent && ` · intent: ${m.intent}`}
                </Typography>
                <Paper sx={{ p: 1.5, mt: 0.5, bgcolor: "background.default" }}>
                  <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>{m.content}</Typography>
                </Paper>
              </Box>
            </Stack>
          ))}
        </Stack>
      </Paper>

      <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
        <TextField
          fullWidth
          placeholder="Ask anything…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") send(input); }}
        />
        <Button endIcon={<SendIcon />} variant="contained" disabled={busy} onClick={() => send(input)}>
          Send
        </Button>
      </Stack>
    </Box>
  );
}
