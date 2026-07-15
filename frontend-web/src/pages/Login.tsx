import { useState } from "react";
import { Alert, Box, Button, Chip, Divider, IconButton, InputAdornment, Link, Paper, Stack, TextField, Typography } from "@mui/material";
import { ArrowForwardRounded, MicRounded, PeopleRounded, TranslateRounded, VisibilityOffRounded, VisibilityRounded } from "@mui/icons-material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuthStore } from "../store/auth";
import type { LoginResponse } from "../types/api";

export default function Login() {
  const [email, setEmail] = useState("resident@greenpark.com");
  const [password, setPassword] = useState("Resident@123");
  const [show, setShow] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setLoading(true); setError(null);
    try {
      const { data } = await api.post<LoginResponse>("/auth/login", { email, password });
      setTokens(data.access_token, data.refresh_token); setUser(data.user); navigate("/", { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail || "The server could not be reached. Start the app and try again.");
    } finally { setLoading(false); }
  }

  return <Box sx={{ minHeight: "100vh", display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1.1fr .9fr" }, bgcolor: "#F8F5EA" }}>
    <Box sx={{ display: { xs: "none", lg: "flex" }, p: 7, bgcolor: "#173F35", color: "#FFFDF6", flexDirection: "column", position: "relative", overflow: "hidden" }}>
      <Box sx={{ position: "absolute", width: 620, height: 620, borderRadius: "50%", border: "1px solid rgba(255,255,255,.1)", right: -240, bottom: -260 }} />
      <Stack direction="row" alignItems="center" spacing={1.5}><BrandMark light /><Box><Typography variant="h6">Panchayat AI</Typography><Typography variant="caption" sx={{ opacity: .65 }}>DIGITAL COMMUNITY SEVA</Typography></Box></Stack>
      <Box sx={{ my: "auto", maxWidth: 650, position: "relative" }}><Chip label="Made for every resident" sx={{ bgcolor: "rgba(255,255,255,.12)", color: "#FFFDF6", mb: 3 }} /><Typography variant="h1" sx={{ fontSize: "clamp(4rem,7vw,7.4rem)" }}>बस बोलिए।<br /><Box component="span" sx={{ color: "#F4B860" }}>काम हो जाएगा.</Box></Typography><Typography variant="h5" sx={{ mt: 4, maxWidth: 560, opacity: .78, fontWeight: 500 }}>Speak naturally. Understand official information. Complete community tasks without learning complicated technology.</Typography><Stack direction="row" spacing={4} sx={{ mt: 6 }}><Feature icon={<MicRounded />} label="Voice first" /><Feature icon={<TranslateRounded />} label="4 languages" /><Feature icon={<PeopleRounded />} label="Human fallback" /></Stack></Box>
      <Typography variant="caption" sx={{ opacity: .55 }}>Your data stays protected by the same permissions used by every manual service.</Typography>
    </Box>
    <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", p: { xs: 2, sm: 5 }, color: "#1E2A26", "& .MuiTypography-colorTextSecondary": { color: "#56645D" } }}>
      <Box sx={{ width: "100%", maxWidth: 500 }}>
        <Stack direction="row" alignItems="center" spacing={1.5} sx={{ display: { lg: "none" }, mb: 5 }}><BrandMark /><Typography variant="h6" sx={{ color: "#1E2A26" }}>Panchayat AI</Typography></Stack>
        <Typography variant="overline" sx={{ color: "#176B52" }} fontWeight={900} letterSpacing={2}>WELCOME BACK</Typography>
        <Typography variant="h3" sx={{ mt: 1, color: "#1E2A26" }}>Enter your community</Typography>
        <Typography sx={{ mt: 1, color: "#56645D" }}>Use your approved society account to sign in.</Typography>
        <Paper component="form" onSubmit={submit} sx={{ mt: 4, p: { xs: 2.5, sm: 4 }, bgcolor: "#FFFDF7", color: "#1E2A26", "& .MuiInputLabel-root": { color: "#4C5B54" }, "& .MuiFormHelperText-root": { color: "#66746D" }, "& .MuiOutlinedInput-input": { color: "#1E2A26" }, "& .MuiOutlinedInput-notchedOutline": { borderColor: "#627069" }, "& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#173F35" }, "& .MuiSvgIcon-root": { color: "#33453D" } }}>
          <Stack spacing={2.5}>
            <TextField label="Email or registered ID" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} helperText="Your registered mobile login will be supported when OTP is configured." />
            <TextField label="Password" type={show ? "text" : "password"} required value={password} onChange={(e) => setPassword(e.target.value)} InputProps={{ endAdornment: <InputAdornment position="end"><IconButton aria-label={show ? "Hide password" : "Show password"} onClick={() => setShow(!show)}>{show ? <VisibilityOffRounded /> : <VisibilityRounded />}</IconButton></InputAdornment> }} />
            {error && <Alert severity="error">{error}</Alert>}
            <Button type="submit" variant="contained" size="large" endIcon={<ArrowForwardRounded />} disabled={loading} sx={{ bgcolor: "#176B52", color: "#FFFDF6", "&:hover": { bgcolor: "#124C3B" } }}>{loading ? "Signing in…" : "Continue"}</Button>
            <Divider sx={{ borderColor: "#CFC8B6" }}><Typography variant="caption" sx={{ color: "#66746D" }}>NEW TO PANCHAYAT AI?</Typography></Divider>
            <Link component={RouterLink} to="/register" textAlign="center" fontWeight={800} sx={{ color: "#176B52" }}>Request to join</Link>
          </Stack>
        </Paper>
        <Typography variant="caption" display="block" sx={{ mt: 2, color: "#66746D" }}>Development login: resident@greenpark.com / Resident@123</Typography>
      </Box>
    </Box>
  </Box>;
}

function BrandMark({ light = false }: { light?: boolean }) { return <Box sx={{ width: 48, height: 48, borderRadius: "50%", bgcolor: light ? "#F4B860" : "#173F35", color: light ? "#33240E" : "#FFFDF6", display: "grid", placeItems: "center", fontWeight: 900 }}>पं</Box>; }
function Feature({ icon, label }: { icon: React.ReactNode; label: string }) { return <Stack spacing={1}><Box sx={{ width: 52, height: 52, borderRadius: "50%", border: "1px solid rgba(255,255,255,.25)", display: "grid", placeItems: "center" }}>{icon}</Box><Typography variant="body2" fontWeight={750}>{label}</Typography></Stack>; }
