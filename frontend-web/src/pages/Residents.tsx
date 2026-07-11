import { Box, Grid, Paper, Stack, Typography, Chip } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { useAuthStore } from "../store/auth";
import { LoadingPanel } from "../components/StateViews";
import { KpiCard } from "../components/KpiCard";
import type { User } from "../types/api";

export default function Residents() {
  const me = useAuthStore((s) => s.user);
  const users = useQuery({
    queryKey: ["users"],
    queryFn: async () => (await api.get<User[]>("/admin/users?limit=100")).data,
    enabled: !!(me?.is_superuser || (me?.roles || []).some((r) => ["admin", "committee"].includes(r.name))),
  });

  if (users.isLoading) return <LoadingPanel />;

  return (
    <Box>
      <Typography variant="h4">Residents Directory</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Society members and their roles.
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={4}>
          <KpiCard title="Total users" value={users.data?.length ?? 0} color="#0F62FE" />
        </Grid>
        <Grid item xs={12} sm={4}>
          <KpiCard title="Admins" value={(users.data || []).filter((u) => u.roles.some((r) => r.name === "admin")).length} color="#7C4DFF" />
        </Grid>
        <Grid item xs={12} sm={4}>
          <KpiCard title="Residents" value={(users.data || []).filter((u) => u.roles.some((r) => r.name === "resident")).length} color="#00B894" />
        </Grid>

        <Grid item xs={12}>
          <Stack spacing={1}>
            {(users.data || []).map((u) => (
              <Paper key={u.id} sx={{ p: 2, borderRadius: 3 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {u.full_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {u.email} · {u.phone || "no phone"} · joined {new Date(u.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1}>
                    {u.roles.map((r) => (
                      <Chip key={r.id} label={r.name} size="small" color="primary" variant="outlined" />
                    ))}
                    {u.is_superuser && <Chip label="superuser" size="small" color="secondary" />}
                  </Stack>
                </Stack>
              </Paper>
            ))}
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
}
