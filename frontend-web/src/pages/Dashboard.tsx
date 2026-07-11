import { Box, Grid, Paper, Stack, Typography, Chip } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Line,
  LineChart,
} from "recharts";
import { api } from "../api/client";
import { KpiCard } from "../components/KpiCard";
import { useAuthStore } from "../store/auth";
import { LoadingPanel, ErrorPanel } from "../components/StateViews";
import type { AdminStats, Bill, Complaint } from "../types/api";
import {
  PeopleAlt,
  ReportProblem,
  ReceiptLong,
  Login,
} from "@mui/icons-material";

const TONES = ["#0F62FE", "#7C4DFF", "#00B894", "#E17055", "#FDCB6E", "#0984E3"];

export default function Dashboard() {
  const { user } = useAuthStore();
  const isPrivileged = (user?.roles || []).some((r) =>
    ["admin", "committee"].includes(r.name)
  );

  const stats = useQuery({
    queryKey: ["admin-stats"],
    queryFn: async () => (await api.get<AdminStats>("/admin/stats")).data,
    enabled: Boolean(isPrivileged || user?.is_superuser),
  });

  const complaints = useQuery({
    queryKey: ["complaints-all"],
    queryFn: async () => (await api.get<Complaint[]>("/complaints/?limit=200")).data,
  });

  const bills = useQuery({
    queryKey: ["bills-all"],
    queryFn: async () => (await api.get<Bill[]>("/bills/?limit=200")).data,
  });

  if (stats.isError) return <ErrorPanel message={(stats.error as any)?.message || "Failed"} />;
  if (stats.isLoading || complaints.isLoading || bills.isLoading) {
    return <LoadingPanel label="Loading dashboard…" />;
  }

  const byStatus = aggregate(complaints.data || [], (c) => c.status);
  const billsByStatus = aggregate(bills.data || [], (b) => b.status);
  const outstanding = (bills.data || []).reduce(
    (acc, b) => acc + Math.max(0, b.total_amount - b.paid_amount),
    0
  );
  const overdueCount = (bills.data || []).filter((b) => b.status === "overdue").length;

  // 7-day visitors trend (synthetic grouping by day bucket)
  const byDay = aggregateByDay(complaints.data || [], (c) => c.created_at);

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h4">Welcome, {user?.full_name?.split(" ")[0] || "User"}</Typography>
          <Typography variant="body2" color="text.secondary">
            Smart Society dashboard overview
          </Typography>
        </Box>
        <Chip
          label={`Logged in as ${(user?.roles || []).map((r) => r.name).join(", ") || "user"}`}
          color="primary"
          variant="outlined"
        />
      </Stack>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            title="Active users"
            value={stats.data?.users_active ?? "—"}
            icon={<PeopleAlt />}
            color="#0F62FE"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            title="Open complaints"
            value={stats.data?.complaints_open ?? "—"}
            icon={<ReportProblem />}
            color="#E17055"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            title="Bills overdue"
            value={overdueCount}
            icon={<ReceiptLong />}
            color="#FDCB6E"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            title="Outstanding (₹)"
            value={outstanding.toLocaleString("en-IN")}
            icon={<Login />}
            color="#7C4DFF"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Complaints by status</Typography>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={byStatus} dataKey="value" nameKey="name" outerRadius={100} label>
                  {byStatus.map((_, i) => (
                    <Cell key={i} fill={TONES[i % TONES.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Bills by status</Typography>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={billsByStatus}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#0F62FE" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Complaints over time</Typography>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={byDay}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#7C4DFF" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function aggregate<T>(arr: T[], keyFn: (t: T) => string): { name: string; value: number }[] {
  const map = new Map<string, number>();
  for (const v of arr) {
    const k = keyFn(v);
    map.set(k, (map.get(k) || 0) + 1);
  }
  return Array.from(map.entries()).map(([name, value]) => ({ name, value }));
}

function aggregateByDay<T>(arr: T[], dateFn: (t: T) => string): { name: string; value: number }[] {
  const map = new Map<string, number>();
  for (const v of arr) {
    const d = dateFn(v);
    if (!d) continue;
    const day = d.slice(0, 10);
    map.set(day, (map.get(day) || 0) + 1);
  }
  return Array.from(map.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .slice(-14)
    .map(([name, value]) => ({ name, value }));
}
