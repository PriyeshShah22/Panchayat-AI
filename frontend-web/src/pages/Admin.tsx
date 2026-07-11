import { Box, Grid, Paper, Stack, Typography, Chip, Divider } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../api/client";
import { KpiCard } from "../components/KpiCard";
import { LoadingPanel } from "../components/StateViews";

interface AuditRow {
  id: number;
  actor_id: number | null;
  action: string;
  entity_type: string | null;
  entity_id: number | null;
  details: string | null;
  created_at: string;
}

export default function Admin() {
  const stats = useQuery({
    queryKey: ["admin-stats"],
    queryFn: async () => (await api.get("/admin/stats")).data,
  });
  const logs = useQuery({
    queryKey: ["audit-logs"],
    queryFn: async () => (await api.get("/admin/audit-logs?limit=20")).data,
  });

  if (stats.isLoading || logs.isLoading) return <LoadingPanel />;

  return (
    <Box>
      <Typography variant="h4">Admin Console</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Society-level metrics and audit trail.
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4}>
          <KpiCard title="Users total" value={stats.data?.users_total ?? 0} color="#0F62FE" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <KpiCard title="Active users" value={stats.data?.users_active ?? 0} color="#00B894" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <KpiCard title="Complaints total" value={stats.data?.complaints_total ?? 0} color="#E17055" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <KpiCard title="Complaints open" value={stats.data?.complaints_open ?? 0} color="#7C4DFF" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <KpiCard title="Overdue bills" value={stats.data?.bills_overdue ?? 0} color="#FDCB6E" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <KpiCard
            title="Outstanding ₹"
            value={(stats.data?.outstanding_amount ?? 0).toLocaleString("en-IN")}
            color="#0984E3"
          />
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Recent audit events</Typography>
            <Divider sx={{ mb: 1 }} />
            <Stack spacing={1}>
              {((logs.data as AuditRow[]) || []).map((row) => (
                <Stack key={row.id} direction="row" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {row.action}
                      {row.entity_type && (
                        <Chip size="small" label={`${row.entity_type}#${row.entity_id ?? "?"}`} sx={{ ml: 1 }} />
                      )}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      actor #{row.actor_id ?? "—"} · {dayjs(row.created_at).format("DD MMM HH:mm:ss")}
                    </Typography>
                  </Box>
                </Stack>
              ))}
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
