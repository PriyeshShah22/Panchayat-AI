import { Alert, Box, Button, Chip, CircularProgress, Paper, Skeleton, Stack, Typography } from "@mui/material";
import { ArrowOutwardRounded, CampaignRounded, CurrencyRupeeRounded, GroupsRounded, KeyboardRounded, MicRounded, NotificationsActiveRounded, PaymentsRounded, ReportProblemRounded, ShieldRounded, VolumeUpRounded } from "@mui/icons-material";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { Bill, Complaint, Notice, Visitor } from "../types/api";
import { useLocalizedTexts } from "../components/LocalizedText";
import { useI18n } from "../store/language";
import { playLocalizedSpeech } from "../utils/speech";
import { enqueueSnackbar } from "notistack";

export default function Dashboard() {
  const go = useNavigate();
  const { language } = useI18n();
  const complaints = useQuery({ queryKey: ["complaints", "home"], queryFn: async () => (await api.get<Complaint[]>("/complaints/?limit=20")).data });
  const bills = useQuery({ queryKey: ["bills", "home"], queryFn: async () => (await api.get<Bill[]>("/bills/?limit=20")).data });
  const notices = useQuery({ queryKey: ["notices", "home"], queryFn: async () => (await api.get<Notice[]>("/notices/")).data });
  const visitors = useQuery({ queryKey: ["visitors", "home"], queryFn: async () => (await api.get<Visitor[]>("/visitors/?limit=20")).data });
  const loading = [complaints, bills, notices, visitors].some((q) => q.isLoading); const failed = [complaints, bills, notices, visitors].some((q) => q.isError);
  const open = complaints.data?.filter((c) => !["closed", "resolved"].includes(c.status)).length ?? 0;
  const due = bills.data?.filter((b) => b.status !== "paid").reduce((s, b) => s + Math.max(0, b.total_amount - b.paid_amount), 0) ?? 0;
  const inside = visitors.data?.filter((v) => v.status === "checked_in").length ?? 0;
  const latest = notices.data?.[0];
  const [latestTitle, latestBody] = useLocalizedTexts([latest?.title ?? "", latest?.body ?? ""]);
  const readNotice = () => {
    if (!latest) return;
    void playLocalizedSpeech(`${latestTitle}. ${latestBody}`, language).catch(() =>
      enqueueSnackbar("Read aloud is temporarily unavailable.", { variant: "error" }),
    );
  };
  return <Stack spacing={3}>
    <Box><Typography variant="overline" color="primary" fontWeight={900} letterSpacing={2}>COMMUNITY DESK</Typography><Typography variant="h2" sx={{ fontSize: { xs: "2.6rem", md: "4.5rem" }, maxWidth: 760 }}>Say it. We’ll help get it done.</Typography></Box>
    {failed && <Alert severity="warning">Some live records are unavailable. You can still use every manual service.</Alert>}
    {latest && <Paper role="status" sx={{ p: { xs: 2, md: 2.5 }, border: 0, bgcolor: latest.is_pinned ? "#D76049" : "#E8A84E", color: "#fff", overflow: "hidden", position: "relative" }}>
      <Box sx={{ position: "absolute", width: 180, height: 180, borderRadius: "50%", bgcolor: "rgba(255,255,255,.08)", right: -45, top: -70 }} />
      <Stack direction={{ xs: "column", md: "row" }} alignItems={{ md: "center" }} spacing={2} sx={{ position: "relative" }}>
        <Box sx={{ width: 48, height: 48, borderRadius: 2, bgcolor: "rgba(255,255,255,.16)", display: "grid", placeItems: "center", flexShrink: 0 }}><NotificationsActiveRounded /></Box>
        <Box sx={{ minWidth: 0, flex: 1 }}><Typography variant="overline" fontWeight={900} letterSpacing={1.4}>{latest.is_pinned ? "IMPORTANT NOTICE" : "NEW SOCIETY NOTICE"}</Typography><Typography variant="h5" sx={{ lineHeight: 1.2 }}>{latestTitle}</Typography><Typography sx={{ mt: .5, opacity: .9, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: { md: "nowrap" } }}>{latestBody}</Typography></Box>
        <Stack direction="row" spacing={1}><Button variant="contained" onClick={() => go("/notices")} sx={{ bgcolor: "#fff", color: "#27342F", "&:hover": { bgcolor: "#FFF7E8" } }}>View notice</Button><Button aria-label="Read important notice aloud" onClick={readNotice} sx={{ color: "#fff", border: "1px solid rgba(255,255,255,.45)" }}><VolumeUpRounded /></Button></Stack>
      </Stack>
    </Paper>}
    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1.15fr .85fr" }, gap: 3 }}>
      <Paper sx={{ minHeight: { xs: 440, md: 540 }, p: { xs: 3, md: 5 }, position: "relative", overflow: "hidden", bgcolor: "#173F35", color: "#FFFDF6", border: 0, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <Box sx={{ position: "absolute", inset: "auto -15% -38% auto", width: "70%", aspectRatio: "1", borderRadius: "50%", border: "1px solid rgba(255,255,255,.15)" }} /><Box sx={{ position: "absolute", inset: "auto -5% -30% auto", width: "55%", aspectRatio: "1", borderRadius: "50%", border: "1px solid rgba(255,255,255,.12)" }} />
        <Box><Chip label="Private • Permission checked" sx={{ bgcolor: "rgba(255,255,255,.12)", color: "white" }} /><Typography variant="h3" sx={{ mt: 3, maxWidth: 620, fontSize: { xs: "2rem", md: "3rem" } }}>What would you like the Panchayat to do?</Typography><Typography sx={{ mt: 1.5, opacity: .75, maxWidth: 560 }}>No forms. No department names. Explain the problem in Hindi, Marathi, Gujarati, or English.</Typography></Box>
        <Stack alignItems="center" sx={{ my: 3, position: "relative" }}><Box sx={{ position: "absolute", width: 190, height: 190, border: "1px solid rgba(244,184,96,.28)", borderRadius: "50%" }} /><Box sx={{ position: "absolute", width: 150, height: 150, border: "1px solid rgba(244,184,96,.4)", borderRadius: "50%" }} /><Button aria-label="Start talking to Panchayat" onClick={() => go("/ai")} sx={{ width: 112, height: 112, minWidth: 112, borderRadius: "50%", bgcolor: "secondary.main", color: "secondary.contrastText", zIndex: 1, flexDirection: "column", gap: .5, boxShadow: "0 15px 45px rgba(244,184,96,.25)", "&:hover": { bgcolor: "#ffc873", transform: "scale(1.04)" } }}><MicRounded fontSize="large" /><span>Speak</span></Button></Stack>
        <Button variant="outlined" startIcon={<KeyboardRounded />} onClick={() => go("/ai")} sx={{ alignSelf: "center", color: "white", borderColor: "rgba(255,255,255,.35)", px: 3 }}>I prefer typing</Button>
      </Paper>
      <Stack spacing={3}>
        <Box sx={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 2 }}>
          <ServiceTile icon={<ReportProblemRounded />} eyebrow="HELP" value={loading ? undefined : String(open)} label="Active complaints" color="#D76049" onClick={() => go("/complaints")} />
          <ServiceTile icon={<PaymentsRounded />} eyebrow="MONEY" value={loading ? undefined : `₹${due.toLocaleString("en-IN")}`} label="Maintenance due" color="#E8A84E" onClick={() => go("/bills")} />
          <ServiceTile icon={<ShieldRounded />} eyebrow="GATE" value={loading ? undefined : String(inside)} label="Visitors inside" color="#4C8D78" onClick={() => go("/visitors")} />
          <ServiceTile icon={<GroupsRounded />} eyebrow="PEOPLE" value={loading ? undefined : "Help"} label="Talk to a person" color="#6D729C" onClick={() => go("/ai")} />
        </Box>
        <Paper sx={{ p: 3, flex: 1, bgcolor: "#F0E9D7", color: "#27342F" }}><Stack direction="row" justifyContent="space-between"><Box><Typography variant="overline" fontWeight={900}>STAY INFORMED</Typography><Typography variant="h5" sx={{ mt: .5 }}>All official updates in one place</Typography></Box><CampaignRounded sx={{ fontSize: 38, color: "#D76049" }} /></Stack><Typography sx={{ mt: 2, color: "#5E6763" }}>{loading ? <Skeleton /> : `${notices.data?.length ?? 0} active notices are available. Important updates are always shown above so they are hard to miss.`}</Typography><Button variant="contained" onClick={() => go("/notices")} sx={{ mt: 3, bgcolor: "#176B52", color: "#FFFDF6", "&:hover": { bgcolor: "#124C3B" } }}>See all notices</Button></Paper>
      </Stack>
    </Box>
    <Box><Stack direction="row" justifyContent="space-between" alignItems="end" sx={{ mb: 2 }}><Box><Typography variant="overline" fontWeight={900}>MANUAL SERVICES</Typography><Typography variant="h4">Prefer doing it yourself?</Typography></Box><Typography color="text.secondary" sx={{ display: { xs: "none", md: "block" } }}>Every AI action has a manual fallback.</Typography></Stack><Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "repeat(2,1fr)", xl: "repeat(4,1fr)" }, gap: 2 }}><Manual icon={<ReportProblemRounded />} title="Report a problem" copy="Water, road, light, waste, or safety" onClick={() => go("/complaints")} /><Manual icon={<CurrencyRupeeRounded />} title="Check bills" copy="See dues, dates, and receipts" onClick={() => go("/bills")} /><Manual icon={<ShieldRounded />} title="Allow a visitor" copy="Create or cancel gate access" onClick={() => go("/visitors")} /><Manual icon={<CampaignRounded />} title="Read notices" copy="Official source and simple explanation" onClick={() => go("/notices")} /></Box></Box>
  </Stack>;
}

function ServiceTile({ icon, eyebrow, value, label, color, onClick }: { icon: React.ReactNode; eyebrow: string; value?: string; label: string; color: string; onClick(): void }) { return <Paper component="button" onClick={onClick} sx={{ p: { xs: 2, md: 2.5 }, minHeight: 170, textAlign: "left", font: "inherit", cursor: "pointer", bgcolor: color, color: "white", border: 0, display: "flex", flexDirection: "column", alignItems: "stretch", "&:hover": { transform: "translateY(-4px)", filter: "brightness(1.04)" }, transition: ".18s ease" }}><Stack direction="row" justifyContent="space-between"><Typography variant="caption" fontWeight={900} letterSpacing={1.5}>{eyebrow}</Typography>{icon}</Stack><Box sx={{ mt: "auto" }}>{value === undefined ? <CircularProgress size={25} color="inherit" /> : <Typography variant="h4">{value}</Typography>}<Typography sx={{ opacity: .9 }}>{label}</Typography></Box></Paper>; }
function Manual({ icon, title, copy, onClick }: { icon: React.ReactNode; title: string; copy: string; onClick(): void }) { return <Paper component="button" onClick={onClick} sx={{ p: 2.5, textAlign: "left", font: "inherit", cursor: "pointer", bgcolor: "background.paper", display: "grid", gridTemplateColumns: "52px 1fr auto", gap: 1.5, alignItems: "center", "&:hover": { borderColor: "primary.main" } }}><Box sx={{ width: 52, height: 52, borderRadius: 1.5, bgcolor: "#E8E2D1", color: "#173F35", display: "grid", placeItems: "center" }}>{icon}</Box><Box><Typography fontWeight={850}>{title}</Typography><Typography variant="body2" color="text.secondary">{copy}</Typography></Box><ArrowOutwardRounded /></Paper>; }
