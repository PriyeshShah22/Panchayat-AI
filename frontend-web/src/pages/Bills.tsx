import { useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import {
  AccountBalanceWalletRounded,
  AddRounded,
  CalendarMonthRounded,
  CheckCircleRounded,
  DownloadRounded,
  HistoryRounded,
  PaymentsRounded,
  ReceiptLongRounded,
  WarningAmberRounded,
} from "@mui/icons-material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import { enqueueSnackbar } from "notistack";
import { api } from "../api/client";
import { useAuthStore } from "../store/auth";
import { useI18n } from "../store/language";
import type { Bill } from "../types/api";

export default function Bills() {
  const me = useAuthStore((state) => state.user);
  const roles = me?.roles.map((role) => role.name) ?? [];
  const manager = Boolean(
    me?.is_superuser ||
      roles.some((role) => ["admin", "committee"].includes(role)),
  );
  const admin = Boolean(me?.is_superuser || roles.includes("admin"));
  const { t } = useI18n();
  const qc = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [payOpen, setPayOpen] = useState(false);
  const bills = useQuery({
    queryKey: ["bills"],
    queryFn: async () => (await api.get<Bill[]>("/bills/?limit=200")).data,
  });
  const config = useQuery({
    queryKey: ["payment-config"],
    queryFn: async () => (await api.get("/bills/payment-config")).data,
  });
  const rows = bills.data ?? [];
  const unpaid = rows.filter(
    (bill) => !["paid", "cancelled"].includes(bill.status),
  );
  const outstanding = unpaid.reduce(
    (sum, bill) => sum + Math.max(0, bill.total_amount - bill.paid_amount),
    0,
  );
  const refresh = async () => {
    await qc.invalidateQueries({ queryKey: ["bills"] });
    await qc.invalidateQueries({ queryKey: ["dues-summary"] });
    await qc.invalidateQueries({ queryKey: ["admin-stats"] });
  };
  const byResident = useMemo(() => {
    const groups = new Map<number, Bill[]>();
    rows.forEach((bill) => {
      const key = bill.billed_user_id ?? 0;
      groups.set(key, [...(groups.get(key) ?? []), bill]);
    });
    return [...groups.values()];
  }, [rows]);
  const existingPeriods = useMemo(
    () =>
      new Set(rows.map((bill) => `${bill.billing_year}-${bill.billing_month}`)),
    [rows],
  );
  return (
    <Stack spacing={3}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ md: "end" }}
        spacing={2}
      >
        <Box>
          <Typography variant="overline" color="primary" fontWeight={900}>
            MAINTENANCE
          </Typography>
          <Typography
            variant="h2"
            sx={{ fontSize: { xs: "2.5rem", md: "3.8rem" } }}
          >
            {manager ? t("Monthly billing") : t("Your society dues")}
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            {manager
              ? "Set one maintenance amount once and bill every verified resident automatically."
              : "Older unpaid months are combined so you can clear everything in one payment."}
          </Typography>
        </Box>
        {admin && (
          <Button
            variant="contained"
            size="large"
            startIcon={<AddRounded />}
            onClick={() => setCreateOpen(true)}
          >
            {t("Create monthly maintenance")}
          </Button>
        )}
      </Stack>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", sm: "repeat(3,1fr)" },
          gap: 1.5,
        }}
      >
        <Metric
          icon={<AccountBalanceWalletRounded />}
          label={manager ? "Society outstanding" : "Total to pay"}
          value={`₹${outstanding.toLocaleString("en-IN")}`}
          tone="#D76049"
        />
        <Metric
          icon={<CalendarMonthRounded />}
          label={manager ? "Unpaid resident bills" : "Unpaid months"}
          value={String(unpaid.length)}
          tone="#C67A20"
        />
        <Metric
          icon={<CheckCircleRounded />}
          label="Paid bills"
          value={String(rows.filter((bill) => bill.status === "paid").length)}
          tone="#2B805F"
        />
      </Box>
      {bills.isLoading && <LinearProgress />}
      {bills.isError && (
        <Alert severity="error">Maintenance records could not be loaded.</Alert>
      )}
      {!manager && rows.length > 0 && (
        <ResidentDues
          rows={rows}
          outstanding={outstanding}
          demo={Boolean(config.data?.demo_enabled)}
          razorpay={Boolean(config.data?.razorpay_enabled)}
          payOpen={payOpen}
          setPayOpen={setPayOpen}
          onPaid={refresh}
        />
      )}
      {manager && (
        <Stack spacing={1.5}>
          <Typography variant="h5">Resident collection status</Typography>
          {byResident.map((residentBills) => {
            const due = residentBills.reduce(
              (sum, bill) =>
                sum + Math.max(0, bill.total_amount - bill.paid_amount),
              0,
            );
            const user = residentBills[0].billed_user;
            return (
              <Paper key={residentBills[0].billed_user_id} sx={{ p: 2.5 }}>
                <Stack
                  direction={{ xs: "column", md: "row" }}
                  justifyContent="space-between"
                  alignItems={{ md: "center" }}
                  spacing={2}
                >
                  <Box>
                    <Typography fontWeight={900}>
                      {user?.full_name || "Resident"}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {residentBills.length} monthly bills ·{" "}
                      {
                        residentBills.filter((bill) => bill.status === "paid")
                          .length
                      }{" "}
                      paid
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip
                      label={
                        due
                          ? `${residentBills.filter((bill) => bill.status !== "paid").length} due`
                          : "Clear"
                      }
                      color={due ? "warning" : "success"}
                    />
                    <Typography variant="h6">
                      ₹{due.toLocaleString("en-IN")}
                    </Typography>
                  </Stack>
                </Stack>
              </Paper>
            );
          })}
          {byResident.length === 0 && <Empty />}
        </Stack>
      )}
      {!manager && rows.length === 0 && <Empty />}
      <CreateMonthlyDialog
        open={createOpen}
        existingPeriods={existingPeriods}
        onClose={() => setCreateOpen(false)}
        onCreated={async () => {
          setCreateOpen(false);
          await refresh();
        }}
      />
    </Stack>
  );
}

function ResidentDues({
  rows,
  outstanding,
  demo,
  razorpay,
  payOpen,
  setPayOpen,
  onPaid,
}: {
  rows: Bill[];
  outstanding: number;
  demo: boolean;
  razorpay: boolean;
  payOpen: boolean;
  setPayOpen: (open: boolean) => void;
  onPaid: () => Promise<void>;
}) {
  const unpaid = rows.filter(
    (bill) => !["paid", "cancelled"].includes(bill.status),
  );
  const pay = useMutation({
    mutationFn: async () => {
      if (demo) return (await api.post("/bills/payments/demo")).data;
      const { data: order } = await api.post("/bills/payment-order");
      await loadRazorpay();
      return new Promise((resolve, reject) => {
        const checkout = new (window as any).Razorpay({
          key: order.key_id,
          amount: order.amount_paise,
          currency: "INR",
          name: "Panchayat",
          description: "Combined maintenance dues",
          order_id: order.order_id,
          prefill: { name: order.resident_name },
          theme: { color: "#173F35" },
          handler: async (response: any) => {
            try {
              resolve(
                (await api.post("/bills/payments/verify", response)).data,
              );
            } catch (error) {
              reject(error);
            }
          },
          modal: { ondismiss: () => reject(new Error("Payment cancelled")) },
        });
        checkout.open();
      });
    },
    onSuccess: async (result: any) => {
      setPayOpen(false);
      enqueueSnackbar(
        result?.demo
          ? "Demo payment completed. No real money was transferred."
          : "Payment received and awaiting bank confirmation.",
        { variant: "success" },
      );
      await onPaid();
    },
    onError: (error: any) =>
      enqueueSnackbar(
        error?.response?.data?.detail ||
          error?.message ||
          "Payment could not be completed",
        { variant: "error" },
      ),
  });
  return (
    <>
      <Paper
        sx={{
          overflow: "hidden",
          border: 0,
          boxShadow: "0 18px 55px rgba(23,63,53,.12)",
        }}
      >
        <Box sx={{ p: { xs: 3, md: 5 }, bgcolor: "#173F35", color: "white" }}>
          <Typography variant="overline" sx={{ opacity: 0.7 }}>
            COMBINED OUTSTANDING
          </Typography>
          <Stack
            direction={{ xs: "column", md: "row" }}
            justifyContent="space-between"
            alignItems={{ md: "end" }}
            spacing={2}
          >
            <Box>
              <Typography variant="h3">
                ₹{outstanding.toLocaleString("en-IN")}
              </Typography>
              <Typography sx={{ opacity: 0.75 }}>
                {unpaid.length
                  ? `${unpaid.length} unpaid month${unpaid.length > 1 ? "s" : ""} included`
                  : "Nothing is due"}
              </Typography>
            </Box>
            {outstanding > 0 && (
              <Button
                size="large"
                variant="contained"
                color="secondary"
                startIcon={<PaymentsRounded />}
                onClick={() => setPayOpen(true)}
              >
                {demo ? "Pay with demo checkout" : "Pay all securely"}
              </Button>
            )}
          </Stack>
        </Box>
        <Box sx={{ p: { xs: 2.5, md: 4 } }}>
          <Typography variant="h6">Months included</Typography>
          <Stack divider={<Divider />} sx={{ mt: 1.5 }}>
            {unpaid.map((bill) => (
              <Stack
                key={bill.id}
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                sx={{ py: 1.5 }}
              >
                <Box>
                  <Typography fontWeight={850}>
                    {dayjs(
                      `${bill.billing_year}-${bill.billing_month}-01`,
                    ).format("MMMM YYYY")}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Due {dayjs(bill.due_date).format("DD MMM YYYY")} ·{" "}
                    {bill.bill_number}
                  </Typography>
                </Box>
                <Typography fontWeight={900}>
                  ₹
                  {Math.max(
                    0,
                    bill.total_amount - bill.paid_amount,
                  ).toLocaleString("en-IN")}
                </Typography>
              </Stack>
            ))}
          </Stack>
          {unpaid.length === 0 && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Your maintenance account is fully paid.
            </Alert>
          )}
        </Box>
      </Paper>
      <Box>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
          <HistoryRounded color="primary" />
          <Typography variant="h5">Payment history</Typography>
        </Stack>
        <Stack spacing={1}>
          {rows
            .filter((bill) => bill.status === "paid")
            .map((bill) => (
              <Paper key={bill.id} sx={{ p: 2 }}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Box>
                    <Typography fontWeight={800}>{bill.title}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Paid · {bill.bill_number}
                    </Typography>
                  </Box>
                  <Download bill={bill} />
                </Stack>
              </Paper>
            ))}
        </Stack>
      </Box>
      <Dialog
        open={payOpen}
        onClose={() => setPayOpen(false)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>{demo ? "Demo payment" : "Confirm payment"}</DialogTitle>
        <DialogContent>
          {demo && (
            <Alert severity="warning" icon={<WarningAmberRounded />}>
              Demo mode only. No bank, UPI account, or real money is involved.
            </Alert>
          )}
          <Typography variant="h3" sx={{ mt: 2 }}>
            ₹{outstanding.toLocaleString("en-IN")}
          </Typography>
          <Typography color="text.secondary">
            This clears all {unpaid.length} outstanding maintenance month
            {unpaid.length > 1 ? "s" : ""}.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPayOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={pay.isPending}
            onClick={() => pay.mutate()}
          >
            {demo ? "Complete demo payment" : "Continue to UPI"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

function CreateMonthlyDialog({
  open,
  onClose,
  onCreated,
  existingPeriods,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => Promise<void>;
  existingPeriods: Set<string>;
}) {
  const now = dayjs();
  const [form, setForm] = useState({
    billing_year: now.year(),
    billing_month: now.month() + 1,
    maintenance_amount: 2500,
    due_date: now.add(15, "day").format("YYYY-MM-DD"),
  });
  const create = useMutation({
    mutationFn: async () => (await api.post("/bills/monthly", form)).data,
    onSuccess: async (data) => {
      enqueueSnackbar(
        `${data.created} residents billed for ${dayjs()
          .month(data.billing_month - 1)
          .format("MMMM")} ${data.billing_year}.`,
        { variant: "success" },
      );
      await onCreated();
    },
    onError: (error: any) =>
      enqueueSnackbar(
        error?.response?.data?.detail || "Monthly billing failed",
        { variant: "error" },
      ),
  });
  const duplicate = existingPeriods.has(
    `${form.billing_year}-${form.billing_month}`,
  );
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Create maintenance for everyone</DialogTitle>
      <DialogContent>
        <Alert severity={duplicate ? "error" : "info"} sx={{ mb: 2 }}>
          {duplicate
            ? "This month has already been billed. Choose another month."
            : "One amount is sent to every approved resident with a linked flat. A month can only be billed once."}
        </Alert>
        <Stack spacing={2}>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField
              fullWidth
              type="number"
              label="Year"
              value={form.billing_year}
              onChange={(e) =>
                setForm({ ...form, billing_year: Number(e.target.value) })
              }
            />
            <TextField
              fullWidth
              select
              label="Month"
              value={form.billing_month}
              onChange={(e) =>
                setForm({ ...form, billing_month: Number(e.target.value) })
              }
            >
              {Array.from({ length: 12 }, (_, index) => (
                <MenuItem key={index + 1} value={index + 1}>
                  {dayjs().month(index).format("MMMM")}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
          <TextField
            type="number"
            label="Maintenance amount per resident"
            value={form.maintenance_amount}
            onChange={(e) =>
              setForm({ ...form, maintenance_amount: Number(e.target.value) })
            }
          />
          <TextField
            type="date"
            label="Due date"
            InputLabelProps={{ shrink: true }}
            value={form.due_date}
            onChange={(e) => setForm({ ...form, due_date: e.target.value })}
          />
        </Stack>
      </DialogContent>
      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          disabled={
            duplicate || form.maintenance_amount <= 0 || create.isPending
          }
          onClick={() => create.mutate()}
        >
          Bill every resident
        </Button>
      </DialogActions>
    </Dialog>
  );
}
function Metric({
  icon,
  label,
  value,
  tone,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <Paper sx={{ p: 2.5, borderTop: `4px solid ${tone}` }}>
      <Stack direction="row" justifyContent="space-between">
        <Box>
          <Typography variant="caption" color="text.secondary">
            {label}
          </Typography>
          <Typography variant="h4">{value}</Typography>
        </Box>
        <Box sx={{ color: tone }}>{icon}</Box>
      </Stack>
    </Paper>
  );
}
function Empty() {
  return (
    <Paper sx={{ p: 7, textAlign: "center" }}>
      <ReceiptLongRounded sx={{ fontSize: 58, color: "text.disabled" }} />
      <Typography variant="h5">No maintenance records yet</Typography>
      <Typography color="text.secondary">
        The monthly maintenance charge will appear here after an administrator
        publishes it.
      </Typography>
    </Paper>
  );
}
function Download({ bill }: { bill: Bill }) {
  const [downloading, setDownloading] = useState(false);
  return (
    <Button
      variant="outlined"
      color="inherit"
      startIcon={<DownloadRounded />}
      disabled={downloading}
      onClick={async () => {
        setDownloading(true);
        try {
          const response = await api.get(`/bills/${bill.id}/pdf`, { responseType: "blob" });
          const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
          const link = document.createElement("a");
          link.href = url;
          link.download = `${bill.bill_number}.pdf`;
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (error: any) {
          enqueueSnackbar(error?.response?.data?.detail || "Receipt could not be downloaded", { variant: "error" });
        } finally {
          setDownloading(false);
        }
      }}
    >
      {downloading ? "Preparing…" : "Receipt"}
    </Button>
  );
}
async function loadRazorpay() {
  if ((window as any).Razorpay) return;
  await new Promise<void>((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve();
    script.onerror = () =>
      reject(new Error("Razorpay checkout could not load"));
    document.body.appendChild(script);
  });
}
