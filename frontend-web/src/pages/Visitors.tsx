import { useMemo, useState } from "react";
import { Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Divider, IconButton, InputAdornment, MenuItem, Paper, Stack, Tab, Tabs, TextField, Typography } from "@mui/material";
import { ApartmentRounded, CalendarMonthRounded, CheckRounded, CloseRounded, DirectionsCarRounded, DoorFrontRounded, HowToRegRounded, LoginRounded, LogoutRounded, PersonAddAltRounded, PersonRounded, PhoneRounded, SearchRounded, ShieldRounded, TodayRounded } from "@mui/icons-material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { enqueueSnackbar } from "notistack";
import { api } from "../api/client";
import { LoadingPanel } from "../components/StateViews";
import { useAuthStore } from "../store/auth";
import type { Flat, Visitor } from "../types/api";
import { formatSocietyDateTime, societyInputToUtc, toSocietyDateTimeInput } from "../utils/dateTime";

type ResidentProfile = { flat_id: number };
type FormState = { wing: string; flat_id: string; name: string; phone: string; purpose: string; vehicle_number: string; expected_at: string };
const emptyForm = (): FormState => ({ wing: "", flat_id: "", name: "", phone: "", purpose: "", vehicle_number: "", expected_at: toSocietyDateTimeInput() });
const statusTone: Record<string, "default" | "warning" | "success" | "error" | "info"> = { pending: "warning", approved: "info", rejected: "error", checked_in: "success", checked_out: "default" };
const purposes = ["Guest visit", "Delivery", "Maintenance", "Domestic help"];

export default function Visitors() {
  const queryClient = useQueryClient();
  const me = useAuthStore((state) => state.user);
  const roles = new Set(me?.roles.map((role) => role.name) ?? []);
  const canApprove = Boolean(me?.is_superuser || roles.has("admin") || roles.has("committee"));
  const canOperateGate = Boolean(canApprove || roles.has("security"));
  const canChooseHousehold = canOperateGate;
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tab, setTab] = useState("active");
  const [search, setSearch] = useState("");
  const [form, setForm] = useState<FormState>(emptyForm);
  const profile = useQuery({ queryKey: ["resident-profile"], queryFn: async () => (await api.get<ResidentProfile>("/residents/me")).data, retry: false, enabled: roles.has("resident") });
  const flats = useQuery({ queryKey: ["society-flats"], queryFn: async () => (await api.get<Flat[]>("/societies/flats")).data });
  const list = useQuery({ queryKey: ["visitors"], queryFn: async () => (await api.get<Visitor[]>("/visitors/?limit=200")).data });
  const selectedFlat = (flats.data ?? []).find((flat) => flat.id === (canChooseHousehold ? Number(form.flat_id) : profile.data?.flat_id));
  const availableFlats = (flats.data ?? []).filter((flat) => flat.block_name === form.wing);
  const reset = () => setForm(emptyForm());
  const create = useMutation({
    mutationFn: async () => api.post("/visitors/", {
      society_id: me?.society_id,
      flat_id: canChooseHousehold ? Number(form.flat_id) : profile.data?.flat_id,
      name: form.name.trim(), phone: form.phone.trim() || null, purpose: form.purpose.trim() || null,
      vehicle_number: form.vehicle_number.trim().toUpperCase() || null,
      expected_at: societyInputToUtc(form.expected_at),
    }),
    onSuccess: async () => { enqueueSnackbar("Gate pass sent for approval", { variant: "success" }); setDialogOpen(false); reset(); await Promise.all([queryClient.invalidateQueries({ queryKey: ["visitors"] }), queryClient.invalidateQueries({ queryKey: ["notifications"] })]); },
    onError: (error: any) => enqueueSnackbar(error?.response?.data?.detail || "Gate pass could not be created", { variant: "error" }),
  });
  const action = useMutation({
    mutationFn: async ({ id, kind }: { id: number; kind: string }) => api.post(`/visitors/${id}/action`, { action: kind }),
    onSuccess: async (_data, variables) => { enqueueSnackbar(actionLabel(variables.kind), { variant: "success" }); await Promise.all([queryClient.invalidateQueries({ queryKey: ["visitors"] }), queryClient.invalidateQueries({ queryKey: ["notifications"] })]); },
    onError: (error: any) => enqueueSnackbar(error?.response?.data?.detail || "Gate status could not be changed", { variant: "error" }),
  });
  const visitors = useMemo(() => (list.data ?? []).filter((visitor) => {
    const active = ["pending", "approved", "checked_in"].includes(visitor.status);
    const tabMatch = tab === "all" || (tab === "active" ? active : !active);
    const term = `${visitor.name} ${visitor.phone || ""} ${visitor.purpose || ""} ${visitor.vehicle_number || ""} ${visitor.wing_name || ""} ${visitor.flat_number || ""}`.toLowerCase();
    return tabMatch && term.includes(search.toLowerCase());
  }), [list.data, search, tab]);
  if (list.isLoading) return <LoadingPanel />;
  const all = list.data ?? [];
  const formReady = form.name.trim().length >= 2 && Boolean(form.expected_at) && (canChooseHousehold ? Boolean(form.flat_id) : Boolean(profile.data?.flat_id));

  return <Stack spacing={3}>
    <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ md: "end" }} spacing={2}>
      <Box><Typography variant="overline" color="primary" fontWeight={900} letterSpacing={1.6}>GATE DESK</Typography><Typography variant="h2" sx={{ fontSize: { xs: "2.35rem", md: "3.6rem" } }}>Visitor access, made clear</Typography><Typography color="text.secondary" sx={{ mt: 1, maxWidth: 700 }}>{canApprove ? "Review resident requests before security admits a visitor." : canOperateGate ? "See approved visitors and record entry or exit at the correct time." : "Request a pass in advance and follow its approval status here."}</Typography></Box>
      <Button variant="contained" size="large" startIcon={<PersonAddAltRounded />} onClick={() => { reset(); setDialogOpen(true); }}>Request visitor pass</Button>
    </Stack>
    <Box sx={{ display: "grid", gridTemplateColumns: { xs: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }, gap: 1.5 }}><GateMetric icon={<DoorFrontRounded />} label="Inside now" value={all.filter((v) => v.status === "checked_in").length} color="#2B805F" /><GateMetric icon={<TodayRounded />} label="Approved & expected" value={all.filter((v) => v.status === "approved").length} color="#3A6EA5" /><GateMetric icon={<HowToRegRounded />} label="Awaiting approval" value={all.filter((v) => v.status === "pending").length} color="#C67A20" /><GateMetric icon={<ShieldRounded />} label="Completed" value={all.filter((v) => v.status === "checked_out").length} color="#6D729C" /></Box>
    <Paper sx={{ overflow: "hidden" }}>
      <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ md: "center" }} spacing={1} sx={{ px: 2, pt: 1 }}><Tabs value={tab} onChange={(_event, value) => setTab(value)} aria-label="Visitor record filter" variant="scrollable"><Tab value="active" label="Active & expected" /><Tab value="history" label="History" /><Tab value="all" label="All" /></Tabs><TextField size="small" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search visitor, wing, flat or vehicle" InputProps={{ startAdornment: <InputAdornment position="start"><SearchRounded /></InputAdornment> }} sx={{ maxWidth: { md: 340 }, pb: { xs: 2, md: 1 } }} /></Stack><Divider />
      <Stack divider={<Divider />}>{visitors.map((visitor) => <VisitorRow key={visitor.id} visitor={visitor} canApprove={canApprove} canOperateGate={canOperateGate} busy={action.isPending} onAction={(kind) => action.mutate({ id: visitor.id, kind })} />)}{visitors.length === 0 && <Box sx={{ py: 8, textAlign: "center" }}><DoorFrontRounded sx={{ fontSize: 48, color: "text.disabled" }} /><Typography variant="h6" sx={{ mt: 1 }}>No visitor records here</Typography><Typography color="text.secondary">Try another filter or request a new visitor pass.</Typography></Box>}</Stack>
    </Paper>

    <Dialog open={dialogOpen} onClose={() => !create.isPending && setDialogOpen(false)} fullWidth maxWidth="md">
      <Box component="form" onSubmit={(event) => { event.preventDefault(); if (formReady) create.mutate(); }}>
        <DialogTitle><Typography variant="h4">Request a visitor pass</Typography><Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>A short request helps the committee approve quickly and security identify the right person.</Typography></DialogTitle>
        <DialogContent>
          <Stack spacing={3}>
            <FormSection number="1" icon={<PersonRounded />} title="Who is visiting?" subtitle="Use the visitor’s name as security will recognise it.">
              <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1.25fr 1fr" }, gap: 2 }}><TextField required autoFocus label="Visitor name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="For example, Ajay Patil" helperText="At least 2 characters" /><TextField label="Mobile number" type="tel" inputProps={{ inputMode: "tel", maxLength: 20 }} value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} placeholder="Optional" helperText="Helps security contact the visitor" InputProps={{ startAdornment: <InputAdornment position="start"><PhoneRounded /></InputAdornment> }} /></Box>
            </FormSection>
            <Divider />
            <FormSection number="2" icon={<ApartmentRounded />} title="Where are they going?" subtitle="Choose the exact wing and flat so the pass reaches the right gate desk.">
              {canChooseHousehold ? <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" }, gap: 2 }}><TextField select required label="Wing / building" value={form.wing} onChange={(event) => setForm({ ...form, wing: event.target.value, flat_id: "" })} helperText="Buildings A to D">{["A", "B", "C", "D"].map((wing) => <MenuItem key={wing} value={wing}>Wing {wing}</MenuItem>)}</TextField><TextField select required disabled={!form.wing} label="Flat number" value={form.flat_id} onChange={(event) => setForm({ ...form, flat_id: event.target.value })} helperText={form.wing ? "4 floors · 4 flats per floor" : "Choose a wing first"}>{availableFlats.map((flat) => <MenuItem key={flat.id} value={String(flat.id)}>Flat {flat.number} · Floor {flat.floor}</MenuItem>)}</TextField></Box> : <Paper variant="outlined" sx={{ p: 2, bgcolor: "action.hover" }}><Stack direction="row" alignItems="center" spacing={1.5}><ApartmentRounded color="primary" /><Box><Typography fontWeight={850}>{selectedFlat ? `Wing ${selectedFlat.block_name} · Flat ${selectedFlat.number}` : "Loading your registered home…"}</Typography><Typography variant="body2" color="text.secondary">The pass is securely linked to your approved resident profile.</Typography></Box></Stack></Paper>}
            </FormSection>
            <Divider />
            <FormSection number="3" icon={<CalendarMonthRounded />} title="When and why?" subtitle="Times are saved and shown in Indian Standard Time (IST).">
              <Stack spacing={2}><Box><Typography variant="caption" color="text.secondary" fontWeight={800}>QUICK PURPOSE</Typography><Stack direction="row" gap={1} flexWrap="wrap" sx={{ mt: .75 }}>{purposes.map((purpose) => <Chip key={purpose} clickable color={form.purpose === purpose ? "primary" : "default"} variant={form.purpose === purpose ? "filled" : "outlined"} label={purpose} onClick={() => setForm({ ...form, purpose })} />)}</Stack></Box><Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1.2fr 1fr" }, gap: 2 }}><TextField required label="Expected date and time" type="datetime-local" value={form.expected_at} onChange={(event) => setForm({ ...form, expected_at: event.target.value })} InputLabelProps={{ shrink: true }} helperText="Shown to everyone in IST" /><TextField label="Vehicle number" value={form.vehicle_number} onChange={(event) => setForm({ ...form, vehicle_number: event.target.value.toUpperCase() })} placeholder="MH 12 AB 1234" helperText="Optional for visitors arriving by vehicle" InputProps={{ startAdornment: <InputAdornment position="start"><DirectionsCarRounded /></InputAdornment> }} /></Box><TextField label="Purpose or note for security" multiline minRows={2} value={form.purpose} onChange={(event) => setForm({ ...form, purpose: event.target.value })} placeholder="Briefly explain the visit" helperText="Do not include sensitive personal information." /></Stack>
            </FormSection>
          </Stack>
        </DialogContent>
        <DialogActions><Button onClick={() => setDialogOpen(false)} disabled={create.isPending}>Cancel</Button><Button type="submit" variant="contained" disabled={!formReady || create.isPending}>{create.isPending ? "Sending request…" : "Send for approval"}</Button></DialogActions>
      </Box>
    </Dialog>
  </Stack>;
}

function FormSection({ number, icon, title, subtitle, children }: { number: string; icon: React.ReactNode; title: string; subtitle: string; children: React.ReactNode }) {
  return <Stack spacing={2}><Stack direction="row" spacing={1.5} alignItems="flex-start"><Box sx={{ width: 38, height: 38, flexShrink: 0, borderRadius: 2, bgcolor: "primary.main", color: "primary.contrastText", display: "grid", placeItems: "center" }}>{icon}</Box><Box><Typography variant="h6"><Box component="span" color="text.disabled" sx={{ mr: 1 }}>{number}.</Box>{title}</Typography><Typography variant="body2" color="text.secondary">{subtitle}</Typography></Box></Stack><Box sx={{ pl: { md: 6.5 } }}>{children}</Box></Stack>;
}

function VisitorRow({ visitor, canApprove, canOperateGate, busy, onAction }: { visitor: Visitor; canApprove: boolean; canOperateGate: boolean; busy: boolean; onAction: (kind: string) => void }) {
  return <Stack direction={{ xs: "column", md: "row" }} alignItems={{ md: "center" }} spacing={2} sx={{ p: 2.25 }}><Box sx={{ width: 48, height: 48, borderRadius: 2, bgcolor: "action.hover", display: "grid", placeItems: "center", fontWeight: 900, fontSize: 18 }}>{visitor.name.slice(0, 1).toUpperCase()}</Box><Box sx={{ minWidth: 0, flex: 1 }}><Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap"><Typography fontWeight={850}>{visitor.name}</Typography><Chip size="small" label={visitor.status.replaceAll("_", " ")} color={statusTone[visitor.status] || "default"} /></Stack><Typography variant="body2" color="text.secondary">{visitor.wing_name && visitor.flat_number ? `Wing ${visitor.wing_name} · Flat ${visitor.flat_number}` : `Flat record ${visitor.flat_id}`} · {visitor.purpose || "Purpose not provided"}{visitor.vehicle_number ? ` · ${visitor.vehicle_number}` : ""}</Typography><Typography variant="caption" color="text.secondary">{visitor.expected_at ? `Expected ${formatSocietyDateTime(visitor.expected_at)} IST` : `Created ${formatSocietyDateTime(visitor.created_at)} IST`}{visitor.host_name ? ` · Requested by ${visitor.host_name}` : ""}</Typography></Box><Stack direction="row" spacing={1} flexWrap="wrap">{canApprove && visitor.status === "pending" && <><Button size="small" variant="contained" startIcon={<CheckRounded />} disabled={busy} onClick={() => onAction("approve")}>Approve</Button><IconButton color="error" aria-label={`Reject ${visitor.name}`} disabled={busy} onClick={() => onAction("reject")}><CloseRounded /></IconButton></>}{canOperateGate && visitor.status === "approved" && <Button size="small" variant="contained" startIcon={<LoginRounded />} disabled={busy} onClick={() => onAction("check_in")}>Check in</Button>}{canOperateGate && visitor.status === "checked_in" && <Button size="small" variant="outlined" startIcon={<LogoutRounded />} disabled={busy} onClick={() => onAction("check_out")}>Check out</Button>}</Stack></Stack>;
}

function GateMetric({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) { return <Paper sx={{ p: 2, borderTop: `4px solid ${color}` }}><Stack direction="row" justifyContent="space-between" alignItems="start"><Box><Typography variant="h4">{value}</Typography><Typography variant="body2" color="text.secondary">{label}</Typography></Box><Box sx={{ color }}>{icon}</Box></Stack></Paper>; }
function actionLabel(kind: string) { return ({ approve: "Visitor approved; security has been notified", reject: "Visitor request rejected", check_in: "Visitor checked in", check_out: "Visitor checked out" } as Record<string, string>)[kind] || "Gate record updated"; }
