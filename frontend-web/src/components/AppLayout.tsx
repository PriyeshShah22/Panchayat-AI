import { Avatar, Box, Button, Chip, CssBaseline, IconButton, Stack, Tooltip, Typography, useMediaQuery, useTheme } from "@mui/material";
import { CampaignRounded, DashboardRounded, DarkModeRounded, GroupsRounded, LightModeRounded, LogoutRounded, PaymentsRounded, RecordVoiceOverRounded, ReportProblemRounded, SettingsRounded, ShieldRounded } from "@mui/icons-material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { useThemeStore } from "../store/theme";
import AdminJoinInbox from "./AdminJoinInbox";
import { LanguageToggle } from "./LanguageToggle";
import { useI18n } from "../store/language";
import NotificationInbox from "./NotificationInbox";

const primary = [
  { to: "/", label: "Home", icon: <DashboardRounded /> },
  { to: "/ai", label: "Assistant", icon: <RecordVoiceOverRounded /> },
  { to: "/complaints", label: "Help", icon: <ReportProblemRounded /> },
  { to: "/bills", label: "Dues", icon: <PaymentsRounded /> },
  { to: "/notices", label: "Notices", icon: <CampaignRounded /> },
];
const staff = [
  { to: "/visitors", label: "Gate", icon: <ShieldRounded /> },
  { to: "/residents", label: "People", icon: <GroupsRounded /> },
  { to: "/admin", label: "Admin", icon: <SettingsRounded /> },
];

export default function AppLayout() {
  const theme = useTheme(); const mobile = useMediaQuery(theme.breakpoints.down("md"));
  const { pathname } = useLocation(); const navigate = useNavigate();
  const { user, logout } = useAuthStore(); const { mode, toggle } = useThemeStore();
  const { t } = useI18n();
  const roles = user?.roles?.map((r) => r.name) ?? [];
  const canManageSociety = Boolean(user?.is_superuser || roles.some((r) => ["admin", "committee"].includes(r)));
  const items = canManageSociety ? [...primary, ...staff] : [...primary, staff[0]];
  const active = (to: string) => to === "/" ? pathname === "/" : pathname.startsWith(to);
  return <Box sx={{ minHeight: "100vh", bgcolor: "background.default", pb: { xs: 10, md: 0 } }}><CssBaseline />
    <Box component="header" sx={{ height: 80, px: { xs: 2, md: 4 }, display: "flex", alignItems: "center", borderBottom: "1px solid", borderColor: "divider", bgcolor: "background.default", position: "sticky", top: 0, zIndex: 1200 }}>
      <Stack direction="row" alignItems="center" spacing={1.5} onClick={() => navigate("/")} sx={{ cursor: "pointer" }}><Box sx={{ width: 44, height: 44, borderRadius: "50% 50% 46% 54%", bgcolor: "#173F35", color: "#F8F5EA", display: "grid", placeItems: "center", fontWeight: 900, fontSize: 19 }}>पं</Box><Box><Typography fontSize={18} fontWeight={850} lineHeight={1}>Panchayat</Typography><Typography variant="caption" color="text.secondary" letterSpacing={1.2}>AI SEVA</Typography></Box></Stack>
      {!mobile && <Stack direction="row" spacing={.5} sx={{ ml: 7, flex: 1 }}>{primary.map((item) => <Button key={item.to} onClick={() => navigate(item.to)} startIcon={item.icon} color="inherit" sx={{ px: 1.5, bgcolor: active(item.to) ? "#E8E2D1" : "transparent", color: active(item.to) ? "#173F35" : "text.secondary" }}>{t(item.label)}</Button>)}</Stack>}
      <Stack direction="row" alignItems="center" spacing={1}><LanguageToggle /><Chip icon={<Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: "success.main" }} />} label={t("Connected")} variant="outlined" size="small" sx={{ display: { xs: "none", xl: "flex" } }} /><NotificationInbox />{(user?.is_superuser || roles.includes("admin")) && <AdminJoinInbox />}<Tooltip title="Change theme"><IconButton onClick={toggle}>{mode === "dark" ? <LightModeRounded /> : <DarkModeRounded />}</IconButton></Tooltip><Avatar sx={{ width: 38, height: 38, bgcolor: "#D76049", fontWeight: 800 }}>{user?.full_name?.[0] ?? "U"}</Avatar><Box sx={{ display: { xs: "none", lg: "block" } }}><Typography variant="body2" fontWeight={800}>{user?.full_name}</Typography><Typography variant="caption" color="text.secondary">{roles[0] ?? "resident"}</Typography></Box><Tooltip title={t("Sign out")}><IconButton onClick={() => { logout(); navigate("/login"); }}><LogoutRounded /></IconButton></Tooltip></Stack>
    </Box>
    <Box sx={{ display: "flex" }}>
      {!mobile && <Box component="aside" sx={{ width: 112, flexShrink: 0, minHeight: "calc(100vh - 80px)", borderRight: "1px solid", borderColor: "divider", py: 3, px: 1.5 }}><Stack spacing={1}>{items.filter((i) => !primary.some((p) => p.to === i.to)).map((item) => <Button key={item.to} onClick={() => navigate(item.to)} color="inherit" sx={{ minHeight: 76, borderRadius: 2, flexDirection: "column", gap: .5, fontSize: 11, bgcolor: active(item.to) ? "#173F35" : "transparent", color: active(item.to) ? "#fff" : "text.secondary", "& .MuiButton-startIcon": { m: 0 } }} startIcon={item.icon}>{t(item.label)}</Button>)}</Stack></Box>}
      <Box component="main" sx={{ flex: 1, minWidth: 0, p: { xs: 2, sm: 3, lg: 4 }, maxWidth: 1540, mx: "auto" }}><Outlet /></Box>
    </Box>
    {mobile && <Box component="nav" aria-label="Mobile navigation" sx={{ position: "fixed", left: 10, right: 10, bottom: 10, zIndex: 1300, bgcolor: "#173F35", color: "white", borderRadius: 3, p: .75, boxShadow: "0 18px 50px rgba(23,63,53,.3)", display: "grid", gridTemplateColumns: "repeat(5,1fr)" }}>{primary.map((item) => <IconButton key={item.to} aria-label={t(item.label)} onClick={() => navigate(item.to)} sx={{ color: active(item.to) ? "#F4B860" : "rgba(255,255,255,.65)", flexDirection: "column", borderRadius: 2, fontSize: 10, gap: .2 }}>{item.icon}<span>{t(item.label)}</span></IconButton>)}</Box>}
  </Box>;
}
