import { useState } from "react";
import {
  Avatar,
  Box,
  Button,
  Chip,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  CampaignRounded,
  CloseRounded,
  DashboardRounded,
  DarkModeRounded,
  GroupsRounded,
  LightModeRounded,
  LogoutRounded,
  MenuRounded,
  PaymentsRounded,
  RecordVoiceOverRounded,
  ReportProblemRounded,
  SettingsRounded,
  ShieldRounded,
  SpaceDashboardRounded,
} from "@mui/icons-material";
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
const sharedStaff = [
  { to: "/visitors", label: "Gate", icon: <ShieldRounded /> },
  { to: "/residents", label: "People", icon: <GroupsRounded /> },
];

export default function AppLayout() {
  const theme = useTheme();
  const mobile = useMediaQuery(theme.breakpoints.down("md"));
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { mode, toggle } = useThemeStore();
  const { t } = useI18n();
  const [menuOpen, setMenuOpen] = useState(false);
  const roles = user?.roles?.map((role) => role.name) ?? [];
  const isAdmin = Boolean(user?.is_superuser || roles.includes("admin"));
  const isCommittee = roles.includes("committee");
  const managementItem = isAdmin
    ? { to: "/admin", label: "Admin", icon: <SettingsRounded /> }
    : isCommittee
      ? { to: "/committee", label: "Committee", icon: <SpaceDashboardRounded /> }
      : null;
  const items = isAdmin || isCommittee
    ? [...primary, ...sharedStaff, ...(managementItem ? [managementItem] : [])]
    : [...primary, sharedStaff[0]];
  const active = (to: string) => to === "/" ? pathname === "/" : pathname.startsWith(to);
  const go = (to: string) => {
    navigate(to);
    setMenuOpen(false);
  };
  const signOut = () => {
    logout();
    navigate("/login");
  };

  return <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}><CssBaseline />
    <Box component="header" sx={{ height: { xs: 64, md: 80 }, px: { xs: 1.5, sm: 2, md: 4 }, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 1, borderBottom: "1px solid", borderColor: "divider", bgcolor: "background.default", position: "sticky", top: 0, zIndex: 1200, overflow: "hidden" }}>
      <Stack direction="row" alignItems="center" spacing={{ xs: 1, md: 1.5 }} onClick={() => go("/")} sx={{ cursor: "pointer", minWidth: 0, flexShrink: 1 }}>
        <Box sx={{ width: { xs: 38, md: 44 }, height: { xs: 38, md: 44 }, flexShrink: 0, borderRadius: "50% 50% 46% 54%", bgcolor: "#173F35", color: "#F8F5EA", display: "grid", placeItems: "center", fontWeight: 900, fontSize: { xs: 16, md: 19 } }}>पं</Box>
        <Box sx={{ minWidth: 0 }}><Typography fontSize={{ xs: 16, md: 18 }} fontWeight={850} lineHeight={1} noWrap>Panchayat</Typography><Typography variant="caption" color="text.secondary" letterSpacing={1.1} noWrap>AI SEVA</Typography></Box>
      </Stack>
      {!mobile && <Stack direction="row" spacing={.5} sx={{ ml: 7, flex: 1 }}>{primary.map((item) => <Button key={item.to} onClick={() => go(item.to)} startIcon={item.icon} color="inherit" sx={{ px: 1.5, bgcolor: active(item.to) ? "#E8E2D1" : "transparent", color: active(item.to) ? "#173F35" : "text.secondary" }}>{t(item.label)}</Button>)}</Stack>}
      {mobile ? <Stack direction="row" alignItems="center" spacing={.25} sx={{ flexShrink: 0 }}>
        <NotificationInbox />
        {isAdmin && <AdminJoinInbox />}
        <IconButton aria-label={t("Open navigation menu")} aria-expanded={menuOpen} onClick={() => setMenuOpen(true)} sx={{ width: 44, height: 44, bgcolor: "action.hover" }}><MenuRounded /></IconButton>
      </Stack> : <Stack direction="row" alignItems="center" spacing={1}>
        <LanguageToggle /><Chip icon={<Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: "success.main" }} />} label={t("Connected")} variant="outlined" size="small" sx={{ display: { xs: "none", xl: "flex" } }} /><NotificationInbox />{isAdmin && <AdminJoinInbox />}<Tooltip title="Change theme"><IconButton onClick={toggle}>{mode === "dark" ? <LightModeRounded /> : <DarkModeRounded />}</IconButton></Tooltip><Avatar sx={{ width: 38, height: 38, bgcolor: "#D76049", fontWeight: 800 }}>{user?.full_name?.[0] ?? "U"}</Avatar><Box sx={{ display: { xs: "none", lg: "block" } }}><Typography variant="body2" fontWeight={800}>{user?.full_name}</Typography><Typography variant="caption" color="text.secondary">{isAdmin ? "admin" : isCommittee ? "committee" : roles[0] ?? "resident"}</Typography></Box><Tooltip title={t("Sign out")}><IconButton onClick={signOut}><LogoutRounded /></IconButton></Tooltip>
      </Stack>}
    </Box>
    <Box sx={{ display: "flex" }}>
      {!mobile && <Box component="aside" sx={{ width: 112, flexShrink: 0, minHeight: "calc(100vh - 80px)", borderRight: "1px solid", borderColor: "divider", py: 3, px: 1.5 }}><Stack spacing={1}>{items.filter((item) => !primary.some((entry) => entry.to === item.to)).map((item) => <Button key={item.to} onClick={() => go(item.to)} color="inherit" sx={{ minHeight: 76, borderRadius: 2, flexDirection: "column", gap: .5, fontSize: 11, bgcolor: active(item.to) ? "#173F35" : "transparent", color: active(item.to) ? "#fff" : "text.secondary", "& .MuiButton-startIcon": { m: 0 } }} startIcon={item.icon}>{t(item.label)}</Button>)}</Stack></Box>}
      <Box component="main" sx={{ flex: 1, minWidth: 0, p: { xs: 2, sm: 3, lg: 4 }, maxWidth: 1540, mx: "auto" }}><Outlet /></Box>
    </Box>
    <Drawer anchor="right" open={mobile && menuOpen} onClose={() => setMenuOpen(false)} PaperProps={{ sx: { width: "min(88vw, 360px)", p: 0, bgcolor: "background.paper", backgroundImage: "none" } }}>
      <Stack sx={{ minHeight: "100%" }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ p: 2 }}><Box><Typography variant="overline" color="primary" fontWeight={900}>PANCHAYAT AI</Typography><Typography variant="h5">{t("Menu")}</Typography></Box><IconButton aria-label={t("Close navigation menu")} onClick={() => setMenuOpen(false)}><CloseRounded /></IconButton></Stack>
        <Divider />
        <List component="nav" aria-label="Main navigation" sx={{ px: 1.5, py: 2 }}>{items.map((item) => <ListItemButton key={item.to} selected={active(item.to)} onClick={() => go(item.to)} sx={{ mb: .5, minHeight: 52, borderRadius: 2, "&.Mui-selected": { bgcolor: "primary.main", color: "primary.contrastText", "& .MuiListItemIcon-root": { color: "inherit" } } }}><ListItemIcon sx={{ minWidth: 42, color: "text.secondary" }}>{item.icon}</ListItemIcon><ListItemText primary={t(item.label)} primaryTypographyProps={{ fontWeight: active(item.to) ? 850 : 650 }} /></ListItemButton>)}</List>
        <Box sx={{ mt: "auto", p: 2, borderTop: 1, borderColor: "divider" }}>
          <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}><Avatar sx={{ bgcolor: "#D76049", fontWeight: 800 }}>{user?.full_name?.[0] ?? "U"}</Avatar><Box sx={{ minWidth: 0 }}><Typography fontWeight={850} noWrap>{user?.full_name}</Typography><Typography variant="caption" color="text.secondary">{isAdmin ? "Admin" : isCommittee ? "Committee" : t("Resident")}</Typography></Box></Stack>
          <Typography variant="caption" color="text.secondary" fontWeight={800}>{t("Language")}</Typography><Box sx={{ mt: .75, mb: 1.5 }}><LanguageToggle /></Box>
          <Stack direction="row" spacing={1}><Button fullWidth variant="outlined" color="inherit" startIcon={mode === "dark" ? <LightModeRounded /> : <DarkModeRounded />} onClick={toggle}>{t("Theme")}</Button><Button fullWidth variant="outlined" color="error" startIcon={<LogoutRounded />} onClick={signOut}>{t("Sign out")}</Button></Stack>
        </Box>
      </Stack>
    </Drawer>
  </Box>;
}
