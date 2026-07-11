import {
  AppBar,
  Avatar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Tooltip,
  Typography,
  Divider,
  Stack,
  Chip,
} from "@mui/material";
import {
  Dashboard,
  ReportProblem,
  Receipt,
  PeopleAlt,
  Login,
  Campaign,
  SmartToy,
  AdminPanelSettings,
  Logout,
  Brightness4,
  Brightness7,
  Group,
} from "@mui/icons-material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { useThemeStore } from "../store/theme";

const NAV = [
  { to: "/", label: "Dashboard", icon: <Dashboard /> },
  { to: "/complaints", label: "Complaints", icon: <ReportProblem /> },
  { to: "/bills", label: "Maintenance & Bills", icon: <Receipt /> },
  { to: "/visitors", label: "Visitors", icon: <Login /> },
  { to: "/notices", label: "Notices", icon: <Campaign /> },
  { to: "/residents", label: "Residents", icon: <Group /> },
  { to: "/ai", label: "AI Assistant", icon: <SmartToy /> },
  { to: "/admin", label: "Admin", icon: <AdminPanelSettings /> },
];

const DRAWER_W = 260;

export default function AppLayout() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { user, logout } = useAuthStore();
  const { mode, toggle } = useThemeStore();
  const initials = (user?.full_name ?? "?")
    .split(/\s+/)
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const role = user?.roles?.map((r) => r.name).join(", ") ?? "";

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flex: 1, fontWeight: 700 }}>
            Smart Society Dashboard
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              label={role || "user"}
              size="small"
              sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "#fff" }}
            />
            <Tooltip title="Toggle theme">
              <IconButton color="inherit" onClick={toggle}>
                {mode === "dark" ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Tooltip>
            <Tooltip title="Sign out">
              <IconButton color="inherit" onClick={() => { logout(); navigate("/login"); }}>
                <Logout />
              </IconButton>
            </Tooltip>
            <Avatar sx={{ bgcolor: "secondary.main" }}>{initials}</Avatar>
          </Stack>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_W,
          flexShrink: 0,
          "& .MuiDrawer-paper": { width: DRAWER_W, boxSizing: "border-box" },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: "auto" }}>
          <List>
            {NAV.map((item) => {
              const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
              return (
                <ListItem disablePadding key={item.to}>
                  <ListItemButton
                    selected={active}
                    onClick={() => navigate(item.to)}
                    sx={{
                      "&.Mui-selected": {
                        bgcolor: (t) =>
                          t.palette.mode === "dark"
                            ? "rgba(130, 177, 255, 0.16)"
                            : "rgba(15, 98, 254, 0.12)",
                        borderRight: "3px solid #0F62FE",
                      },
                    }}
                  >
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
          <Divider />
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {user?.full_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user?.email}
            </Typography>
          </Box>
          <Box sx={{ p: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <PeopleAlt fontSize="small" />
              <Typography variant="caption">v1.0.0</Typography>
            </Stack>
          </Box>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Outlet />
      </Box>
    </Box>
  );
}
