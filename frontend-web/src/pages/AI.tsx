import { useEffect, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Paper,
  Stack,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  AutoAwesomeRounded,
  CancelOutlined,
  CheckCircleRounded,
  HearingRounded,
  MicRounded,
  PaymentsRounded,
  SendRounded,
  StopCircleRounded,
  VolumeUpRounded,
} from "@mui/icons-material";
import { enqueueSnackbar } from "notistack";
import { api } from "../api/client";
import { useI18n } from "../store/language";
import { playLocalizedSpeech, stopLocalizedSpeech } from "../utils/speech";

interface Proposal {
  id: number;
  action_type: string;
  risk: string;
  status: string;
  summary: string;
  fields: Record<string, unknown>;
  expires_at: string;
}
interface Message {
  role: "user" | "assistant";
  content: string;
  action?: Proposal;
  language?: string;
}
interface MemoryMessage {
  role: "user" | "assistant";
  content: string;
}

const plainSpeech = (text: string) =>
  text
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1")
    .replace(/^\s{0,3}#{1,6}\s*/gm, "")
    .replace(/\*\*|__|`/g, "")
    .replace(/^\s*[-*•]\s+/gm, "")
    .replace(/[\*_]/g, " ")
    .replace(/[ \t]+/g, " ")
    .trim();
function recordingFormat() {
  return [
    { mimeType: "audio/webm;codecs=opus", extension: "webm" },
    { mimeType: "audio/webm", extension: "webm" },
    { mimeType: "audio/mp4", extension: "m4a" },
    { mimeType: "audio/ogg;codecs=opus", extension: "ogg" },
  ].find(({ mimeType }) => MediaRecorder.isTypeSupported(mimeType));
}

export default function AI() {
  const { t } = useI18n();
  const theme = useTheme();
  const mobile = useMediaQuery(theme.breakpoints.down("md"));
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Namaste. What can I do for you today?",
      language: "en-IN",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [memoryMessages, setMemoryMessages] = useState<MemoryMessage[]>([]);
  const [conversationSummary, setConversationSummary] = useState("");
  const [speakingText, setSpeakingText] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationRef = useRef<number | null>(null);
  const holdRequestedRef = useRef(false);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);
  useEffect(
    () => () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      if (timerRef.current) clearInterval(timerRef.current);
      stopLocalizedSpeech();
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      void audioContextRef.current?.close();
    },
    [],
  );

  function stopSpeaking() {
    stopLocalizedSpeech();
    setSpeakingText(null);
  }
  async function speak(text: string, language = "en-IN") {
    stopSpeaking();
    const cleanText = plainSpeech(text);
    setVoiceError(null);
    setSpeakingText(text);
    const speechLanguage = language.toLowerCase().startsWith("mr")
      ? "mr"
      : language.toLowerCase().startsWith("hi")
        ? "hi"
        : "en";
    try {
      await playLocalizedSpeech(cleanText, speechLanguage, {
        onEnd: () => setSpeakingText(null),
        onError: (message) => {
          setSpeakingText(null);
          setVoiceError(message);
        },
      });
    } catch (error) {
      setSpeakingText(null);
      setVoiceError(
        error instanceof Error
          ? error.message
          : "Read aloud is unavailable in this browser.",
      );
    }
  }
  function appendResult(
    data: {
      reply?: string;
      detected_language?: string;
      memory_messages?: MemoryMessage[];
      conversation_summary?: string;
      action?: Proposal;
    },
    translated?: string,
  ) {
    const reply = plainSpeech(data.reply || "");
    const responseLanguage = data.detected_language || "en-IN";
    setMemoryMessages(data.memory_messages || []);
    setConversationSummary(data.conversation_summary || "");
    setMessages((current) => [
      ...current,
      ...(translated ? [{ role: "user" as const, content: translated }] : []),
      {
        role: "assistant",
        content: reply,
        action: data.action,
        language: responseLanguage,
      },
    ]);
    void speak(reply, responseLanguage);
  }
  async function send(text = input) {
    if (!text.trim() || busy) return;
    stopSpeaking();
    setMessages((current) => [
      ...current,
      { role: "user", content: text.trim() },
    ]);
    setInput("");
    setBusy(true);
    try {
      appendResult(
        (
          await api.post("/ai/chat", {
            message: text.trim(),
            language: "auto",
            history: memoryMessages,
            conversation_summary: conversationSummary || null,
          })
        ).data,
      );
    } catch (error: any) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            error?.response?.data?.detail ||
            "The assistant could not be reached.",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }
  async function sendVoice(blob: Blob, extension: string) {
    setBusy(true);
    try {
      const form = new FormData();
      form.append("audio", blob, `request.${extension}`);
      form.append("language", "unknown");
      form.append("history", JSON.stringify(memoryMessages));
      form.append("conversation_summary", conversationSummary);
      const data = (await api.post("/ai/voice", form, { timeout: 45_000 }))
        .data;
      appendResult(data, data.input_transcript);
    } catch (error: any) {
      setVoiceError(
        error?.response?.data?.detail ||
          "The recording could not be understood. Try again or type instead.",
      );
    } finally {
      setBusy(false);
    }
  }
  function startWaveform(stream: MediaStream) {
    const context = new AudioContext();
    const analyser = context.createAnalyser();
    analyser.fftSize = 1024;
    analyser.smoothingTimeConstant = 0.82;
    context.createMediaStreamSource(stream).connect(analyser);
    audioContextRef.current = context;
    const values = new Uint8Array(analyser.fftSize);
    const draw = () => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext("2d");
      if (canvas && ctx) {
        const width = canvas.clientWidth * devicePixelRatio;
        const height = canvas.clientHeight * devicePixelRatio;
        if (canvas.width !== width || canvas.height !== height) {
          canvas.width = width;
          canvas.height = height;
        }
        analyser.getByteTimeDomainData(values);
        ctx.clearRect(0, 0, width, height);
        const gradient = ctx.createLinearGradient(0, 0, width, 0);
        gradient.addColorStop(0, "#7EE2B8");
        gradient.addColorStop(0.5, "#F4B860");
        gradient.addColorStop(1, "#7EE2B8");
        ctx.strokeStyle = gradient;
        ctx.lineWidth = Math.max(2, 2.5 * devicePixelRatio);
        ctx.lineCap = "round";
        ctx.beginPath();
        values.forEach((value, index) => {
          const x = (index / (values.length - 1)) * width;
          const y = height / 2 + ((value - 128) / 128) * height * 0.42;
          if (index === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.stroke();
      }
      animationRef.current = requestAnimationFrame(draw);
    };
    draw();
  }
  function stopWaveform() {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    animationRef.current = null;
    void audioContextRef.current?.close();
    audioContextRef.current = null;
  }
  async function startRecording() {
    stopSpeaking();
    setVoiceError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { autoGainControl: true, channelCount: 1 },
      });
      if (mobile && !holdRequestedRef.current) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      streamRef.current = stream;
      chunksRef.current = [];
      setRecording(true);
      startWaveform(stream);
      const format = recordingFormat();
      const recorder = new MediaRecorder(
        stream,
        format ? { mimeType: format.mimeType } : undefined,
      );
      recorderRef.current = recorder;
      recorder.ondataavailable = (event) =>
        event.data.size && chunksRef.current.push(event.data);
      recorder.onstop = () => {
        const mime = recorder.mimeType || format?.mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: mime });
        stream.getTracks().forEach((track) => track.stop());
        if (blob.size < 1000)
          return setVoiceError("Almost no microphone audio was captured.");
        void sendVoice(blob, format?.extension || "webm");
      };
      recorder.start();
      setSeconds(0);
      timerRef.current = window.setInterval(
        () => setSeconds((value) => value + 1),
        1000,
      );
    } catch {
      setVoiceError("Allow microphone access, or type your request below.");
    }
  }
  function stopRecording() {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
    stopWaveform();
    if (recorderRef.current?.state !== "inactive") recorderRef.current?.stop();
    setRecording(false);
  }
  function beginHold(event: React.PointerEvent<HTMLButtonElement>) {
    if (!mobile || busy || recording) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    holdRequestedRef.current = true;
    void startRecording();
  }
  function endHold() {
    if (!mobile) return;
    holdRequestedRef.current = false;
    if (recording || recorderRef.current?.state === "recording") stopRecording();
  }
  async function decide(
    action: Proposal,
    decision: "confirm" | "cancel",
    language = "en-IN",
  ) {
    stopSpeaking();
    setBusy(true);
    try {
      const data = (
        await api.post(`/ai/actions/${action.id}/${decision}`, undefined, {
          params: { language },
        })
      ).data;
      setMessages((current) => [
        ...current,
        { role: "assistant", content: data.message, language },
      ]);
      void speak(data.message, language);
    } catch (error: any) {
      enqueueSnackbar(
        error?.response?.data?.detail || "That action could not be completed",
        { variant: "error" },
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <Stack spacing={{ xs: 0, md: 2.5 }} sx={{ maxWidth: 980, mx: { xs: -2, sm: -3, md: "auto" }, mt: { xs: -2, sm: -3, md: 0 }, mb: { xs: -2, sm: -3, md: 0 }, minHeight: { xs: "calc(100dvh - 64px)", md: "auto" } }}>
      <Box textAlign="center" sx={{ display: { xs: "none", md: "block" } }}>
        <Chip
          icon={<AutoAwesomeRounded />}
          label="Sarvam + OpenAI agent"
          color="success"
          size="small"
        />
        <Typography
          variant="h2"
          sx={{ mt: 1.5, fontSize: { xs: "2.4rem", md: "4rem" } }}
        >
          {t("Ask Panchayat")}
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 1 }}>
          {t(
            "Speak or type. Panchayat can check records and complete approved tasks for you.",
          )}
        </Typography>
      </Box>
      <Paper
        sx={{
          minHeight: { xs: "calc(100dvh - 64px)", md: 700 },
          height: { xs: "calc(100dvh - 64px)", md: "auto" },
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          boxShadow: "0 22px 70px rgba(23,63,53,.12)",
          borderRadius: { xs: 0, md: 3 },
          border: { xs: 0, md: undefined },
        }}
      >
        <Stack
          direction="row"
          alignItems="center"
          spacing={1.5}
          sx={{ p: { xs: 1.5, md: 2 }, minHeight: { xs: 64, md: "auto" }, bgcolor: "#173F35", color: "white" }}
        >
          <Box
            sx={{
              width: { xs: 40, md: 46 },
              height: { xs: 40, md: 46 },
              borderRadius: 2,
              bgcolor: "rgba(255,255,255,.12)",
              display: "grid",
              placeItems: "center",
            }}
          >
            <HearingRounded />
          </Box>
          <Box>
            <Typography fontWeight={900}>Panchayat Agent</Typography>
            <Typography variant="caption" sx={{ opacity: 0.7 }}>
              Can read records and complete confirmed tasks
            </Typography>
          </Box>
          <Box
            sx={{
              ml: "auto",
              width: 9,
              height: 9,
              bgcolor: "#7EE2B8",
              borderRadius: "50%",
            }}
          />
        </Stack>
        <Stack
          spacing={2}
          sx={{
            p: { xs: 2, md: 3 },
            flex: 1,
            overflowY: "auto",
            minHeight: 0,
            maxHeight: { xs: "none", md: 540 },
          }}
          aria-live="polite"
        >
          {messages.map((message, index) => (
            <Box
              key={`${message.role}-${index}`}
              sx={{
                alignSelf: message.role === "user" ? "flex-end" : "flex-start",
                maxWidth: { xs: "92%", md: "78%" },
              }}
            >
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  border: 0,
                  bgcolor:
                    message.role === "user" ? "primary.main" : "action.hover",
                  color:
                    message.role === "user"
                      ? "primary.contrastText"
                      : "text.primary",
                  borderRadius:
                    message.role === "user"
                      ? "16px 16px 4px 16px"
                      : "16px 16px 16px 4px",
                }}
              >
                <Typography sx={{ whiteSpace: "pre-wrap" }}>
                  {message.content}
                </Typography>
                {message.role === "assistant" && (
                  <IconButton
                    size="small"
                    onClick={() =>
                      speakingText === message.content
                        ? stopSpeaking()
                        : void speak(message.content, message.language)
                    }
                    aria-label="Read response aloud"
                    sx={{ mt: 0.5 }}
                  >
                    {speakingText === message.content ? (
                      <StopCircleRounded />
                    ) : (
                      <VolumeUpRounded />
                    )}
                  </IconButton>
                )}
              </Paper>
              {message.action && (
                <ActionCard
                  action={message.action}
                  busy={busy}
                  decide={decide}
                  language={message.language || "en-IN"}
                  onPaid={async () =>
                    setMessages((current) => [
                      ...current,
                      {
                        role: "assistant",
                        content:
                          "Payment complete. Your maintenance account is now clear.",
                      },
                    ])
                  }
                />
              )}
            </Box>
          ))}
          {busy && (
            <Stack direction="row" spacing={1} alignItems="center">
              <CircularProgress size={20} />
              <Typography color="text.secondary">
                Working on your request…
              </Typography>
            </Stack>
          )}
          <div ref={endRef} />
        </Stack>
        <Box
          sx={{
            p: { xs: 1.25, sm: 2 },
            borderTop: 1,
            borderColor: "divider",
            bgcolor: "background.default",
          }}
        >
          {voiceError && (
            <Alert
              severity="warning"
              onClose={() => setVoiceError(null)}
              sx={{ mb: 1.5 }}
            >
              {voiceError}
            </Alert>
          )}
          <Stack direction="row" spacing={1} alignItems="center">
            <IconButton
              onClick={mobile ? undefined : recording ? stopRecording : startRecording}
              onPointerDown={beginHold}
              onPointerUp={endHold}
              onPointerCancel={endHold}
              onLostPointerCapture={endHold}
              disabled={busy}
              aria-label={mobile ? "Hold to record a voice request" : recording ? "Stop recording" : "Start voice request"}
              sx={{
                width: 54,
                height: 54,
                flexShrink: 0,
                touchAction: "none",
                userSelect: "none",
                bgcolor: recording ? "error.main" : "primary.main",
                color: "white",
                "&:hover": {
                  bgcolor: recording ? "error.dark" : "primary.dark",
                },
              }}
            >
              {recording ? <StopCircleRounded /> : <MicRounded />}
            </IconButton>
            {recording ? (
              <Paper
                elevation={0}
                sx={{
                  flex: 1,
                  height: { xs: 64, sm: 68 },
                  minWidth: 0,
                  px: { xs: 1.25, sm: 2 },
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr auto", sm: "auto 1fr auto" },
                  gap: { xs: .75, sm: 1.5 },
                  alignItems: "center",
                  overflow: "hidden",
                  color: "white",
                  background: "linear-gradient(135deg,#173F35,#225E4E)",
                  border: "1px solid rgba(126,226,184,.28)",
                }}
              >
                <Box
                  sx={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    bgcolor: "#7EE2B8",
                    boxShadow: "0 0 0 7px rgba(126,226,184,.12)",
                    display: { xs: "none", sm: "block" },
                  }}
                />
                <Box sx={{ minWidth: 0 }}>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="caption" fontWeight={900}>
                      {t("Listening")}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.72 }}>
                      {t("Tap when finished")}
                    </Typography>
                  </Stack>
                  <Box sx={{ width: "100%", height: 36, minHeight: 36, overflow: "visible", display: "flex", alignItems: "center" }}><canvas ref={canvasRef} style={{ display: "block", width: "100%", height: 36, flex: 1 }} /></Box>
                </Box>
                <Chip
                  label={`${seconds}s`}
                  size="small"
                  sx={{
                    bgcolor: "rgba(255,255,255,.12)",
                    color: "white",
                    fontWeight: 900,
                  }}
                />
              </Paper>
            ) : (
              <TextField
                fullWidth
                multiline
                maxRows={3}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void send();
                  }
                }}
                placeholder={t("Tell Panchayat what you need…")}
                inputProps={{ "aria-label": "Message to Panchayat Assistant" }}
              />
            )}
            <IconButton
              aria-label="Send message"
              color="primary"
              disabled={!input.trim() || busy || recording}
              onClick={() => void send()}
            >
              <SendRounded />
            </IconButton>
          </Stack>
          {recording && (
            <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: .75 }}>
              {mobile ? "Keep holding while you speak. Release to send." : "Moving bars mean your voice is being heard. Tap stop when finished."}
            </Typography>
          )}
          {!recording && mobile && <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: .75, ml: .5 }}>{t("Hold the microphone to talk")}</Typography>}
        </Box>
      </Paper>
    </Stack>
  );
}

function ActionCard({
  action,
  busy,
  decide,
  language,
  onPaid,
}: {
  action: Proposal;
  busy: boolean;
  decide: (
    action: Proposal,
    decision: "confirm" | "cancel",
    language?: string,
  ) => Promise<void>;
  language: string;
  onPaid: () => Promise<void>;
}) {
  const payment = action.action_type === "pay_outstanding_dues";
  const [paying, setPaying] = useState(false);
  async function payNow() {
    setPaying(true);
    try {
      await api.post(`/ai/actions/${action.id}/confirm`);
      if (action.fields.demo) {
        const result = (await api.post("/bills/payments/demo")).data;
        enqueueSnackbar(
          `Demo payment of ₹${result.amount.toLocaleString("en-IN")} completed`,
          { variant: "success" },
        );
        await onPaid();
      } else {
        const order = (await api.post("/bills/payment-order")).data;
        await loadRazorpay();
        await new Promise((resolve, reject) => {
          const checkout = new (window as any).Razorpay({
            key: order.key_id,
            amount: order.amount_paise,
            currency: "INR",
            name: "Panchayat",
            description: "Combined maintenance dues",
            order_id: order.order_id,
            handler: async (response: any) =>
              resolve(
                (await api.post("/bills/payments/verify", response)).data,
              ),
            modal: { ondismiss: () => reject(new Error("Payment cancelled")) },
          });
          checkout.open();
        });
      }
    } catch (error: any) {
      enqueueSnackbar(
        error?.response?.data?.detail || error?.message || "Payment failed",
        { variant: "error" },
      );
    } finally {
      setPaying(false);
    }
  }
  return (
    <Paper
      sx={{
        mt: 1.5,
        p: 2.5,
        borderLeft: 5,
        borderColor: payment
          ? "success.main"
          : action.risk === "high"
            ? "error.main"
            : "secondary.main",
      }}
    >
      <Stack direction="row" justifyContent="space-between">
        <Typography variant="overline" fontWeight={900}>
          {payment ? "COMBINED CHECKOUT" : "ACTION TO REVIEW"}
        </Typography>
        <Chip
          size="small"
          label={
            payment && action.fields.demo ? "Demo mode" : `${action.risk} risk`
          }
          color={payment ? "success" : "warning"}
        />
      </Stack>
      <Typography variant="h6">{action.summary}</Typography>
      <Divider sx={{ my: 1.5 }} />
      {Object.entries(action.fields)
        .filter(([key]) => !["bill_ids", "society_id"].includes(key))
        .map(([key, value]) => (
          <Stack
            key={key}
            direction="row"
            justifyContent="space-between"
            spacing={2}
            sx={{ py: 0.5 }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ textTransform: "capitalize" }}
            >
              {key.replaceAll("_", " ")}
            </Typography>
            <Typography variant="body2" fontWeight={850}>
              {Array.isArray(value)
                ? value.join(", ")
                : typeof value === "boolean"
                  ? value
                    ? "Yes"
                    : "No"
                  : String(value)}
            </Typography>
          </Stack>
        ))}
      {payment && Boolean(action.fields.demo) && (
        <Alert severity="warning" sx={{ mt: 1.5 }}>
          Simulation only. No real money or bank account is used.
        </Alert>
      )}
      <Stack direction={{ xs: "column", sm: "row" }} spacing={1} sx={{ mt: 2 }}>
        {payment ? (
          <Button
            variant="contained"
            color="success"
            startIcon={<PaymentsRounded />}
            disabled={paying || busy}
            onClick={payNow}
          >
            Pay ₹{Number(action.fields.amount).toLocaleString("en-IN")} now
          </Button>
        ) : (
          <Button
            variant="contained"
            startIcon={<CheckCircleRounded />}
            disabled={busy}
            onClick={() => void decide(action, "confirm", language)}
          >
            Confirm action
          </Button>
        )}
        <Button
          variant="outlined"
          color="inherit"
          startIcon={<CancelOutlined />}
          disabled={busy || paying}
          onClick={() => void decide(action, "cancel", language)}
        >
          Cancel
        </Button>
      </Stack>
    </Paper>
  );
}

async function loadRazorpay() {
  if ((window as any).Razorpay) return;
  await new Promise<void>((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve();
    script.onerror = () =>
      reject(new Error("Razorpay checkout could not load"));
    document.body.appendChild(script);
  });
}
