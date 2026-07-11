import { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  TextField,
  Typography,
  Alert,
  Link,
  Divider,
  Avatar,
} from "@mui/material";
import { LockOutlined } from "@mui/icons-material";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { api } from "../api/client";
import { useAuthStore } from "../store/auth";
import type { LoginResponse } from "../types/api";

export default function Login() {
  const [email, setEmail] = useState("admin@greenpark.com");
  const [password, setPassword] = useState("Admin@12345");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<LoginResponse>("/auth/login", { email, password });
      setTokens(res.data.access_token, res.data.refresh_token);
      setUser(res.data.user);
      navigate("/", { replace: true });
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || err?.message || "Login failed. Check your credentials."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 440, width: "100%", borderRadius: 4 }}>
        <CardContent>
          <Stack spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Avatar sx={{ bgcolor: "primary.main", width: 56, height: 56 }}>
              <LockOutlined />
            </Avatar>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              Welcome to Smart Society
            </Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              Sign in to manage complaints, bills, visitors and notices.
            </Typography>
          </Stack>
          <form onSubmit={onSubmit}>
            <Stack spacing={2}>
              <TextField
                label="Email"
                type="email"
                fullWidth
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <TextField
                label="Password"
                type="password"
                fullWidth
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {error && <Alert severity="error">{error}</Alert>}
              <Button type="submit" variant="contained" size="large" disabled={loading}>
                {loading ? "Signing in…" : "Sign In"}
              </Button>
              <Divider />
              <Typography variant="body2" textAlign="center" color="text.secondary">
                Demo accounts seeded in <code>scripts/seed.py</code>:
                <br />
                <code>admin@greenpark.com / Admin@12345</code>
                <br />
                <code>resident@greenpark.com / Resident@123</code>
              </Typography>
              <Link component={RouterLink} to="/register" variant="body2" textAlign="center">
                Create a new account
              </Link>
            </Stack>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
